"""
Edit File Tool

Search and replace in files
"""

from pathlib import Path
from ..registry import Tool, ToolMetadata, ToolCategory, ToolParameter


class EditFileTool(Tool):
    """Tool to edit files using search and replace"""

    def _define_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="edit_file",
            description="Edit a file by searching for text and replacing it. Supports multi-line search/replace.",
            category=ToolCategory.FILES,
            parameters=[
                ToolParameter(
                    name="path",
                    type="string",
                    description="Path to the file to edit",
                    required=True,
                ),
                ToolParameter(
                    name="search",
                    type="string",
                    description="Text to search for (must be unique in the file)",
                    required=True,
                ),
                ToolParameter(
                    name="replace",
                    type="string",
                    description="Text to replace with",
                    required=True,
                ),
                ToolParameter(
                    name="replace_all",
                    type="boolean",
                    description="Replace all occurrences (default: false, only first match)",
                    required=False,
                    default=False,
                ),
            ],
            requires_approval=True,  # Editing files is destructive
            dangerous=True,
            timeout=10,
        )

    async def execute(
        self, path: str, search: str, replace: str, replace_all: bool = False
    ) -> str:
        """Edit file with search and replace"""
        try:
            file_path = Path(path).expanduser().resolve()

            if not file_path.exists():
                return f"Error: File '{path}' does not exist"

            if not file_path.is_file():
                return f"Error: '{path}' is not a file"

            # Read the file
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Check if search string exists
            if search not in content:
                return f"Error: Search string not found in '{path}'"

            # Count occurrences
            occurrence_count = content.count(search)

            if occurrence_count > 1 and not replace_all:
                return f"Error: Search string appears {occurrence_count} times in the file. Use replace_all=true to replace all occurrences, or make the search string more specific."

            # Perform replacement
            if replace_all:
                new_content = content.replace(search, replace)
            else:
                new_content = content.replace(search, replace, 1)

            # Write back
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            replacements_made = occurrence_count if replace_all else 1

            return f"✓ Successfully replaced {replacements_made} occurrence(s) in '{path}'"

        except PermissionError:
            return f"Error: Permission denied editing '{path}'"
        except Exception as e:
            return f"Error editing file: {str(e)}"

