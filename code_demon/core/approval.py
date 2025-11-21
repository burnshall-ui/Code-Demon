"""
Approval System for Dangerous Operations

Manages user approval for destructive and dangerous operations
"""

from typing import Callable, Optional
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

console = Console()


@dataclass
class ApprovalRequest:
    """Request for user approval"""

    operation: str
    reason: str
    details: str
    dangerous: bool = False


# Dangerous operations that always require approval
DANGEROUS_OPERATIONS = [
    "write_file",
    "edit_file",
    "delete_file",
    "git_commit",
    "git_push",
    "execute_command",
    "run_script",
]

# File patterns that are always dangerous to modify
DANGEROUS_PATHS = [
    "/etc/",
    "/var/",
    "/usr/",
    "/bin/",
    "/sbin/",
    "/boot/",
    "/sys/",
    "/proc/",
    ".git/",
    ".env",
    "config.json",
    "package.json",
    "requirements.txt",
]


class ApprovalSystem:
    """Manages approval for dangerous operations"""

    def __init__(self, require_approval: bool = True):
        self.require_approval = require_approval
        self._approval_handler: Optional[Callable[[ApprovalRequest], bool]] = None
        self._auto_approve_all = False

    def set_approval_handler(self, handler: Callable[[ApprovalRequest], bool]) -> None:
        """Set custom approval handler"""
        self._approval_handler = handler

    def enable_auto_approve(self) -> None:
        """Enable auto-approval for all operations (dangerous!)"""
        self._auto_approve_all = True

    def disable_auto_approve(self) -> None:
        """Disable auto-approval"""
        self._auto_approve_all = False

    def is_dangerous_operation(self, operation: str) -> bool:
        """Check if an operation is dangerous"""
        return operation in DANGEROUS_OPERATIONS

    def is_dangerous_path(self, path: str) -> bool:
        """Check if a path is dangerous to modify"""
        path_lower = path.lower()
        return any(dangerous in path_lower for dangerous in DANGEROUS_PATHS)

    def needs_approval(self, operation: str, **kwargs: any) -> bool:
        """Check if an operation needs approval"""
        if not self.require_approval:
            return False

        if self._auto_approve_all:
            return False

        # Check if operation is dangerous
        if self.is_dangerous_operation(operation):
            return True

        # Check for dangerous paths
        if "path" in kwargs:
            if self.is_dangerous_path(kwargs["path"]):
                return True

        return False

    def request_approval(self, request: ApprovalRequest) -> bool:
        """
        Request user approval

        Args:
            request: Approval request details

        Returns:
            True if approved, False otherwise
        """
        if not self.require_approval or self._auto_approve_all:
            return True

        # Use custom handler if set
        if self._approval_handler:
            return self._approval_handler(request)

        # Default: CLI prompt
        return self._cli_approval(request)

    def _cli_approval(self, request: ApprovalRequest) -> bool:
        """CLI-based approval prompt"""
        console.print()

        # Build warning panel
        warning_text = f"[bold yellow]⚠ APPROVAL REQUIRED[/bold yellow]\n\n"
        warning_text += f"[bold]Operation:[/bold] {request.operation}\n"
        warning_text += f"[bold]Reason:[/bold] {request.reason}\n\n"
        warning_text += f"[dim]{request.details}[/dim]"

        if request.dangerous:
            warning_text += "\n\n[bold red]⚠ This is a DANGEROUS operation![/bold red]"

        console.print(
            Panel(
                warning_text,
                title="[red]⚠ Approval Required[/red]",
                border_style="red" if request.dangerous else "yellow",
            )
        )

        # Ask for confirmation
        approved = Confirm.ask(
            "\n[bold]Execute this operation?[/bold]",
            default=False,
        )

        console.print()
        return approved

    async def execute_with_approval(
        self, operation: str, executor: Callable, **kwargs: any
    ) -> any:
        """
        Execute an operation with approval check

        Args:
            operation: Operation name
            executor: Function to execute
            **kwargs: Operation arguments

        Returns:
            Result of executor

        Raises:
            ApprovalDeniedError: If approval is denied
        """
        if self.needs_approval(operation, **kwargs):
            # Build approval request
            details = "\n".join([f"{k}: {v}" for k, v in kwargs.items()])

            request = ApprovalRequest(
                operation=operation,
                reason=self._get_approval_reason(operation, **kwargs),
                details=details,
                dangerous=self.is_dangerous_operation(operation),
            )

            # Request approval
            if not self.request_approval(request):
                raise ApprovalDeniedError(f"User denied approval for '{operation}'")

        # Execute the operation
        return await executor(**kwargs)

    def _get_approval_reason(self, operation: str, **kwargs: any) -> str:
        """Get reason why approval is needed"""
        reasons = []

        if self.is_dangerous_operation(operation):
            reasons.append("Dangerous operation")

        if "path" in kwargs and self.is_dangerous_path(kwargs["path"]):
            reasons.append("Modifying sensitive file/directory")

        if operation in ["git_push", "git_commit"]:
            reasons.append("Modifying git repository")

        if not reasons:
            reasons.append("Requires confirmation")

        return ", ".join(reasons)


class ApprovalDeniedError(Exception):
    """Raised when user denies approval"""

    pass


# Global approval system instance
_approval_system: Optional[ApprovalSystem] = None


def get_approval_system(require_approval: bool = True) -> ApprovalSystem:
    """Get the global approval system instance"""
    global _approval_system
    if _approval_system is None:
        _approval_system = ApprovalSystem(require_approval)
    return _approval_system


def reset_approval_system() -> None:
    """Reset the global approval system"""
    global _approval_system
    _approval_system = None

