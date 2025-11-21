"""
LLM Provider Base Classes

Abstract interfaces for LLM providers
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class MessageRole(str, Enum):
    """Message roles in conversation"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class Message:
    """A message in the conversation"""

    role: MessageRole
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


@dataclass
class ToolDefinition:
    """Definition of a tool that the LLM can call"""

    name: str
    description: str
    parameters: Dict[str, Any]  # JSON Schema


@dataclass
class ToolCall:
    """A tool call made by the LLM"""

    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class LLMResponse:
    """Response from LLM"""

    content: str
    tool_calls: List[ToolCall]
    finish_reason: str
    model: str
    tokens_used: Optional[int] = None
    tokens_per_second: Optional[float] = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    def __init__(self, model: str, base_url: str):
        self.model = model
        self.base_url = base_url

    @abstractmethod
    async def chat(
        self,
        messages: List[Message],
        tools: Optional[List[ToolDefinition]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """
        Send a chat request to the LLM

        Args:
            messages: Conversation history
            tools: Available tools for the LLM to call
            temperature: Sampling temperature (0.0 - 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            LLMResponse with content and/or tool calls
        """
        pass

    @abstractmethod
    async def stream_chat(
        self,
        messages: List[Message],
        tools: Optional[List[ToolDefinition]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat response from the LLM

        Args:
            messages: Conversation history
            tools: Available tools for the LLM to call
            temperature: Sampling temperature (0.0 - 1.0)
            max_tokens: Maximum tokens to generate

        Yields:
            Tokens as they are generated
        """
        pass

    @abstractmethod
    def supports_tools(self) -> bool:
        """
        Check if this provider supports tool calling

        Returns:
            True if tools are supported
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the LLM provider is available

        Returns:
            True if healthy
        """
        pass


class LLMError(Exception):
    """Base exception for LLM errors"""

    pass


class LLMConnectionError(LLMError):
    """Error connecting to LLM provider"""

    pass


class LLMTimeoutError(LLMError):
    """LLM request timed out"""

    pass


class LLMToolCallError(LLMError):
    """Error in tool calling"""

    pass

