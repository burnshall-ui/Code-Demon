"""
Achievement Tracker

Track and award achievements
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
from .definitions import Achievement, ACHIEVEMENTS, get_achievement_by_id


class AchievementTracker:
    """Tracks achievement progress"""

    def __init__(self, storage_file: Path):
        self.storage_file = storage_file
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing progress
        self.earned: Set[str] = set()
        self.progress: Dict[str, int] = {}
        self.stats: Dict[str, int] = {}
        self._load()

    def _load(self) -> None:
        """Load progress from disk"""
        if not self.storage_file.exists():
            return

        try:
            with open(self.storage_file, "r") as f:
                data = json.load(f)
                self.earned = set(data.get("earned", []))
                self.progress = data.get("progress", {})
                self.stats = data.get("stats", {})
        except Exception:
            pass

    def _save(self) -> None:
        """Save progress to disk"""
        data = {
            "earned": list(self.earned),
            "progress": self.progress,
            "stats": self.stats,
        }
        with open(self.storage_file, "w") as f:
            json.dump(data, f, indent=2)

    def increment_stat(self, stat_name: str, amount: int = 1) -> None:
        """Increment a stat"""
        self.stats[stat_name] = self.stats.get(stat_name, 0) + amount
        self._save()

    def get_stat(self, stat_name: str) -> int:
        """Get a stat value"""
        return self.stats.get(stat_name, 0)

    def check_and_award(self) -> List[Achievement]:
        """Check for new achievements and award them"""
        newly_earned = []

        for achievement in ACHIEVEMENTS:
            if achievement.id in self.earned:
                continue

            if self._check_achievement(achievement):
                self.earned.add(achievement.id)
                newly_earned.append(achievement)

        if newly_earned:
            self._save()

        return newly_earned

    def _check_achievement(self, achievement: Achievement) -> bool:
        """Check if an achievement should be awarded"""
        # Session-based
        if achievement.id == "first_blood":
            return self.get_stat("sessions_completed") >= 1
        if achievement.id == "veteran":
            return self.get_stat("sessions_completed") >= 50
        if achievement.id == "legend":
            return self.get_stat("sessions_completed") >= 100

        # Tool-based
        if achievement.id == "first_tool":
            return self.get_stat("tools_used") >= 1
        if achievement.id == "tool_enthusiast":
            return self.get_stat("unique_tools_used") >= 10
        if achievement.id == "tool_master":
            return self.get_stat("all_tools_used") >= 1
        if achievement.id == "demon_master":
            return self.get_stat("tools_used") >= 1000

        # Git-based
        if achievement.id == "first_commit":
            return self.get_stat("git_commits") >= 1
        if achievement.id == "commit_master":
            return self.get_stat("git_commits") >= 50
        if achievement.id == "git_guru":
            return self.get_stat("git_tools_used") >= 5
        if achievement.id == "merge_master":
            return self.get_stat("git_merges") >= 50

        # File-based
        if achievement.id == "file_editor":
            return self.get_stat("files_edited") >= 10
        if achievement.id == "code_surgeon":
            return self.get_stat("files_edited") >= 100

        # Code-based
        if achievement.id == "bug_hunter":
            return self.get_stat("bugs_fixed") >= 50
        if achievement.id == "test_warrior":
            return self.get_stat("tests_run") >= 100
        if achievement.id == "refactor_king":
            return self.get_stat("refactorings") >= 100
        if achievement.id == "code_master":
            return self.get_stat("lines_written") >= 1000

        # Special
        if achievement.id == "night_owl":
            return self.get_stat("night_sessions") >= 10
        if achievement.id == "speed_demon":
            return self.get_stat("fast_sessions") >= 1
        if achievement.id == "marathon_runner":
            return self.get_stat("long_sessions") >= 1
        if achievement.id == "perfectionist":
            return self.get_stat("consecutive_successes") >= 10
        if achievement.id == "friday_13th":
            return self.get_stat("friday_13th_sessions") >= 1
        if achievement.id == "immortal":
            return self.get_stat("days_active") >= 365

        return False

    def get_earned_achievements(self) -> List[Achievement]:
        """Get all earned achievements"""
        return [get_achievement_by_id(aid) for aid in self.earned if get_achievement_by_id(aid)]

    def get_total_points(self) -> int:
        """Get total points from earned achievements"""
        return sum(a.points for a in self.get_earned_achievements())

    def get_progress_percentage(self) -> float:
        """Get overall achievement completion percentage"""
        return (len(self.earned) / len(ACHIEVEMENTS)) * 100

    def mark_tool_used(self, tool_name: str) -> None:
        """Mark a tool as used"""
        self.increment_stat("tools_used")

        # Track unique tools
        unique_tools = self.stats.get("unique_tools_list", [])
        if tool_name not in unique_tools:
            unique_tools.append(tool_name)
            self.stats["unique_tools_list"] = unique_tools
            self.stats["unique_tools_used"] = len(unique_tools)

        self._save()

    def mark_session_completed(self, success: bool, duration_minutes: float) -> None:
        """Mark a session as completed"""
        self.increment_stat("sessions_completed")

        if success:
            self.increment_stat("successful_sessions")
            self.increment_stat("consecutive_successes")
        else:
            self.stats["consecutive_successes"] = 0

        # Check duration
        if duration_minutes > 30:
            self.increment_stat("long_sessions")
        if duration_minutes < 1:
            self.increment_stat("fast_sessions")

        # Check time of day
        hour = datetime.now().hour
        if 0 <= hour < 6:
            self.increment_stat("night_sessions")

        # Check Friday 13th
        now = datetime.now()
        if now.weekday() == 4 and now.day == 13:
            self.increment_stat("friday_13th_sessions")

        self._save()


# Global tracker instance
_tracker: AchievementTracker | None = None


def get_achievement_tracker(storage_file: Path | None = None) -> AchievementTracker:
    """Get the global achievement tracker"""
    global _tracker
    if _tracker is None:
        if storage_file is None:
            storage_file = Path.home() / ".code-demon" / "achievements.json"
        _tracker = AchievementTracker(storage_file)
    return _tracker


def reset_achievement_tracker() -> None:
    """Reset the global tracker"""
    global _tracker
    _tracker = None

