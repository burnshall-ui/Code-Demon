"""
Git Push/Pull Tools

Push and pull from remote repositories
"""

from pathlib import Path
from git import Repo, InvalidGitRepositoryError
from ..registry import Tool, ToolMetadata, ToolCategory, ToolParameter


class GitPushTool(Tool):
    """Tool to push commits to remote"""

    def _define_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="git_push",
            description="Push commits to remote repository.",
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
                    name="remote",
                    type="string",
                    description="Remote name (defaults to 'origin')",
                    required=False,
                    default="origin",
                ),
                ToolParameter(
                    name="branch",
                    type="string",
                    description="Branch to push (defaults to current branch)",
                    required=False,
                    default=None,
                ),
                ToolParameter(
                    name="force",
                    type="boolean",
                    description="Force push (dangerous!)",
                    required=False,
                    default=False,
                ),
            ],
            requires_approval=True,  # Push requires approval
            dangerous=True,
            timeout=60,
        )

    async def execute(
        self,
        path: str = ".",
        remote: str = "origin",
        branch: str | None = None,
        force: bool = False,
    ) -> str:
        """Push to remote"""
        try:
            repo_path = Path(path).expanduser().resolve()

            try:
                repo = Repo(repo_path, search_parent_directories=True)
            except InvalidGitRepositoryError:
                return f"Error: '{path}' is not a git repository"

            # Get branch to push
            if branch is None:
                if repo.head.is_detached:
                    return "Error: HEAD is detached. Specify a branch to push."
                branch = repo.active_branch.name

            # Get remote
            try:
                remote_obj = repo.remote(remote)
            except Exception:
                return f"Error: Remote '{remote}' not found"

            # Push
            push_args = []
            if force:
                push_args.append("--force")

            result = remote_obj.push(branch, *push_args)

            output = []
            output.append(f"✓ Successfully pushed to {remote}/{branch}")

            for info in result:
                if info.flags & info.ERROR:
                    output.append(f"⚠ Error: {info.summary}")
                elif info.flags & info.REJECTED:
                    output.append(f"⚠ Rejected: {info.summary}")
                else:
                    output.append(f"✓ {info.summary}")

            return "\n".join(output)

        except Exception as e:
            return f"Error pushing: {str(e)}"


class GitPullTool(Tool):
    """Tool to pull from remote"""

    def _define_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="git_pull",
            description="Pull changes from remote repository.",
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
                    name="remote",
                    type="string",
                    description="Remote name (defaults to 'origin')",
                    required=False,
                    default="origin",
                ),
                ToolParameter(
                    name="branch",
                    type="string",
                    description="Branch to pull (defaults to current branch)",
                    required=False,
                    default=None,
                ),
            ],
            requires_approval=True,  # Pull can modify working directory
            dangerous=False,
            timeout=60,
        )

    async def execute(
        self, path: str = ".", remote: str = "origin", branch: str | None = None
    ) -> str:
        """Pull from remote"""
        try:
            repo_path = Path(path).expanduser().resolve()

            try:
                repo = Repo(repo_path, search_parent_directories=True)
            except InvalidGitRepositoryError:
                return f"Error: '{path}' is not a git repository"

            # Check for uncommitted changes
            if repo.is_dirty():
                return "Error: You have uncommitted changes. Commit or stash them first."

            # Get remote
            try:
                remote_obj = repo.remote(remote)
            except Exception:
                return f"Error: Remote '{remote}' not found"

            # Pull
            result = remote_obj.pull(branch) if branch else remote_obj.pull()

            output = []
            output.append(f"✓ Successfully pulled from {remote}")

            for info in result:
                if info.flags & info.ERROR:
                    output.append(f"⚠ Error: {info.note}")
                elif info.flags & info.REJECTED:
                    output.append(f"⚠ Rejected: {info.note}")
                else:
                    output.append(f"✓ Updated: {info.note}")

            return "\n".join(output)

        except Exception as e:
            return f"Error pulling: {str(e)}"

