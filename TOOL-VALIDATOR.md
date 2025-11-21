# Tool Validator System

## Overview

Code Demon includes an intelligent **Tool Validator** that prevents and corrects LLM tool hallucination through smart error handling and suggestions.

## How It Works

When an LLM attempts to use a non-existent tool, the validator:

1. **Detects the invalid tool** name
2. **Finds similar tools** using fuzzy string matching (SequenceMatcher)
3. **Returns helpful suggestions** with descriptions
4. **Educates the LLM** with clear error messages

## Features

### 🎯 Fuzzy String Matching
- Uses `difflib.SequenceMatcher` for similarity scoring
- Boosts substring matches (e.g., "search" matches "search_files")
- Returns top 3 most similar tools

### 📚 Smart Suggestions
When a tool doesn't exist, the LLM receives:
```
Tool 'repo_browser.search' does not exist.

Did you mean one of these?
  • search_files - Search for files by name, pattern, or content
  • list_directory - List contents of a directory
  • read_file - Read the contents of a file

IMPORTANT: Only use tools that actually exist. Do not invent tool names.
```

### 🔄 Feedback Loop
The LLM learns from these error messages and self-corrects in subsequent tool calls.

### 📋 Fallback Mode
If no similar tools are found (similarity < 0.4), the validator lists all available tools organized by category:

```
files: read_file, write_file, edit_file, search_files, list_directory
git: git_status, git_commit, git_add, git_diff, ...
execution: execute_command, run_python, run_tests
web: fetch_url, call_api, web_search
```

## Implementation

### Core Algorithm

```python
def _find_similar_tools(self, tool_name: str, max_suggestions: int = 3) -> List[str]:
    """Find similar tool names using fuzzy string matching"""
    similarities = []

    for available_tool in self._tools.keys():
        # Calculate similarity ratio
        ratio = SequenceMatcher(None, tool_name.lower(), available_tool.lower()).ratio()

        # Boost substring matches
        if tool_name.lower() in available_tool.lower() or available_tool.lower() in tool_name.lower():
            ratio += 0.3

        similarities.append((available_tool, ratio))

    # Sort and return top matches
    similarities.sort(key=lambda x: x[1], reverse=True)
    return [name for name, score in similarities[:max_suggestions] if score > 0.4]
```

### Integration

The validator is integrated into `ToolRegistry.execute_tool()`:
- No changes needed in agent code
- Works automatically for all tool calls
- Error messages are returned to LLM as tool results

## Benefits

### For Users
- ✅ Fewer failed tool calls
- ✅ Better user experience
- ✅ Clear error messages

### For the LLM
- ✅ Learns correct tool names through feedback
- ✅ Self-corrects in conversation
- ✅ Reduces hallucination over time

### For Developers
- ✅ Easy to extend with new tools
- ✅ No special handling needed
- ✅ Works with any LLM provider

## Configuration

No configuration needed! The Tool Validator works automatically.

### Adjustable Parameters

If you want to tune the validator, modify in `tools/registry.py`:

```python
def _find_similar_tools(self, tool_name: str, max_suggestions: int = 3):
    # max_suggestions: Number of suggestions to return (default: 3)
    # similarity threshold: Current 0.4 (line 184)
    # substring boost: Current 0.3 (line 176)
```

## Testing

The Tool Validator is most effective with:
- Models prone to hallucination (gpt-oss:20b, smaller models)
- Natural language queries
- Ambiguous requests

Test by asking the agent to use non-existent tools and observe the self-correction.

## Future Enhancements

Potential improvements:
- [ ] Learn from user corrections
- [ ] Context-aware suggestions (file tools vs git tools)
- [ ] Typo correction (e.g., "git_staus" → "git_status")
- [ ] Tool usage history to prioritize common tools
