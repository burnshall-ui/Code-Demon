"""
Git Diff Tool

Show differences in git repository
"""

from pathlib import Path
from git import Repo, InvalidGitRepositoryError
from ..registry import Tool, ToolMetadata, ToolCategory, ToolParameter


class GitDiffTool(Tool):
    """Tool to show git diff"""

    def _define_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="git_diff",
            description="Show differences between working directory and last commit, or between commits.",
            category=ToolCategory.GIT,
            parameters=[
                ToolParameter(
                    name="path",
                    type="string",
                    description="Path to git repository (defaults to current directory)",
                    required=False,
                    default=".",
                ),
                ToolParameter(
                    name="file",
                    type="string",
                    description="Specific file to diff (optional)",
                    required=False,
                    default=None,
                ),
                ToolParameter(
                    name="staged",
                    type="boolean",
                    description="Show diff of staged changes",
                    required=False,
                    default=False,
                ),
            ],
            requires_approval=False,
            dangerous=False,
            timeout=10,
        )

    async def execute(
        self, path: str = ".", file: str | None = None, staged: bool = False
    ) -> str:
        """Show git diff"""
        try:
            repo_path = Path(path).expanduser().resolve()

            try:
                repo = Repo(repo_path, search_parent_directories=True)
            except InvalidGitRepositoryError:
                return f"Error: '{path}' is not a git repository"

            # Get diff
            if staged:
                # Diff of staged changes
                diff_text = repo.git.diff("--cached", file if file else "")
            else:
                # Diff of working directory
                diff_text = repo.git.diff(file if file else "")

            if not diff_text:
                return "No differences found"

            # Format output
            output = []
            if staged:
                output.append("📋 Staged changes:")
            else:
                output.append("📋 Working directory changes:")

            if file:
                output.append(f"📄 File: {file}")

            output.append("")
            output.append(diff_text)

            # Truncate if too long
            full_output = "\n".join(output)
            if len(full_output) > 5000:
                full_output = (
                    full_output[:5000]
                    + "\n\n... (diff truncated, too long to display)"
                )

            return full_output

        except Exception as e:
            return f"Error getting diff: {str(e)}"

