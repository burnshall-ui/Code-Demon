"""
Terminal UI Components

Rich-based UI elements for the CLI
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

console = Console()


def print_banner() -> None:
    """Print the code-demon banner"""
    banner = """
  ╔═══════════════════════════════════════════╗
  ║                                           ║
  ║   ██████╗ ██████╗ ██████╗ ███████╗       ║
  ║  ██╔════╝██╔═══██╗██╔══██╗██╔════╝       ║
  ║  ██║     ██║   ██║██║  ██║█████╗         ║
  ║  ██║     ██║   ██║██║  ██║██╔══╝         ║
  ║  ╚██████╗╚██████╔╝██████╔╝███████╗       ║
  ║   ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝       ║
  ║                                           ║
  ║  ██████╗ ███████╗███╗   ███╗ ██████╗ ███╗  ██╗
  ║  ██╔══██╗██╔════╝████╗ ████║██╔═══██╗████╗ ██║
  ║  ██║  ██║█████╗  ██╔████╔██║██║   ██║██╔██╗██║
  ║  ██║  ██║██╔══╝  ██║╚██╔╝██║██║   ██║██║╚████║
  ║  ██████╔╝███████╗██║ ╚═╝ ██║╚██████╔╝██║ ╚███║
  ║  ╚═════╝ ╚══════╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚══╝
  ║                                           ║
  ╚═══════════════════════════════════════════╝
    """
    console.print(banner, style="bold red")
    console.print(
        "  [dim]Your AI Coding & Server Admin Assistant[/dim]\n", justify="center"
    )


def print_welcome(personality: str) -> None:
    """Print welcome message"""
    from ..personality.phrases import get_greeting

    greeting = get_greeting()

    panel = Panel(
        f"[bold]{greeting}[/bold]\n\n"
        f"Personality: [cyan]{personality}[/cyan]\n"
        f"Type your request or 'help' for commands.\n"
        f"Type 'exit' or 'quit' to end the session.",
        title="[red]Welcome[/red]",
        border_style="red",
    )
    console.print(panel)
    console.print()


def print_goodbye() -> None:
    """Print goodbye message"""
    from ..personality.phrases import get_goodbye

    goodbye = get_goodbye()
    console.print(f"\n[red]{goodbye}[/red]\n")


def print_help() -> None:
    """Print help information"""
    help_text = """[bold]Available Commands:[/bold]

[yellow]help[/yellow]          Show this help message
[yellow]exit/quit[/yellow]     End the session
[yellow]clear[/yellow]         Clear conversation history
[yellow]stats[/yellow]         Show session statistics
[yellow]achievements[/yellow]  Show your achievements

[bold]Tool Categories:[/bold]

📁 [cyan]Files:[/cyan]     read_file, write_file, edit_file, search_files, list_directory
🐙 [cyan]Git:[/cyan]       git_status, git_commit, git_add, git_diff, git_branch, git_push
🔧 [cyan]Execution:[/cyan] execute_command, run_python, run_tests
🌐 [cyan]Web:[/cyan]       fetch_url, call_api, web_search

[bold]Examples:[/bold]

• "Read the README.md file"
• "Show me git status"
• "Edit main.py and fix the bug on line 42"
• "Commit these changes with message 'fix: resolve issue'"
• "Run the tests"
"""
    console.print(Panel(help_text, title="[red]Code Demon Help[/red]", border_style="red"))


def print_stats(history_storage, achievement_tracker) -> None:
    """Print session statistics"""
    stats = history_storage.get_stats()

    table = Table(title="📊 Statistics", border_style="red")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Total Sessions", str(stats.total_sessions))
    table.add_row("Successful", str(stats.successful_sessions))
    table.add_row("Failed", str(stats.failed_sessions))
    table.add_row("Total Messages", str(stats.total_messages))
    table.add_row("Total Tool Calls", str(stats.total_tool_calls))
    table.add_row("Avg Session Duration", f"{stats.average_session_duration:.1f} min")
    table.add_row("", "")
    table.add_row("Achievements Earned", str(len(achievement_tracker.earned)))
    table.add_row(
        "Achievement Progress", f"{achievement_tracker.get_progress_percentage():.1f}%"
    )
    table.add_row("Total Points", str(achievement_tracker.get_total_points()))

    console.print()
    console.print(table)
    console.print()

    if stats.most_used_tools:
        console.print("[bold]🔧 Most Used Tools:[/bold]")
        for tool, count in stats.most_used_tools[:5]:
            console.print(f"  • {tool}: {count}x")
        console.print()


def print_achievements(achievement_tracker) -> None:
    """Print earned achievements"""
    earned = achievement_tracker.get_earned_achievements()

    if not earned:
        console.print(
            "\n[yellow]No achievements yet. Keep coding to unlock them![/yellow]\n"
        )
        return

    table = Table(title="🏆 Your Achievements", border_style="red")
    table.add_column("Icon", style="yellow")
    table.add_column("Name", style="bold cyan")
    table.add_column("Description", style="white")
    table.add_column("Points", style="green", justify="right")

    for achievement in sorted(earned, key=lambda a: a.points, reverse=True):
        table.add_row(
            achievement.icon,
            achievement.name,
            achievement.description,
            str(achievement.points),
        )

    console.print()
    console.print(table)
    console.print(
        f"\n[bold]Total: {len(earned)} achievements, {achievement_tracker.get_total_points()} points[/bold]"
    )
    console.print(
        f"[dim]Progress: {achievement_tracker.get_progress_percentage():.1f}% complete[/dim]\n"
    )


def print_error(message: str) -> None:
    """Print error message"""
    console.print(f"[bold red]Error:[/bold red] {message}")


def print_info(message: str) -> None:
    """Print info message"""
    console.print(f"[dim cyan]{message}[/dim cyan]")

