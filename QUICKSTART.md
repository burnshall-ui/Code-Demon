# Code Demon - Quickstart Guide 🔥

Schnellanleitung um Code Demon in 5 Minuten zum Laufen zu bringen.

## Voraussetzungen

- **Python 3.10+** installiert
- **Ollama** installiert und laufend (oder Text Generation WebUI)
- Ein LLM Model geladen (z.B. `gpt-oss:20b`)

## 1. Installation

```bash
cd code-demon
pip install -e .
```

## 2. Ollama Setup

Falls noch nicht installiert:

```bash
# Ollama installieren (macOS)
curl -fsSL https://ollama.com/install.sh | sh

# Model laden (empfohlen)
ollama pull gpt-oss:20b

# Ollama starten (falls nicht automatisch gestartet)
ollama serve
```

## 3. Configuration

Die `.env` Datei ist bereits vorkonfiguriert. Anpassen falls nötig:

```bash
# Standard Config (bereits gesetzt)
LLM_PROVIDER=ollama
OLLAMA_MODEL=gpt-oss:20b
PERSONALITY=cynical
```

## 4. Starten!

```bash
# Als "demon" Command
demon

# Oder mit Python
python -m code_demon

# Mit Optionen
demon --model llama3.1:8b
demon --personality professional
```

## 5. Erste Schritte

Im Chat kannst du direkt loslegen:

```
You: Lies die README.md Datei

You: Zeig mir git status

You: Schreib eine neue Datei test.py mit einem Hello World

You: Führe die Tests aus

You: help        # Zeigt alle Commands
You: stats       # Zeigt Statistiken
You: achievements # Zeigt deine Achievements
You: exit        # Beenden
```

## Beispiel-Session

```text
You: Was ist in diesem Projekt?

Code Demon: [liest package.json und README]
Das ist ein Python-Projekt namens "code-demon" - ein AI Coding Assistant.
Ich sehe TypeScript Dependencies, aber das Projekt ist in Python...
interessante Wahl. Soll ich die Struktur analysieren?

You: Ja, zeig mir die Projektstruktur

Code Demon: [nutzt list_directory rekursiv]
Ok, hier die Struktur... [zeigt Ordner und Files]
```

## Troubleshooting

### Ollama läuft nicht
```bash
# Check Ollama
curl http://localhost:11434/api/tags

# Ollama starten
ollama serve
```

### Model nicht gefunden
```bash
# Models auflisten
ollama list

# Model herunterladen
ollama pull gpt-oss:20b
```

### Python Dependencies fehlen
```bash
pip install -e .
# Oder manuell
pip install -r requirements.txt
```

## Nächste Schritte

- Lies die komplette [README.md](README.md) für alle Features
- Schau dir die [Achievements](code_demon/achievements/definitions.py) an
- Customize die [Personality](code_demon/personality/prompts.py)
- Probiere verschiedene Models aus

## Support

Bei Problemen:
1. Check Ollama Status: `ollama list`
2. Check Python Version: `python --version` (muss 3.10+)
3. Check Dependencies: `pip list`
4. Check Logs: `~/.code-demon/logs/demon.log`

---

**Happy Coding! 🔥**

