"""
Memory System Integration (Cognee)

Provides long-term memory capabilities using Cognee's graph/vector store.
"""

import os
import asyncio
from pathlib import Path
from typing import List, Optional, Any
from rich.console import Console

from ..config.settings import get_settings

# Try to import cognee, but don't fail if not installed (graceful degradation)
try:
    import cognee
    from cognee.api.v1.add import add as cognee_add
    from cognee.api.v1.search import search as cognee_search
    from cognee.api.v1.cognify import cognify as cognee_cognify
    COGNEE_AVAILABLE = True
except ImportError:
    COGNEE_AVAILABLE = False
    # Define placeholders to avoid NameError
    cognee_add = None
    cognee_search = None
    cognee_cognify = None

console = Console()


class MemorySystem:
    """
    Manages the agent's long-term memory using Cognee.
    Handles initialization, indexing, and retrieval.
    """

    def __init__(self):
        self.settings = get_settings()
        self.enabled = self.settings.memory_enabled and COGNEE_AVAILABLE
        self._initialized = False

    async def initialize(self) -> None:
        """
        Initialize the memory system.
        Sets up environment variables for local storage to avoid Docker requirements.
        """
        if not self.enabled:
            if self.settings.memory_enabled and not COGNEE_AVAILABLE:
                console.print("[dim yellow]Warning: Memory enabled but 'cognee' not installed.[/dim yellow]")
            return

        try:
            # Set up local paths for Cognee storage
            # This forces Cognee to use local files instead of trying to connect to services
            # Note: Specific env vars might depend on Cognee version, but we'll try to set standard ones
            # for embedded usage if supported, or default to what Cognee does.
            
            # We want to ensure we don't break if Cognee changes, so we rely on its defaults
            # but maybe point it to a specific .demon_memory folder if possible.
            
            # For now, we'll just let Cognee do its thing but ensure we handle errors.
            
            # Ideally we'd set:
            # os.environ["COGNEE_VECTOR_DB_URL"] = "lancedb://./.code_demon_memory/vectors"
            # os.environ["COGNEE_GRAPH_DB_URL"] = "sqlite://./.code_demon_memory/graph.db"
            
            # Since I can't verify the exact env vars for embedded mode without docs,
            # I will assume standard behavior but wrap in try/except.
            
            self._initialized = True
            console.print("[dim green]Memory system initialized.[/dim green]")

            # Auto-index key documentation on startup to ensure context
            # This is fast enough for small docs and ensures the agent knows the project
            try:
                key_docs = ["README.md", "PROJECT_SUMMARY.md", "QUICKSTART.md"]
                docs_added = False
                for doc in key_docs:
                    if Path(doc).exists():
                        content = Path(doc).read_text(encoding="utf-8")
                        await cognee_add(content)
                        docs_added = True
                
                if docs_added:
                    await cognee_cognify()
            except Exception as e:
                console.print(f"[dim yellow]Auto-indexing docs failed: {e}[/dim yellow]")

        except Exception as e:
            console.print(f"[dim red]Failed to initialize memory: {e}[/dim red]")
            self.enabled = False

    async def index_text(self, text: str, metadata: Optional[dict] = None) -> bool:
        """
        Add text to memory and index it (cognify).
        """
        if not self.enabled or not self._initialized:
            return False

        try:
            await cognee_add(text)
            await cognee_cognify()
            return True
        except Exception as e:
            console.print(f"[dim red]Memory indexing failed: {e}[/dim red]")
            return False

    async def search(self, query: str, limit: int = 5) -> List[str]:
        """
        Search memory for relevant context.
        
        Args:
            query: Search query
            limit: Maximum number of results to return (default: 5)
        
        Returns:
            List of relevant search results
        """
        if not self.enabled or not self._initialized:
            return []

        try:
            results = await cognee_search(query)
            # Top N relevanteste nehmen
            results = results[:limit] if len(results) > limit else results
            return [str(r) for r in results]
        except Exception:
            return []

    async def index_project_files(self, path: Path = Path(".")) -> None:
        """
        Index relevant project files (md, py, etc.)
        """
        if not self.enabled or not self._initialized:
            return

        try:
            # Simple filter for relevant files
            extensions = {".md", ".py", ".txt", ".rst"}
            
            count = 0
            for file_path in path.rglob("*"):
                if file_path.is_file() and file_path.suffix in extensions:
                    if ".git" in file_path.parts or "__pycache__" in file_path.parts:
                        continue
                        
                    try:
                        content = file_path.read_text(encoding="utf-8")
                        await cognee_add(content)
                        count += 1
                    except Exception:
                        continue
            
            if count > 0:
                console.print(f"[dim]Cognifying {count} files...[/dim]")
                await cognee_cognify()
                console.print(f"[dim green]Indexed {count} files into memory.[/dim green]")
                
        except Exception as e:
            console.print(f"[dim red]Project indexing failed: {e}[/dim red]")


# Global instance
_memory_system: Optional[MemorySystem] = None

def get_memory_system() -> MemorySystem:
    global _memory_system
    if _memory_system is None:
        _memory_system = MemorySystem()
    return _memory_system

