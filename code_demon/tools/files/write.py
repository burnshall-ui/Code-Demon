"""
Write File Tool

Write contents to files
"""

from pathlib import Path
from ..registry import Tool, ToolMetadata, ToolCategory, ToolParameter


class WriteFileTool(Tool):
    """Tool to write content to a file"""

    def _define_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="write_file",
            description="Write content to a file. Creates the file if it doesn't exist, overwrites if it does.",
            category=ToolCategory.FILES,
            parameters=[
                ToolParameter(
                    name="path",
                    type="string",
                    description="Path to the file to write (relative or absolute)",
                    required=True,
                ),
                ToolParameter(
                    name="content",
                    type="string",
                    description="Content to write to the file",
                    required=True,
                ),
                ToolParameter(
                    name="create_dirs",
                    type="boolean",
                    description="Create parent directories if they don't exist",
                    required=False,
                    default=True,
                ),
            ],
            requires_approval=True,  # Writing files is destructive
            dangerous=True,
            timeout=10,
        )

    async def execute(self, path: str, content: str, create_dirs: bool = True) -> str:
        """Write content to file"""
        try:
            file_path = Path(path).expanduser().resolve()

            # Create parent directories if requested
            if create_dirs:
                file_path.parent.mkdir(parents=True, exist_ok=True)

            # Check if parent directory exists
            if not file_path.parent.exists():
                return f"Error: Parent directory '{file_path.parent}' does not exist"

            # Write the file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            file_size = file_path.stat().st_size
            line_count = content.count("\n") + 1

            return f"✓ Successfully wrote {line_count} lines ({file_size} bytes) to '{path}'"

        except PermissionError:
            return f"Error: Permission denied writing to '{path}'"
        except Exception as e:
            return f"Error writing file: {str(e)}"

