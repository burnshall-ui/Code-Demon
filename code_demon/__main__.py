#!/usr/bin/env python3
"""
Code Demon - AI Coding & Server Admin Assistant

Main entry point for the CLI
"""

import asyncio
import sys
import os
import logging
import click
from rich.console import Console
from rich.prompt import Prompt

# Suppress verbose logging from dependencies BEFORE imports
os.environ.setdefault("COGNEE_LOG_LEVEL", "CRITICAL")
logging.basicConfig(level=logging.WARNING)
logging.getLogger("cognee").setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("httpcore").setLevel(logging.CRITICAL)
logging.getLogger("structlog").setLevel(logging.CRITICAL)
logging.getLogger("lancedb").setLevel(logging.CRITICAL)

from .config.settings import get_settings
from .core.llm.ollama import OllamaProvider
from .core.llm.textgen import TextGenProvider
from .core.agent import Agent
from .tools.registry import get_registry
from .history.storage import get_history_storage
from .achievements.tracker import get_achievement_tracker
from .core.approval import get_approval_system
from .core.memory import get_memory_system
from .cli.ui import (
    print_banner,
    print_welcome,
    print_goodbye,
    print_help,
    print_stats,
    print_achievements,
    print_error,
    print_info,
)

# Import and register all tools
from .tools.files.read import ReadFileTool
from .tools.files.write import WriteFileTool
from .tools.files.edit import EditFileTool
from .tools.files.search import SearchFilesTool, ListDirectoryTool
from .tools.git.status import GitStatusTool
from .tools.git.commit import GitCommitTool, GitAddTool
from .tools.git.diff import GitDiffTool
from .tools.git.branch import GitBranchTool, GitCheckoutTool
from .tools.git.push import GitPushTool, GitPullTool
from .tools.execution.command import ExecuteCommandTool, RunPythonTool, RunTestsTool
from .tools.web.http import FetchURLTool, CallAPITool, WebSearchTool

console = Console()


def register_all_tools() -> None:
    """Register all available tools"""
    registry = get_registry()

    # File tools
    registry.register(ReadFileTool())
    registry.register(WriteFileTool())
    registry.register(EditFileTool())
    registry.register(SearchFilesTool())
    registry.register(ListDirectoryTool())

    # Git tools
    registry.register(GitStatusTool())
    registry.register(GitCommitTool())
    registry.register(GitAddTool())
    registry.register(GitDiffTool())
    registry.register(GitBranchTool())
    registry.register(GitCheckoutTool())
    registry.register(GitPushTool())
    registry.register(GitPullTool())

    # Execution tools
    registry.register(ExecuteCommandTool())
    registry.register(RunPythonTool())
    registry.register(RunTestsTool())

    # Web tools
    registry.register(FetchURLTool())
    registry.register(CallAPITool())
    registry.register(WebSearchTool())


def create_llm_provider() -> OllamaProvider | TextGenProvider:
    """Create LLM provider based on settings"""
    settings = get_settings()

    if settings.llm_provider == "ollama":
        return OllamaProvider(model=settings.ollama_model, base_url=settings.ollama_url)
    elif settings.llm_provider == "textgen":
        return TextGenProvider(
            model=settings.textgen_model, base_url=settings.textgen_url
        )
    else:
        raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")


async def chat_loop(agent: Agent) -> None:
    """Main chat loop"""
    settings = get_settings()
    history = get_history_storage()
    achievements = get_achievement_tracker()

    while True:
        try:
            # Get user input
            user_input = Prompt.ask("\n[bold red]You[/bold red]").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.lower() in ["exit", "quit"]:
                break
            elif user_input.lower() == "help":
                print_help()
                continue
            elif user_input.lower() == "clear":
                agent.reset_conversation()
                print_info("Conversation cleared.")
                continue
            elif user_input.lower() == "stats":
                print_stats(history, achievements)
                continue
            elif user_input.lower() == "achievements":
                print_achievements(achievements)
                continue

            # Process with agent
            console.print()
            console.print("[dim]Thinking...[/dim]")

            try:
                response = await agent.chat(user_input)

                console.print()
                console.print("[bold red]Code Demon:[/bold red]")
                console.print(response)

            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted[/yellow]")
                continue
            except Exception as e:
                print_error(f"Agent error: {str(e)}")
                continue

        except KeyboardInterrupt:
            console.print()
            break
        except EOFError:
            break


@click.command()
@click.option("--model", help="Override LLM model")
@click.option("--provider", type=click.Choice(["ollama", "textgen"]), help="LLM provider")
@click.option("--personality", type=click.Choice(["cynical", "professional", "friendly"]), help="Agent personality")
def main(model: str | None, provider: str | None, personality: str | None) -> None:
    """
    Code Demon - AI Coding & Server Admin Assistant

    An intelligent agent for coding tasks and server administration,
    powered by local LLMs (Ollama or Text Generation WebUI).
    """
    # Load settings
    settings = get_settings()

    # Override settings if provided
    if model:
        if provider == "ollama" or settings.llm_provider == "ollama":
            settings.ollama_model = model
        elif provider == "textgen" or settings.llm_provider == "textgen":
            settings.textgen_model = model

    if provider:
        settings.llm_provider = provider

    if personality:
        settings.personality = personality

    # Print banner
    print_banner()

    # Register all tools
    register_all_tools()

    # Set up approval system
    approval_system = get_approval_system(settings.require_approval)

    # Connect approval to tool registry
    def approval_handler(operation: str, reason: str) -> bool:
        from .core.approval import ApprovalRequest

        request = ApprovalRequest(
            operation=operation, reason=reason, details="", dangerous=True
        )
        return approval_system.request_approval(request)

    registry = get_registry()
    registry.set_approval_handler(approval_handler)

    # Create LLM provider
    try:
        llm_provider = create_llm_provider()
    except Exception as e:
        print_error(f"Failed to create LLM provider: {e}")
        sys.exit(1)

    # Check LLM health
    print_info(f"Connecting to {settings.llm_provider}...")
    try:
        is_healthy = asyncio.run(llm_provider.health_check())
        if not is_healthy:
            print_error(
                f"{settings.llm_provider} is not responding. "
                f"Make sure it's running at {settings.ollama_url if settings.llm_provider == 'ollama' else settings.textgen_url}"
            )
            sys.exit(1)
        print_info(f"Connected to {settings.llm_provider} successfully!")
    except Exception as e:
        print_error(f"Failed to connect to {settings.llm_provider}: {e}")
        sys.exit(1)

    # Create agent
    agent = Agent(llm_provider)

    # Start session
    agent.start_session()

    # Print welcome
    print_welcome(settings.personality)

    # Initialize memory system (silently - it's optional)
    try:
        memory_system = get_memory_system()
        asyncio.run(memory_system.initialize())
    except Exception:
        # Silently fail - memory is optional
        pass

    # Run chat loop
    try:
        asyncio.run(chat_loop(agent))
    except KeyboardInterrupt:
        console.print()
    finally:
        # End session
        print_goodbye()
        agent.end_session(success=True)


if __name__ == "__main__":
    main()

