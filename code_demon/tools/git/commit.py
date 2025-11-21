"""
Git Commit Tool

Commit changes to git repository
"""

from pathlib import Path
from git import Repo, InvalidGitRepositoryError
from ..registry import Tool, ToolMetadata, ToolCategory, ToolParameter


class GitCommitTool(Tool):
    """Tool to commit changes to git"""

    def _define_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="git_commit",
            description="Commit staged changes to the git repository with a message.",
            category=ToolCategory.GIT,
            parameters=[
                ToolParameter(
                    name="message",
                    type="string",
                    description="Commit message",
                    required=True,
                ),
                ToolParameter(
                    name="path",
                    type="string",
                    description="Path to git repository (defaults to current directory)",
                    required=False,
                    default=".",
                ),
                ToolParameter(
                    name="add_all",
                    type="boolean",
                    description="Stage all modified files before committing",
                    required=False,
                    default=False,
                ),
            ],
            requires_approval=True,  # Committing requires approval
            dangerous=True,
            timeout=30,
        )

    async def execute(
        self, message: str, path: str = ".", add_all: bool = False
    ) -> str:
        """Commit changes"""
        try:
            repo_path = Path(path).expanduser().resolve()

            if not repo_path.exists():
                return f"Error: Path '{path}' does not exist"

            # Open repository
            try:
                repo = Repo(repo_path, search_parent_directories=True)
            except InvalidGitRepositoryError:
                return f"Error: '{path}' is not a git repository"

            # Stage all files if requested
            if add_all:
                repo.git.add(A=True)

            # Check if there are staged changes
            staged_files = [item.a_path for item in repo.index.diff("HEAD")]
            if not staged_files:
                return "Error: No staged changes to commit. Use add_all=true to stage all changes."

            # Commit
            commit = repo.index.commit(message)

            # Build output
            output = []
            output.append(f"✓ Successfully committed changes")
            output.append(f"📝 Commit: {commit.hexsha[:7]}")
            output.append(f"💬 Message: {message}")
            output.append(f"📁 Files: {len(staged_files)} files changed")
            output.append("")
            output.append("Changed files:")
            for file in staged_files[:10]:  # Show first 10 files
                output.append(f"  • {file}")
            if len(staged_files) > 10:
                output.append(f"  ... and {len(staged_files) - 10} more")

            return "\n".join(output)

        except Exception as e:
            return f"Error committing: {str(e)}"


class GitAddTool(Tool):
    """Tool to stage files for commit"""

    def _define_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="git_add",
            description="Stage files for commit.",
            category=ToolCategory.GIT,
            parameters=[
                ToolParameter(
                    name="files",
                    type="string",
                    description="Files to stage (space-separated) or '.' for all",
                    required=True,
                ),
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

    async def execute(self, files: str, path: str = ".") -> str:
        """Stage files"""
        try:
            repo_path = Path(path).expanduser().resolve()

            try:
                repo = Repo(repo_path, search_parent_directories=True)
            except InvalidGitRepositoryError:
                return f"Error: '{path}' is not a git repository"

            # Stage files
            if files == ".":
                repo.git.add(A=True)
                staged = "all files"
            else:
                file_list = files.split()
                repo.index.add(file_list)
                staged = ", ".join(file_list)

            return f"✓ Staged {staged}"

        except Exception as e:
            return f"Error staging files: {str(e)}"

