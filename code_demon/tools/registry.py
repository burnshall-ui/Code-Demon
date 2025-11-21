"""
Tool Registry & Execution Engine

Central registry for all tools and their execution
"""

import asyncio
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from enum import Enum
from difflib import SequenceMatcher


class ToolCategory(str, Enum):
    """Tool categories"""

    FILES = "files"
    CODE = "code"
    GIT = "git"
    EXECUTION = "execution"
    WEB = "web"
    SYSTEM = "system"


@dataclass
class ToolParameter:
    """Parameter definition for a tool"""

    name: str
    type: str  # "string", "number", "boolean", "array", "object"
    description: str
    required: bool = True
    default: Any = None
    enum: Optional[List[Any]] = None


@dataclass
class ToolMetadata:
    """Metadata about a tool"""

    name: str
    description: str
    category: ToolCategory
    parameters: List[ToolParameter]
    requires_approval: bool = False
    dangerous: bool = False
    timeout: int = 30  # seconds


class Tool(ABC):
    """Abstract base class for tools"""

    def __init__(self):
        self.metadata = self._define_metadata()

    @abstractmethod
    def _define_metadata(self) -> ToolMetadata:
        """Define tool metadata"""
        pass

    @abstractmethod
    async def execute(self, **kwargs: Any) -> str:
        """
        Execute the tool

        Args:
            **kwargs: Tool parameters

        Returns:
            Result as a string

        Raises:
            ToolExecutionError: If execution fails
        """
        pass

    def to_json_schema(self) -> Dict[str, Any]:
        """Convert tool to JSON Schema format for LLM"""
        properties: Dict[str, Any] = {}
        required = []

        for param in self.metadata.parameters:
            param_schema: Dict[str, Any] = {
                "type": param.type,
                "description": param.description,
            }

            if param.enum:
                param_schema["enum"] = param.enum

            if param.default is not None:
                param_schema["default"] = param.default

            properties[param.name] = param_schema

            if param.required:
                required.append(param.name)

        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }


class ToolRegistry:
    """Central registry for all tools"""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._approval_handler: Optional[Callable[[str, str], bool]] = None

    def register(self, tool: Tool) -> None:
        """Register a tool"""
        self._tools[tool.metadata.name] = tool

    def unregister(self, name: str) -> None:
        """Unregister a tool"""
        if name in self._tools:
            del self._tools[name]

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
        """List all registered tool names"""
        return list(self._tools.keys())

    def list_tools_by_category(self, category: ToolCategory) -> List[str]:
        """List tools in a specific category"""
        return [
            name
            for name, tool in self._tools.items()
            if tool.metadata.category == category
        ]

    def get_tools_for_llm(self) -> List[Dict[str, Any]]:
        """Get all tools in LLM-compatible format"""
        tools = []
        for tool in self._tools.values():
            tools.append(
                {
                    "name": tool.metadata.name,
                    "description": tool.metadata.description,
                    "parameters": tool.to_json_schema(),
                }
            )
        return tools

    def set_approval_handler(self, handler: Callable[[str, str], bool]) -> None:
        """Set the approval handler for dangerous operations"""
        self._approval_handler = handler

    def _find_similar_tools(self, tool_name: str, max_suggestions: int = 3) -> List[str]:
        """
        Find similar tool names using fuzzy string matching

        Args:
            tool_name: The tool name that wasn't found
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of similar tool names, sorted by similarity
        """
        similarities = []

        for available_tool in self._tools.keys():
            # Calculate similarity ratio
            ratio = SequenceMatcher(None, tool_name.lower(), available_tool.lower()).ratio()

            # Also check if the query is a substring or vice versa
            if tool_name.lower() in available_tool.lower() or available_tool.lower() in tool_name.lower():
                ratio += 0.3  # Boost substring matches

            similarities.append((available_tool, ratio))

        # Sort by similarity score (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Return top matches with similarity > 0.4
        suggestions = [name for name, score in similarities[:max_suggestions] if score > 0.4]
        return suggestions

    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """
        Execute a tool with given arguments

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Execution result

        Raises:
            ToolNotFoundError: If tool doesn't exist
            ToolExecutionError: If execution fails
            ToolApprovalDenied: If approval is required and denied
        """
        tool = self.get_tool(name)
        if not tool:
            # Find similar tools and provide helpful suggestions
            suggestions = self._find_similar_tools(name)

            error_msg = f"Tool '{name}' does not exist."

            if suggestions:
                error_msg += f"\n\nDid you mean one of these?\n"
                for suggestion in suggestions:
                    tool_obj = self._tools.get(suggestion)
                    if tool_obj:
                        error_msg += f"  • {suggestion} - {tool_obj.metadata.description}\n"
                error_msg += "\nIMPORTANT: Only use tools that actually exist. Do not invent tool names."
            else:
                # No suggestions - list available tools in the relevant category
                error_msg += f"\n\nNo similar tools found. Available tools:\n"
                categories = {}
                for tool_name, tool_obj in self._tools.items():
                    cat = tool_obj.metadata.category.value
                    if cat not in categories:
                        categories[cat] = []
                    categories[cat].append(tool_name)

                for category, tools in sorted(categories.items()):
                    error_msg += f"\n{category}: {', '.join(tools)}"

            raise ToolNotFoundError(error_msg)

        # Check if approval is required
        if tool.metadata.requires_approval:
            if self._approval_handler:
                reason = f"Tool: {name}\nArguments: {json.dumps(arguments, indent=2)}"
                approved = self._approval_handler(name, reason)
                if not approved:
                    raise ToolApprovalDenied(f"Approval denied for tool '{name}'")
            else:
                # No approval handler set, deny dangerous operations by default
                raise ToolApprovalDenied(
                    f"Tool '{name}' requires approval but no handler is set"
                )

        # Execute with timeout
        try:
            result = await asyncio.wait_for(
                tool.execute(**arguments), timeout=tool.metadata.timeout
            )
            return result
        except asyncio.TimeoutError:
            raise ToolExecutionError(
                f"Tool '{name}' timed out after {tool.metadata.timeout}s"
            )
        except Exception as e:
            raise ToolExecutionError(f"Tool '{name}' failed: {str(e)}")


# Global registry instance
_registry: Optional[ToolRegistry] = None


def get_registry() -> ToolRegistry:
    """Get the global tool registry"""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry


# Exceptions


class ToolError(Exception):
    """Base exception for tool errors"""

    pass


class ToolNotFoundError(ToolError):
    """Tool not found in registry"""

    pass


class ToolExecutionError(ToolError):
    """Tool execution failed"""

    pass


class ToolApprovalDenied(ToolError):
    """Tool execution requires approval which was denied"""

    pass


class ToolTimeoutError(ToolError):
    """Tool execution timed out"""

    pass

