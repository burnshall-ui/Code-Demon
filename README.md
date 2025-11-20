# Code Demon 🔥

> Ein zynischer, aber extrem kompetenter AI-Agent für Coding und Server-Administration

Ein CLI-basierter AI-Agent ähnlich wie Gemini CLI oder Claude Code, powered by Ollama oder Text Generation WebUI.

## Features

- 🤖 **Multi-LLM Support** - Ollama & Text Generation WebUI
- 📝 **File Operations** - Lesen, Schreiben, Editieren, Suchen
- 🐙 **Git Integration** - Status, Commit, Branch, Push, Diff
- 🔧 **Code Execution** - Run commands, execute code, run tests
- 🌐 **Web Tools** - Search, fetch URLs, API calls
- 🏆 **Achievement System** - Track your progress with gamification
- 🧠 **Memory System** - Langzeitgedächtnis & Kontext-Verständnis dank Cognee
- 📊 **Session History** - Learn from past sessions
- 😈 **Zynische Persönlichkeit** - Schwarzer Humor & okkulte Anspielungen
- 🔒 **Security First** - Approval system für destructive actions

## Quick Start

```bash
# Install
git clone <repo>
cd code-demon
pip install -e .

# Configure
cp .env.example .env
# Edit .env and set your LLM provider

# Run
demon
```

## Architecture

```text
code_demon/
├── core/           # Agent loop, conversation management, LLM providers
├── tools/          # File, Git, Code, Execution, Web tools
├── achievements/   # Gamification system
├── history/        # Session tracking
├── personality/    # System prompts & flavor text
├── core/memory.py  # Memory system integration
├── cli/            # CLI interface
└── config/         # Configuration
```

## Configuration

See `.env.example` for all configuration options.

## License

MIT
# Code-Demon
