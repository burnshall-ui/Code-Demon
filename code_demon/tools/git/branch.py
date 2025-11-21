"""
Git Branch Tools

Manage git branches
"""

from pathlib import Path
from git import Repo, InvalidGitRepositoryError
from ..registry import Tool, ToolMetadata, ToolCategory, ToolParameter


class GitBranchTool(Tool):
    """Tool to list and manage git branches"""

    def _define_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="git_branch",
            description="List all branches in the repository and show the current branch.",
            category=ToolCategory.GIT,
            parameters=[
                ToolParameter(
                    name="path",
                    type="string",
                    description="Path to git repository (defaults to current directory)",
                    required=False,
                    default=".",
                ),
            ],
            requires_approval=False,
            dangerous=False,
            timeout=10,
        )

    async def execute(self, path: str = ".") -> str:
        """List branches"""
        try:
            repo_path = Path(path).expanduser().resolve()

            try:
                repo = Repo(repo_path, search_parent_directories=True)
            except InvalidGitRepositoryError:
                return f"Error: '{path}' is not a git repository"

            # Get branches
            branches = repo.branches
            current_branch = repo.active_branch.name if not repo.head.is_detached else None

            output = []
            output.append("🌿 Branches:")
            output.append("")

            for branch in branches:
                if branch.name == current_branch:
                    output.append(f"* {branch.name} (current)")
                else:
                    output.append(f"  {branch.name}")

            # Get remote branches
            try:
                remote_branches = [ref.name for ref in repo.remote().refs]
                if remote_branches:
                    output.append("")
                    output.append("🌐 Remote branches:")
                    for branch in remote_branches[:10]:  # Limit to 10
                        output.append(f"  {branch}")
                    if len(remote_branches) > 10:
                        output.append(f"  ... and {len(remote_branches) - 10} more")
            except Exception:
                pass

            return "\n".join(output)

        except Exception as e:
            return f"Error listing branches: {str(e)}"


class GitCheckoutTool(Tool):
    """Tool to checkout a git branch"""

    def _define_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="git_checkout",
            description="Checkout a git branch or create a new branch.",
            category=ToolCategory.GIT,
            parameters=[
                ToolParameter(
                    name="branch",
                    type="string",
                    description="Branch name to checkout",
                    required=True,
                ),
                ToolParameter(
                    name="create",
                    type="boolean",
                    description="Create new branch if it doesn't exist",
                    required=False,
                    default=False,
                ),
                ToolParameter(
                    name="path",
                    type="string",
                    description="Path to git repository (defaults to current directory)",
                    required=False,
                    default=".",
                ),
            ],
            requires_approval=True,  # Checkout can be destructive
            dangerous=False,
            timeout=10,
        )

    async def execute(self, branch: str, create: bool = False, path: str = ".") -> str:
        """Checkout branch"""
        try:
            repo_path = Path(path).expanduser().resolve()

            try:
                repo = Repo(repo_path, search_parent_directories=True)
            except InvalidGitRepositoryError:
                return f"Error: '{path}' is not a git repository"

            # Check for uncommitted changes
            if repo.is_dirty():
                return "Error: You have uncommitted changes. Commit or stash them first."

            # Checkout or create branch
            if create:
                # Create new branch
                new_branch = repo.create_head(branch)
                new_branch.checkout()
                return f"✓ Created and checked out new branch '{branch}'"
            else:
                # Checkout existing branch
                if branch not in [b.name for b in repo.branches]:
                    return f"Error: Branch '{branch}' does not exist. Use create=true to create it."

                repo.git.checkout(branch)
                return f"✓ Checked out branch '{branch}'"

        except Exception as e:
            return f"Error checking out branch: {str(e)}"

