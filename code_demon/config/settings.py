"""
Configuration Management

Handles environment variables and application settings
"""

import os
from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # LLM Provider
    llm_provider: Literal["ollama", "textgen"] = Field(default="ollama")
    ollama_url: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="gpt-oss:20b")
    textgen_url: str = Field(default="http://localhost:5000")
    textgen_model: str = Field(default="default")

    # Features
    require_approval: bool = Field(default=True)
    achievements_enabled: bool = Field(default=True)
    history_enabled: bool = Field(default=True)
    memory_enabled: bool = Field(default=False)  # Disabled by default (requires Cognee LLM API key)

    # Personality
    personality: Literal["cynical", "professional", "friendly"] = Field(default="cynical")

    # Logging
    log_level: str = Field(default="INFO")
    log_file: str = Field(default="~/.code-demon/logs/demon.log")

    # Storage
    history_dir: str = Field(default="~/.code-demon/history")
    achievements_file: str = Field(default="~/.code-demon/achievements.json")

    # Security
    max_tool_depth: int = Field(default=10)
    max_conversation_length: int = Field(default=50)
    tool_timeout: int = Field(default=30)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def expanded_log_file(self) -> Path:
        """Expand ~ in log file path"""
        return Path(self.log_file).expanduser()

    @property
    def expanded_history_dir(self) -> Path:
        """Expand ~ in history dir path"""
        return Path(self.history_dir).expanduser()

    @property
    def expanded_achievements_file(self) -> Path:
        """Expand ~ in achievements file path"""
        return Path(self.achievements_file).expanduser()

    def ensure_dirs(self) -> None:
        """Create necessary directories"""
        self.expanded_log_file.parent.mkdir(parents=True, exist_ok=True)
        self.expanded_history_dir.mkdir(parents=True, exist_ok=True)
        self.expanded_achievements_file.parent.mkdir(parents=True, exist_ok=True)


# Global settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get the global settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.ensure_dirs()
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment"""
    global _settings
    _settings = Settings()
    _settings.ensure_dirs()
    return _settings

