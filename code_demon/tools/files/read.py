"""
Read File Tool

Read contents of files
"""

from pathlib import Path
from ..registry import Tool, ToolMetadata, ToolCategory, ToolParameter


class ReadFileTool(Tool):
    """Tool to read file contents"""

    def _define_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="read_file",
            description="Read the contents of a file. Returns the full file content.",
            category=ToolCategory.FILES,
            parameters=[
                ToolParameter(
                    name="path",
                    type="string",
                    description="Path to the file to read (relative or absolute)",
                    required=True,
                ),
                ToolParameter(
                    name="start_line",
                    type="number",
                    description="Optional: Line number to start reading from (1-indexed)",
                    required=False,
                    default=None,
                ),
                ToolParameter(
                    name="end_line",
                    type="number",
                    description="Optional: Line number to end reading at (1-indexed, inclusive)",
                    required=False,
                    default=None,
                ),
            ],
            requires_approval=False,
            dangerous=False,
            timeout=10,
        )

    async def execute(
        self, path: str, start_line: int | None = None, end_line: int | None = None
    ) -> str:
        """Read file contents"""
        try:
            file_path = Path(path).expanduser().resolve()

            if not file_path.exists():
                return f"Error: File '{path}' does not exist"

            if not file_path.is_file():
                return f"Error: '{path}' is not a file"

            # Check file size (avoid reading huge files)
            file_size = file_path.stat().st_size
            max_size = 10 * 1024 * 1024  # 10 MB
            if file_size > max_size:
                return f"Error: File too large ({file_size} bytes). Maximum size is {max_size} bytes"

            # Read the file
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                if start_line is not None or end_line is not None:
                    # Read specific lines
                    lines = f.readlines()
                    start_idx = (start_line - 1) if start_line else 0
                    end_idx = end_line if end_line else len(lines)

                    if start_idx < 0 or start_idx >= len(lines):
                        return f"Error: start_line {start_line} is out of range (file has {len(lines)} lines)"

                    selected_lines = lines[start_idx:end_idx]
                    content = "".join(selected_lines)

                    # Add line numbers
                    numbered_lines = []
                    for i, line in enumerate(selected_lines, start=start_idx + 1):
                        numbered_lines.append(f"{i:4d} | {line.rstrip()}")
                    return "\n".join(numbered_lines)
                else:
                    # Read entire file
                    content = f.read()
                    return content

        except PermissionError:
            return f"Error: Permission denied reading '{path}'"
        except Exception as e:
            return f"Error reading file: {str(e)}"

