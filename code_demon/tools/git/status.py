"""
Git Status Tool

Get the current status of a git repository
"""

from pathlib import Path
from git import Repo, InvalidGitRepositoryError
from ..registry import Tool, ToolMetadata, ToolCategory, ToolParameter


class GitStatusTool(Tool):
    """Tool to get git repository status"""

    def _define_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="git_status",
            description="Get the status of a git repository. Shows modified, staged, and untracked files.",
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
        """Get git status"""
        try:
            repo_path = Path(path).expanduser().resolve()

            if not repo_path.exists():
                return f"Error: Path '{path}' does not exist"

            # Open repository
            try:
                repo = Repo(repo_path, search_parent_directories=True)
            except InvalidGitRepositoryError:
                return f"Error: '{path}' is not a git repository"

            # Get current branch
            branch = repo.active_branch.name if not repo.head.is_detached else "HEAD (detached)"

            # Get status
            changed_files = [item.a_path for item in repo.index.diff(None)]
            staged_files = [item.a_path for item in repo.index.diff("HEAD")]
            untracked_files = repo.untracked_files

            # Build output
            output = []
            output.append(f"📁 Repository: {repo.working_dir}")
            output.append(f"🌿 Branch: {branch}")
            output.append("")

            # Remote info
            try:
                remote = repo.remote("origin")
                output.append(f"🌐 Remote: {remote.url}")
            except Exception:
                output.append("🌐 Remote: (none)")

            output.append("")

            # Staged files
            if staged_files:
                output.append("✓ Staged changes:")
                for file in staged_files:
                    output.append(f"  + {file}")
                output.append("")

            # Modified files
            if changed_files:
                output.append("✎ Modified files:")
                for file in changed_files:
                    output.append(f"  M {file}")
                output.append("")

            # Untracked files
            if untracked_files:
                output.append("? Untracked files:")
                for file in untracked_files[:20]:  # Limit to 20 files
                    output.append(f"  ? {file}")
                if len(untracked_files) > 20:
                    output.append(f"  ... and {len(untracked_files) - 20} more")
                output.append("")

            # Summary
            if not staged_files and not changed_files and not untracked_files:
                output.append("✓ Working directory clean")
            else:
                total = len(staged_files) + len(changed_files) + len(untracked_files)
                output.append(
                    f"📊 Total: {len(staged_files)} staged, {len(changed_files)} modified, {len(untracked_files)} untracked"
                )

            return "\n".join(output)

        except Exception as e:
            return f"Error getting git status: {str(e)}"

