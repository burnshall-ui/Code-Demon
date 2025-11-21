"""
Main Agent Loop

Orchestrates LLM, tools, conversation management, and achievements
"""

import asyncio
from typing import List, Optional
from datetime import datetime

from .llm.base import LLMProvider, Message, MessageRole, ToolDefinition, ToolCall
from ..tools.registry import get_registry, ToolRegistry
from ..history.storage import get_history_storage, HistoryStorage
from ..history.types import ToolCallRecord, MessageRole as HistoryMessageRole
from ..achievements.tracker import get_achievement_tracker, AchievementTracker
from .memory import get_memory_system
from ..personality.prompts import get_system_prompt
from ..personality.phrases import get_greeting, get_success_message
from ..config.settings import get_settings
from rich.console import Console

console = Console()


class Agent:
    """Main AI Agent"""

    def __init__(
        self,
        llm_provider: LLMProvider,
        tool_registry: Optional[ToolRegistry] = None,
        history_storage: Optional[HistoryStorage] = None,
        achievement_tracker: Optional[AchievementTracker] = None,
    ):
        self.llm = llm_provider
        self.registry = tool_registry or get_registry()
        self.history = history_storage or get_history_storage()
        self.achievements = achievement_tracker or get_achievement_tracker()
        self.settings = get_settings()

        # Conversation state
        self.messages: List[Message] = []
        self.max_conversation_length = self.settings.max_conversation_length
        self.max_tool_depth = self.settings.max_tool_depth

        # Initialize system prompt
        self._initialize_system_prompt()

    def _initialize_system_prompt(self) -> None:
        """Initialize system prompt based on personality"""
        system_prompt = get_system_prompt(self.settings.personality)
        self.messages.append(Message(role=MessageRole.SYSTEM, content=system_prompt))

    async def chat(self, user_message: str) -> str:
        """
        Process a user message and return response

        Args:
            user_message: User's input

        Returns:
            Agent's response
        """
        # Check memory for context
        full_message = user_message
        if self.settings.memory_enabled:
            memory = get_memory_system()
            results = await memory.search(user_message)
            if results:
                context = "\n\n[Memory Context]\n" + "\n".join(results)
                full_message += context
                console.print(f"  [dim]Found {len(results)} relevant memories[/dim]")

        # Add user message to conversation
        self.messages.append(Message(role=MessageRole.USER, content=full_message))

        # Track in history
        if self.settings.history_enabled:
            self.history.add_message(HistoryMessageRole.USER, user_message)

        # Get tools for LLM
        tools = self._get_tools_for_llm()

        # Process with tool calling loop
        response_text = await self._process_with_tools(tools)

        # Add assistant response to conversation
        self.messages.append(Message(role=MessageRole.ASSISTANT, content=response_text))

        # Track in history
        if self.settings.history_enabled:
            self.history.add_message(HistoryMessageRole.ASSISTANT, response_text)

        # Trim conversation if too long
        self._trim_conversation()

        return response_text

    async def _process_with_tools(self, tools: List[ToolDefinition]) -> str:
        """Process LLM response with tool calling loop"""
        depth = 0
        final_response = ""

        while depth < self.max_tool_depth:
            # Call LLM
            response = await self.llm.chat(self.messages, tools)

            # Check if we have tool calls
            if not response.tool_calls:
                # No tool calls, return the content
                final_response = response.content
                break

            # Execute tool calls
            tool_results = []
            for tool_call in response.tool_calls:
                result = await self._execute_tool(tool_call)
                tool_results.append(result)

                # Add tool result to conversation
                self.messages.append(
                    Message(role=MessageRole.TOOL, content=result, tool_call_id=tool_call.id)
                )

            depth += 1

            # If no content after tool calls, continue loop
            if not response.content:
                continue

            # If we have content, we're done
            final_response = response.content
            break

        if depth >= self.max_tool_depth:
            final_response += f"\n\n(Max tool depth reached: {self.max_tool_depth})"

        return final_response

    async def _execute_tool(self, tool_call: ToolCall) -> str:
        """Execute a tool call"""
        start_time = datetime.now()

        try:
            console.print(f"  [dim]→ Executing {tool_call.name}...[/dim]")

            # Execute the tool
            result = await self.registry.execute_tool(tool_call.name, tool_call.arguments)

            # Calculate duration
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            # Track in history
            if self.settings.history_enabled:
                tool_record = ToolCallRecord(
                    tool=tool_call.name,
                    arguments=tool_call.arguments,
                    result=result,
                    success=True,
                    timestamp=start_time,
                    duration_ms=duration_ms,
                )
                self.history.add_tool_call(tool_record)

            # Track achievements
            if self.settings.achievements_enabled:
                self.achievements.mark_tool_used(tool_call.name)

                # Check for git-specific achievements
                if tool_call.name == "git_commit":
                    self.achievements.increment_stat("git_commits")
                elif tool_call.name.startswith("git_"):
                    self.achievements.increment_stat("git_tools_used")

                # Check for file operations
                if tool_call.name == "edit_file":
                    self.achievements.increment_stat("files_edited")

                # Check for newly earned achievements
                new_achievements = self.achievements.check_and_award()
                if new_achievements:
                    for achievement in new_achievements:
                        console.print(
                            f"\n  [bold yellow]🏆 Achievement Unlocked: {achievement.name}[/bold yellow]"
                        )
                        console.print(f"  [dim]{achievement.description}[/dim]")

            # Memory indexing für wichtige Changes
            if self.settings.memory_enabled:
                memory = get_memory_system()

                # File edits indexieren
                if tool_call.name == "edit_file" and result and "Error" not in result:
                    file_path = tool_call.arguments.get("path", "unknown")
                    await memory.index_text(
                        f"File modified: {file_path}\nChange: {result[:300]}..."
                    )

                # Git commits indexieren
                elif tool_call.name == "git_commit" and result:
                    await memory.index_text(
                        f"Git commit: {tool_call.arguments.get('message', 'no message')}\n{result[:200]}"
                    )

            console.print(f"  [dim green]✓ {tool_call.name} completed[/dim green]")
            return result

        except Exception as e:
            error_msg = f"Error executing {tool_call.name}: {str(e)}"
            console.print(f"  [dim red]✗ {error_msg}[/dim red]")

            # Track failed tool call
            if self.settings.history_enabled:
                duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
                tool_record = ToolCallRecord(
                    tool=tool_call.name,
                    arguments=tool_call.arguments,
                    result=error_msg,
                    success=False,
                    timestamp=start_time,
                    duration_ms=duration_ms,
                )
                self.history.add_tool_call(tool_record)

            return error_msg

    def _get_tools_for_llm(self) -> List[ToolDefinition]:
        """Get tools in LLM-compatible format"""
        tools_data = self.registry.get_tools_for_llm()
        return [
            ToolDefinition(
                name=tool["name"],
                description=tool["description"],
                parameters=tool["parameters"],
            )
            for tool in tools_data
        ]

    def _trim_conversation(self) -> None:
        """Trim conversation to max length, keeping system prompt"""
        if len(self.messages) <= self.max_conversation_length:
            return

        # Keep system prompt (first message) and most recent messages
        system_prompt = self.messages[0]
        recent_messages = self.messages[-(self.max_conversation_length - 1) :]
        self.messages = [system_prompt] + recent_messages

    def start_session(self) -> None:
        """Start a new session"""
        if self.settings.history_enabled:
            self.history.start_session()

    def end_session(self, success: bool = True) -> None:
        """End the current session"""
        if self.settings.history_enabled:
            session = self.history.end_session(success)

            if session and self.settings.achievements_enabled:
                duration_minutes = session.duration_minutes()
                self.achievements.mark_session_completed(success, duration_minutes)

                # Check for newly earned achievements
                new_achievements = self.achievements.check_and_award()
                if new_achievements:
                    console.print("\n[bold yellow]🏆 Session Summary[/bold yellow]")
                    for achievement in new_achievements:
                        console.print(
                            f"  • {achievement.icon} {achievement.name} (+{achievement.points} pts)"
                        )

            # Session ins Memory schreiben
            if self.settings.memory_enabled and len(self.messages) > 3:
                try:
                    # Start new event loop since end_session is called after the main loop ends
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            loop.create_task(self._index_session_summary())
                        else:
                            asyncio.run(self._index_session_summary())
                    except RuntimeError:
                        # No event loop running, create a new one
                        asyncio.run(self._index_session_summary())
                except Exception as e:
                    console.print(f"[dim yellow]Session summary indexing failed: {e}[/dim yellow]")

    async def _index_session_summary(self) -> None:
        """Index important parts of the session"""
        memory = get_memory_system()

        # Letzte paar Messages als Context
        recent = self.messages[-5:]
        summary = "\n".join([f"{m.role.value}: {m.content[:200]}" for m in recent])

        await memory.index_text(f"Session summary:\n{summary}")

    def reset_conversation(self) -> None:
        """Reset conversation (keep system prompt)"""
        system_prompt = self.messages[0] if self.messages else None
        self.messages = []
        if system_prompt:
            self.messages.append(system_prompt)
        else:
            self._initialize_system_prompt()

