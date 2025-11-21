"""
History System Types

Type definitions for session tracking and history
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class MessageRole(str, Enum):
    """Message roles"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class ToolCallRecord:
    """Record of a tool call"""

    tool: str
    arguments: Dict[str, Any]
    result: str
    success: bool
    timestamp: datetime
    duration_ms: int


@dataclass
class MessageRecord:
    """Record of a message in conversation"""

    role: MessageRole
    content: str
    timestamp: datetime
    tool_calls: List[ToolCallRecord] = field(default_factory=list)


@dataclass
class SessionMetadata:
    """Metadata about a session"""

    problem: Optional[str] = None
    solution: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    success: bool = False
    user_rating: Optional[int] = None  # 1-5


@dataclass
class ChatSession:
    """A complete chat session"""

    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    messages: List[MessageRecord] = field(default_factory=list)
    tools_called: List[ToolCallRecord] = field(default_factory=list)
    metadata: SessionMetadata = field(default_factory=SessionMetadata)
    achievements_earned: List[str] = field(default_factory=list)

    def duration_minutes(self) -> float:
        """Get session duration in minutes"""
        if self.end_time:
            delta = self.end_time - self.start_time
            return delta.total_seconds() / 60
        return 0.0

    def message_count(self) -> int:
        """Get total message count"""
        return len(self.messages)

    def tool_count(self) -> int:
        """Get total tool call count"""
        return len(self.tools_called)


@dataclass
class HistoryStats:
    """Statistics about session history"""

    total_sessions: int
    successful_sessions: int
    failed_sessions: int
    most_used_tools: List[tuple[str, int]]
    common_problems: List[tuple[str, int]]
    average_session_duration: float
    total_tool_calls: int
    total_messages: int

