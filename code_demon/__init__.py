"""
Code Demon - AI Coding & Server Admin Assistant
"""

__version__ = "0.1.0"
__author__ = "Tomasz"

from .core.agent import Agent
from .config.settings import get_settings

__all__ = ["Agent", "get_settings", "__version__"]

