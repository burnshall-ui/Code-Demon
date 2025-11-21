"""
Achievement Definitions

All available achievements for code-demon
"""

from dataclasses import dataclass
from enum import Enum
from typing import Literal


class AchievementRarity(str, Enum):
    """Achievement rarity levels"""

    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class AchievementCategory(str, Enum):
    """Achievement categories"""

    SESSIONS = "sessions"
    TOOLS = "tools"
    GIT = "git"
    FILES = "files"
    CODE = "code"
    SPECIAL = "special"


@dataclass
class Achievement:
    """An achievement definition"""

    id: str
    name: str
    description: str
    category: AchievementCategory
    rarity: AchievementRarity
    icon: str
    points: int


# All Achievements
ACHIEVEMENTS = [
    # Session Achievements
    Achievement(
        id="first_blood",
        name="First Blood",
        description="Deine erste Session abgeschlossen",
        category=AchievementCategory.SESSIONS,
        rarity=AchievementRarity.COMMON,
        icon="[*]",
        points=10,
    ),
    Achievement(
        id="veteran",
        name="Veteran",
        description="50 Sessions abgeschlossen",
        category=AchievementCategory.SESSIONS,
        rarity=AchievementRarity.RARE,
        icon="[VET]",
        points=75,
    ),
    Achievement(
        id="legend",
        name="Legend",
        description="100 Sessions abgeschlossen",
        category=AchievementCategory.SESSIONS,
        rarity=AchievementRarity.EPIC,
        icon="[LEG]",
        points=150,
    ),
    # Tool Achievements
    Achievement(
        id="first_tool",
        name="Tool Master Beginner",
        description="Erstes Tool erfolgreich benutzt",
        category=AchievementCategory.TOOLS,
        rarity=AchievementRarity.COMMON,
        icon="[T]",
        points=10,
    ),
    Achievement(
        id="tool_enthusiast",
        name="Tool Enthusiast",
        description="10 verschiedene Tools benutzt",
        category=AchievementCategory.TOOLS,
        rarity=AchievementRarity.UNCOMMON,
        icon="[TT]",
        points=25,
    ),
    Achievement(
        id="tool_master",
        name="Tool Master",
        description="Alle verfügbaren Tools mindestens einmal benutzt",
        category=AchievementCategory.TOOLS,
        rarity=AchievementRarity.RARE,
        icon="[TTT]",
        points=50,
    ),
    # Git Achievements
    Achievement(
        id="first_commit",
        name="First Commit",
        description="Erster Git Commit gemacht",
        category=AchievementCategory.GIT,
        rarity=AchievementRarity.COMMON,
        icon="[C]",
        points=15,
    ),
    Achievement(
        id="commit_master",
        name="Commit Master",
        description="50 Commits gemacht",
        category=AchievementCategory.GIT,
        rarity=AchievementRarity.UNCOMMON,
        icon="[CC]",
        points=40,
    ),
    Achievement(
        id="git_guru",
        name="Git Guru",
        description="Alle Git-Tools benutzt (status, commit, push, branch, diff)",
        category=AchievementCategory.GIT,
        rarity=AchievementRarity.RARE,
        icon="[GIT]",
        points=60,
    ),
    Achievement(
        id="merge_master",
        name="Merge Master",
        description="50 erfolgreiche Git Merges",
        category=AchievementCategory.GIT,
        rarity=AchievementRarity.RARE,
        icon="[MERGE]",
        points=60,
    ),
    # File Operations
    Achievement(
        id="file_editor",
        name="File Editor",
        description="10 Dateien erfolgreich editiert",
        category=AchievementCategory.FILES,
        rarity=AchievementRarity.COMMON,
        icon="[ED]",
        points=20,
    ),
    Achievement(
        id="code_surgeon",
        name="Code Surgeon",
        description="100 Dateien editiert - präzise wie ein Chirurg",
        category=AchievementCategory.FILES,
        rarity=AchievementRarity.RARE,
        icon="[SURG]",
        points=70,
    ),
    # Code Achievements
    Achievement(
        id="bug_hunter",
        name="Bug Hunter",
        description="50 Bugs gefixt",
        category=AchievementCategory.CODE,
        rarity=AchievementRarity.UNCOMMON,
        icon="[BUG]",
        points=50,
    ),
    Achievement(
        id="test_warrior",
        name="Test Warrior",
        description="100 Tests geschrieben oder ausgeführt",
        category=AchievementCategory.CODE,
        rarity=AchievementRarity.RARE,
        icon="[TEST]",
        points=80,
    ),
    Achievement(
        id="refactor_king",
        name="Refactor King",
        description="100 Code Refactorings durchgeführt",
        category=AchievementCategory.CODE,
        rarity=AchievementRarity.EPIC,
        icon="[REF]",
        points=100,
    ),
    Achievement(
        id="code_master",
        name="Code Master",
        description="1000 Zeilen Code geschrieben",
        category=AchievementCategory.CODE,
        rarity=AchievementRarity.EPIC,
        icon="[CODE]",
        points=120,
    ),
    # Special/Time-based
    Achievement(
        id="night_owl",
        name="Night Owl",
        description="10 Sessions zwischen 00:00 und 06:00 Uhr",
        category=AchievementCategory.SPECIAL,
        rarity=AchievementRarity.UNCOMMON,
        icon="[OWL]",
        points=40,
    ),
    Achievement(
        id="speed_demon",
        name="Speed Demon",
        description="Problem in unter 1 Minute gelöst",
        category=AchievementCategory.SPECIAL,
        rarity=AchievementRarity.RARE,
        icon="[!!!]",
        points=50,
    ),
    Achievement(
        id="marathon_runner",
        name="Marathon Runner",
        description="Session länger als 30 Minuten",
        category=AchievementCategory.SPECIAL,
        rarity=AchievementRarity.UNCOMMON,
        icon="[RUN]",
        points=30,
    ),
    Achievement(
        id="perfectionist",
        name="Perfectionist",
        description="10 Sessions in Folge erfolgreich",
        category=AchievementCategory.SPECIAL,
        rarity=AchievementRarity.EPIC,
        icon="[***]",
        points=100,
    ),
    Achievement(
        id="friday_13th",
        name="Friday the 13th Survivor",
        description="Session an einem Freitag dem 13. überlebt",
        category=AchievementCategory.SPECIAL,
        rarity=AchievementRarity.RARE,
        icon="[666]",
        points=66,
    ),
    # Legendary
    Achievement(
        id="demon_master",
        name="Demon Master",
        description="1000 Tools erfolgreich ausgeführt",
        category=AchievementCategory.TOOLS,
        rarity=AchievementRarity.LEGENDARY,
        icon="[DEMON]",
        points=500,
    ),
    Achievement(
        id="immortal",
        name="Immortal",
        description="365 Tage code-demon benutzt",
        category=AchievementCategory.SESSIONS,
        rarity=AchievementRarity.LEGENDARY,
        icon="[INF]",
        points=1000,
    ),
]


def get_achievement_by_id(achievement_id: str) -> Achievement | None:
    """Get achievement by ID"""
    for achievement in ACHIEVEMENTS:
        if achievement.id == achievement_id:
            return achievement
    return None


def get_achievements_by_category(category: AchievementCategory) -> list[Achievement]:
    """Get all achievements in a category"""
    return [a for a in ACHIEVEMENTS if a.category == category]


def get_achievements_by_rarity(rarity: AchievementRarity) -> list[Achievement]:
    """Get all achievements of a rarity"""
    return [a for a in ACHIEVEMENTS if a.rarity == rarity]

