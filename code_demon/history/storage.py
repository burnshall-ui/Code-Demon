"""
History Storage

Store and retrieve session history
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from collections import Counter

from .types import (
    ChatSession,
    MessageRecord,
    ToolCallRecord,
    SessionMetadata,
    HistoryStats,
    MessageRole,
)


class HistoryStorage:
    """Manages session history storage"""

    def __init__(self, history_dir: Path):
        self.history_dir = history_dir
        self.history_dir.mkdir(parents=True, exist_ok=True)

        # Current session
        self.current_session: Optional[ChatSession] = None

    def start_session(self) -> ChatSession:
        """Start a new session"""
        session_id = str(uuid.uuid4())
        self.current_session = ChatSession(
            session_id=session_id,
            start_time=datetime.now(),
            metadata=SessionMetadata(),
        )
        return self.current_session

    def end_session(self, success: bool = True) -> Optional[ChatSession]:
        """End the current session"""
        if not self.current_session:
            return None

        self.current_session.end_time = datetime.now()
        self.current_session.metadata.success = success

        # Save to disk
        self._save_session(self.current_session)

        session = self.current_session
        self.current_session = None
        return session

    def add_message(
        self, role: MessageRole, content: str, tool_calls: List[ToolCallRecord] = None
    ) -> None:
        """Add a message to current session"""
        if not self.current_session:
            return

        message = MessageRecord(
            role=role,
            content=content,
            timestamp=datetime.now(),
            tool_calls=tool_calls or [],
        )
        self.current_session.messages.append(message)

    def add_tool_call(self, tool_call: ToolCallRecord) -> None:
        """Add a tool call to current session"""
        if not self.current_session:
            return

        self.current_session.tools_called.append(tool_call)

    def add_achievement(self, achievement_id: str) -> None:
        """Add an achievement to current session"""
        if not self.current_session:
            return

        self.current_session.achievements_earned.append(achievement_id)

    def _save_session(self, session: ChatSession) -> None:
        """Save session to disk"""
        # Create filename from session ID and timestamp
        filename = f"{session.start_time.strftime('%Y%m%d_%H%M%S')}_{session.session_id[:8]}.json"
        file_path = self.history_dir / filename

        # Convert to dict
        session_dict = {
            "session_id": session.session_id,
            "start_time": session.start_time.isoformat(),
            "end_time": session.end_time.isoformat() if session.end_time else None,
            "messages": [
                {
                    "role": msg.role.value,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "tool_calls": [
                        {
                            "tool": tc.tool,
                            "arguments": tc.arguments,
                            "result": tc.result,
                            "success": tc.success,
                            "timestamp": tc.timestamp.isoformat(),
                            "duration_ms": tc.duration_ms,
                        }
                        for tc in msg.tool_calls
                    ],
                }
                for msg in session.messages
            ],
            "tools_called": [
                {
                    "tool": tc.tool,
                    "arguments": tc.arguments,
                    "result": tc.result,
                    "success": tc.success,
                    "timestamp": tc.timestamp.isoformat(),
                    "duration_ms": tc.duration_ms,
                }
                for tc in session.tools_called
            ],
            "metadata": {
                "problem": session.metadata.problem,
                "solution": session.metadata.solution,
                "tags": session.metadata.tags,
                "success": session.metadata.success,
                "user_rating": session.metadata.user_rating,
            },
            "achievements_earned": session.achievements_earned,
        }

        # Write to file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(session_dict, f, indent=2, ensure_ascii=False)

    def load_session(self, session_id: str) -> Optional[ChatSession]:
        """Load a session by ID"""
        # Find session file
        for file_path in self.history_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("session_id") == session_id:
                        return self._dict_to_session(data)
            except Exception:
                continue
        return None

    def list_sessions(self, limit: int = 50) -> List[ChatSession]:
        """List recent sessions"""
        sessions = []

        for file_path in sorted(self.history_dir.glob("*.json"), reverse=True):
            if len(sessions) >= limit:
                break

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    session = self._dict_to_session(data)
                    sessions.append(session)
            except Exception:
                continue

        return sessions

    def get_stats(self) -> HistoryStats:
        """Get statistics about session history"""
        sessions = self.list_sessions(limit=1000)

        if not sessions:
            return HistoryStats(
                total_sessions=0,
                successful_sessions=0,
                failed_sessions=0,
                most_used_tools=[],
                common_problems=[],
                average_session_duration=0.0,
                total_tool_calls=0,
                total_messages=0,
            )

        successful = sum(1 for s in sessions if s.metadata.success)
        failed = len(sessions) - successful

        # Count tool usage
        tool_counts = Counter()
        for session in sessions:
            for tool_call in session.tools_called:
                tool_counts[tool_call.tool] += 1

        # Count problems
        problem_counts = Counter()
        for session in sessions:
            if session.metadata.problem:
                problem_counts[session.metadata.problem] += 1

        # Calculate average duration
        durations = [s.duration_minutes() for s in sessions if s.end_time]
        avg_duration = sum(durations) / len(durations) if durations else 0.0

        # Total counts
        total_tool_calls = sum(len(s.tools_called) for s in sessions)
        total_messages = sum(len(s.messages) for s in sessions)

        return HistoryStats(
            total_sessions=len(sessions),
            successful_sessions=successful,
            failed_sessions=failed,
            most_used_tools=tool_counts.most_common(10),
            common_problems=problem_counts.most_common(10),
            average_session_duration=avg_duration,
            total_tool_calls=total_tool_calls,
            total_messages=total_messages,
        )

    def _dict_to_session(self, data: dict) -> ChatSession:
        """Convert dict to ChatSession"""
        return ChatSession(
            session_id=data["session_id"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=(
                datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None
            ),
            messages=[
                MessageRecord(
                    role=MessageRole(msg["role"]),
                    content=msg["content"],
                    timestamp=datetime.fromisoformat(msg["timestamp"]),
                    tool_calls=[
                        ToolCallRecord(
                            tool=tc["tool"],
                            arguments=tc["arguments"],
                            result=tc["result"],
                            success=tc["success"],
                            timestamp=datetime.fromisoformat(tc["timestamp"]),
                            duration_ms=tc["duration_ms"],
                        )
                        for tc in msg.get("tool_calls", [])
                    ],
                )
                for msg in data.get("messages", [])
            ],
            tools_called=[
                ToolCallRecord(
                    tool=tc["tool"],
                    arguments=tc["arguments"],
                    result=tc["result"],
                    success=tc["success"],
                    timestamp=datetime.fromisoformat(tc["timestamp"]),
                    duration_ms=tc["duration_ms"],
                )
                for tc in data.get("tools_called", [])
            ],
            metadata=SessionMetadata(
                problem=data["metadata"].get("problem"),
                solution=data["metadata"].get("solution"),
                tags=data["metadata"].get("tags", []),
                success=data["metadata"].get("success", False),
                user_rating=data["metadata"].get("user_rating"),
            ),
            achievements_earned=data.get("achievements_earned", []),
        )


# Global storage instance
_storage: Optional[HistoryStorage] = None


def get_history_storage(history_dir: Optional[Path] = None) -> HistoryStorage:
    """Get the global history storage instance"""
    global _storage
    if _storage is None:
        if history_dir is None:
            history_dir = Path.home() / ".code-demon" / "history"
        _storage = HistoryStorage(history_dir)
    return _storage


def reset_history_storage() -> None:
    """Reset the global history storage"""
    global _storage
    _storage = None

