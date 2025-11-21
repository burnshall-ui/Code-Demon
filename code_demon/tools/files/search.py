"""
Search Files Tool

Search for files and content
"""

import os
import re
from pathlib import Path
from typing import List, Tuple
from ..registry import Tool, ToolMetadata, ToolCategory, ToolParameter


class SearchFilesTool(Tool):
    """Tool to search for files and content"""

    def _define_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="search_files",
            description="Search for files by name or search for text content within files.",
            category=ToolCategory.FILES,
            parameters=[
                ToolParameter(
                    name="path",
                    type="string",
                    description="Directory path to search in",
                    required=True,
                ),
                ToolParameter(
                    name="pattern",
                    type="string",
                    description="Search pattern (filename pattern or text to search for)",
                    required=True,
                ),
                ToolParameter(
                    name="search_type",
                    type="string",
                    description="Type of search: 'filename' or 'content'",
                    required=False,
                    default="filename",
                    enum=["filename", "content"],
                ),
                ToolParameter(
                    name="case_sensitive",
                    type="boolean",
                    description="Case sensitive search",
                    required=False,
                    default=False,
                ),
                ToolParameter(
                    name="max_results",
                    type="number",
                    description="Maximum number of results to return",
                    required=False,
                    default=50,
                ),
            ],
            requires_approval=False,
            dangerous=False,
            timeout=30,
        )

    async def execute(
        self,
        path: str,
        pattern: str,
        search_type: str = "filename",
        case_sensitive: bool = False,
        max_results: int = 50,
    ) -> str:
        """Search for files or content"""
        try:
            search_path = Path(path).expanduser().resolve()

            if not search_path.exists():
                return f"Error: Path '{path}' does not exist"

            if not search_path.is_dir():
                return f"Error: '{path}' is not a directory"

            results: List[str] = []

            if search_type == "filename":
                results = self._search_filenames(
                    search_path, pattern, case_sensitive, max_results
                )
            elif search_type == "content":
                results = self._search_content(
                    search_path, pattern, case_sensitive, max_results
                )
            else:
                return f"Error: Invalid search_type '{search_type}'. Use 'filename' or 'content'"

            if not results:
                return f"No matches found for '{pattern}' in '{path}'"

            result_text = f"Found {len(results)} match(es):\n\n"
            result_text += "\n".join(results)

            if len(results) >= max_results:
                result_text += f"\n\n(Limited to {max_results} results. Refine your search for more.)"

            return result_text

        except Exception as e:
            return f"Error searching: {str(e)}"

    def _search_filenames(
        self, path: Path, pattern: str, case_sensitive: bool, max_results: int
    ) -> List[str]:
        """Search for files by filename pattern"""
        results = []
        flags = 0 if case_sensitive else re.IGNORECASE

        try:
            regex = re.compile(pattern, flags)
        except re.error:
            # If pattern is not a valid regex, treat it as literal text
            pattern_escaped = re.escape(pattern)
            regex = re.compile(pattern_escaped, flags)

        for root, dirs, files in os.walk(path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith(".")]

            for filename in files:
                if regex.search(filename):
                    file_path = Path(root) / filename
                    relative_path = file_path.relative_to(path)
                    results.append(f"📄 {relative_path}")

                    if len(results) >= max_results:
                        return results

        return results

    def _search_content(
        self, path: Path, pattern: str, case_sensitive: bool, max_results: int
    ) -> List[str]:
        """Search for text content within files"""
        results = []
        flags = 0 if case_sensitive else re.IGNORECASE

        try:
            regex = re.compile(pattern, flags)
        except re.error:
            pattern_escaped = re.escape(pattern)
            regex = re.compile(pattern_escaped, flags)

        for root, dirs, files in os.walk(path):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d not in ["node_modules", "__pycache__", "venv", "dist", "build"]
            ]

            for filename in files:
                # Skip binary and large files
                if any(
                    filename.endswith(ext)
                    for ext in [
                        ".pyc",
                        ".so",
                        ".o",
                        ".jpg",
                        ".png",
                        ".gif",
                        ".pdf",
                        ".zip",
                    ]
                ):
                    continue

                file_path = Path(root) / filename

                try:
                    # Check file size
                    if file_path.stat().st_size > 1024 * 1024:  # Skip files > 1MB
                        continue

                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line_num, line in enumerate(f, 1):
                            if regex.search(line):
                                relative_path = file_path.relative_to(path)
                                results.append(
                                    f"📄 {relative_path}:{line_num}: {line.strip()}"
                                )

                                if len(results) >= max_results:
                                    return results
                except (PermissionError, OSError):
                    # Skip files we can't read
                    continue

        return results


class ListDirectoryTool(Tool):
    """Tool to list directory contents"""

    def _define_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="list_directory",
            description="List files and directories in a given path.",
            category=ToolCategory.FILES,
            parameters=[
                ToolParameter(
                    name="path",
                    type="string",
                    description="Directory path to list",
                    required=True,
                ),
                ToolParameter(
                    name="recursive",
                    type="boolean",
                    description="List recursively (show subdirectories)",
                    required=False,
                    default=False,
                ),
                ToolParameter(
                    name="show_hidden",
                    type="boolean",
                    description="Show hidden files (starting with .)",
                    required=False,
                    default=False,
                ),
            ],
            requires_approval=False,
            dangerous=False,
            timeout=10,
        )

    async def execute(
        self, path: str, recursive: bool = False, show_hidden: bool = False
    ) -> str:
        """List directory contents"""
        try:
            dir_path = Path(path).expanduser().resolve()

            if not dir_path.exists():
                return f"Error: Directory '{path}' does not exist"

            if not dir_path.is_dir():
                return f"Error: '{path}' is not a directory"

            results = []

            if recursive:
                for root, dirs, files in os.walk(dir_path):
                    # Filter hidden directories
                    if not show_hidden:
                        dirs[:] = [d for d in dirs if not d.startswith(".")]

                    level = len(Path(root).relative_to(dir_path).parts)
                    indent = "  " * level

                    rel_root = Path(root).relative_to(dir_path)
                    if rel_root != Path("."):
                        results.append(f"{indent}📁 {rel_root.name}/")

                    for filename in sorted(files):
                        if not show_hidden and filename.startswith("."):
                            continue
                        results.append(f"{indent}  📄 {filename}")
            else:
                items = sorted(dir_path.iterdir(), key=lambda x: (not x.is_dir(), x.name))

                for item in items:
                    if not show_hidden and item.name.startswith("."):
                        continue

                    if item.is_dir():
                        results.append(f"📁 {item.name}/")
                    else:
                        size = item.stat().st_size
                        size_str = self._format_size(size)
                        results.append(f"📄 {item.name} ({size_str})")

            if not results:
                return f"Directory '{path}' is empty"

            return "\n".join(results)

        except PermissionError:
            return f"Error: Permission denied accessing '{path}'"
        except Exception as e:
            return f"Error listing directory: {str(e)}"

    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format"""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

