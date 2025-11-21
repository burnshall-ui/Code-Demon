# Code Demon - Usage Guide

Ausführliche Anleitung für Code Demon mit konkreten Beispielen.

## Installation

```bash
# Clone repository
cd /Users/tomasz/say10/code-demon

# Install in development mode
pip install -e .

# Verify installation
demon --help
```

## Configuration

### Standard Config (.env)

Die `.env.example` Datei zeigt alle verfügbaren Optionen. Kopiere sie zu `.env` und passe an:

```bash
# LLM Provider
LLM_PROVIDER=ollama              # ollama | textgen
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=gpt-oss:20b

# Personality
PERSONALITY=cynical              # cynical | professional | friendly

# Features
REQUIRE_APPROVAL=true            # Approval für destructive actions
ACHIEVEMENTS_ENABLED=true        # Achievement System
HISTORY_ENABLED=true             # Session tracking
```

### CLI Optionen

```bash
# Mit anderem Model
demon --model llama3.1:8b

# Mit anderem Provider
demon --provider textgen

# Mit anderer Personality
demon --personality professional

# Kombiniert
demon --model qwen3-coder:30b --personality cynical
```

## Features

### 1. File Operations

#### Dateien lesen

```text
You: Lies die README.md Datei

You: Zeig mir die ersten 50 Zeilen von main.py

You: Was steht in der config.json?
```

#### Dateien schreiben

```text
You: Schreib eine neue Datei hello.py mit einem Hello World Programm

You: Erstelle eine README.md mit Projekt-Dokumentation
```

#### Dateien editieren

```text
You: Edit main.py und ändere die Variable name von "test" zu "production"

You: Füge einen Kommentar zu Zeile 42 in utils.py hinzu

You: Refactor die Funktion process_data() in app.py
```

#### Dateien suchen

```text
You: Suche nach allen Python-Dateien in diesem Projekt

You: Finde alle Dateien die "TODO" enthalten

You: Zeig mir alle .js Files im src/ Ordner
```

### 2. Git Operations

#### Status & Diff

```text
You: Zeig mir git status

You: Was hat sich geändert?

You: Zeig mir den diff von main.py
```

#### Commit & Push

```text
You: Commit die Änderungen mit Message "fix: resolve bug in login"

You: Stage alle Dateien und commit mit "feat: add new feature"

You: Push zu origin main
```

#### Branches

```text
You: Zeig mir alle Branches

You: Erstelle einen neuen Branch "feature/new-login"

You: Wechsle zu Branch develop
```

### 3. Code Execution

#### Commands ausführen

```text
You: Führe ls -la aus

You: Zeig mir die Python Version

You: Starte den Development Server
```

#### Python Code ausführen

```text
You: Führe diesen Python Code aus: print("Hello World")

You: Teste ob numpy installiert ist
```

#### Tests laufen lassen

```text
You: Führe die pytest Tests aus

You: Run die Tests im tests/ Ordner

You: Zeig mir die Test-Coverage
```

### 4. Web & APIs

#### URLs abrufen

```text
You: Hol den Inhalt von https://example.com

You: Fetch die GitHub API für mein Repository
```

#### API Calls

```text
You: Call die REST API bei http://localhost:3000/api/users

You: POST zu https://api.example.com/data mit {"name": "test"}
```

### 5. Memory & Context

Der Code Demon merkt sich Dinge über mehrere Sessions hinweg (dank Cognee).

#### Automatisches Lernen

Beim Start liest er automatisch `README.md`, `PROJECT_SUMMARY.md` und `QUICKSTART.md` ein.

#### Kontext-Nutzung

Du musst ihm nicht jedes Mal alles neu erklären:

```text
You: Wie war nochmal der Befehl zum Starten?
Code Demon: [Checkt Memory] Laut Doku ist es `demon`.

You: Was steht im Project Summary zu den Achievements?
Code Demon: [Checkt Memory] Es gibt 25+ Achievements in 5 Kategorien...
```

### 6. Commands

#### Spezial-Commands

```text
help          # Zeigt Help
exit / quit   # Beendet Session
clear         # Löscht Conversation
stats         # Zeigt Statistiken
achievements  # Zeigt Achievements
```

## Beispiel-Sessions

### Session 1: Bug Fix

```text
You: Ich habe einen Bug in main.py. Zeig mir die Datei.

Code Demon: [liest main.py]
Ich sehe den Code. Was ist das Problem?

You: Die Funktion calculate_total() gibt falsche Werte zurück.

Code Demon: [analysiert Code]
Ah, Zeile 42: Du addierst statt zu multiplizieren. Soll ich das fixen?

You: Ja bitte.

Code Demon: [editiert Datei]
Fixed. Die Zeile 42 wurde korrigiert. Soll ich die Tests ausführen?

You: Ja.

Code Demon: [führt Tests aus]
Alle Tests passed. Möchtest du committen?

You: Ja, mit Message "fix: correct calculation in total"

Code Demon: [commit]
Committed: fix: correct calculation in total (abc123)
```

### Session 2: Neues Feature

```text
You: Ich möchte ein neues Login-Feature hinzufügen.

Code Demon: Ok. Wo soll ich anfangen? Brauchst du eine neue Datei?

You: Ja, erstelle auth.py mit einer login() Funktion.

Code Demon: [erstellt auth.py]
Fertig. Ich hab eine basic login() Funktion erstellt mit Email/Password validation.
Die Funktion returned True/False und logged errors.

You: Gut. Füge das zu main.py hinzu.

Code Demon: [editiert main.py]
Hab den Import und einen Login-Call hinzugefügt. Willst du das testen?

You: Ja.

Code Demon: [führt Code aus]
Funktioniert. Ready für commit?

You: Ja.

Code Demon: [stages & commits]
✓ Committed: feat: add login functionality
```

### Session 3: Code Review

```text
You: Review den Code in diesem Projekt.

Code Demon: [analysiert Projektstruktur]
Ok, schaue ich mir an...

[liest mehrere Dateien]

Hier meine Findings:
1. main.py: Zu lange Funktionen, solltest du in Module aufteilen
2. utils.py: Keine Type Hints - das würde helfen
3. tests/: Nur 60% Coverage - critical Paths fehlen
4. requirements.txt: Dependencies sind veraltet

Soll ich das priorisieren und anfangen zu fixen?

You: Ja, fang mit den Type Hints an.

Code Demon: [editiert utils.py]
Type Hints zu allen Funktionen hinzugefügt. Next?
```

## Achievements

Du verdienst Achievements während du arbeitest:

### Common

- **First Blood** - Erste Session completed
- **First Tool** - Erstes Tool benutzt
- **First Commit** - Erster Git Commit

### Uncommon

- **Tool Enthusiast** - 10 verschiedene Tools benutzt
- **Night Owl** - 10 Sessions zwischen 00:00-06:00
- **File Editor** - 10 Dateien editiert

### Rare

- **Git Guru** - Alle Git Tools benutzt
- **Code Surgeon** - 100 Dateien editiert
- **Bug Hunter** - 50 Bugs gefixt

### Epic

- **Refactor King** - 100 Refactorings
- **Code Master** - 1000 Zeilen geschrieben

### Legendary

- **Demon Master** - 1000 Tools ausgeführt
- **Immortal** - 365 Tage aktiv

## Personality Types

### Cynical (Standard)

Zynisch, kompetent, mit schwarzem Humor:

```text
You: Warum ist mein Code so langsam?

Code Demon: Lass mich raten: Nested loops in der Datenbank-Query?
Oder gleich die ganze Datenbank in den RAM laden? Zeig's mir.

[analysiert]

Ah ja. Du machst 1000 einzelne Queries in einem Loop.
Das ist... kreativ. Aber falsch. Soll ich das mit einem JOIN fixen?
```

### Professional

Höflich, strukturiert, Best Practices:

```text
You: Wie optimiere ich das?

Code Demon: Gerne! Lass uns den Code zunächst analysieren.

[analysiert]

Ich sehe drei Optimierungsmöglichkeiten:
1. Database Query Batching (höchste Priorität)
2. Caching häufig genutzter Daten
3. Code-Level Optimierung (Algorithmus)

Soll ich mit Option 1 starten?
```

### Friendly

Enthusiastisch, ermutigend, lernorientiert:

```text
You: Ich verstehe das nicht...

Code Demon: Kein Problem! Lass uns das zusammen durchgehen. 😊

[erklärt Schritt für Schritt]

Siehst du? So funktioniert das. Probier's mal aus!
Wenn es klappt, können wir das noch verbessern. 🎉
```

## Tips & Tricks

### 1. Multi-Step Requests

Code Demon kann komplexe Tasks in mehreren Schritten lösen:

```text
You: Analysiere das Projekt, finde Bugs, fixe sie und committe alles.
```

### 2. Context Awareness

Der Agent behält den Context der Conversation:

```text
You: Lies main.py
You: Jetzt editiere Zeile 42    # "Zeile 42" bezieht sich auf main.py
You: Und füge einen Test dafür hinzu    # "dafür" = die Änderung
```

### 3. File Patterns

Du kannst File-Patterns nutzen:

```text
You: Lies alle .py Dateien im src/ Ordner
You: Zeig mir alle Tests
You: Editiere alle Config-Files
```

### 4. Approval System

Destructive Actions benötigen Approval:

```text
You: Lösch alle .tmp Dateien

Code Demon: [Approval Request]
⚠ APPROVAL REQUIRED
Operation: execute_command
Reason: Dangerous operation
Details: command: rm *.tmp

Execute this operation? (y/N):
```

## Troubleshooting

### LLM antwortet nicht

```bash
# Check Ollama
ollama list
ollama serve

# Check Model
ollama pull gpt-oss:20b
```

### Tools funktionieren nicht

```bash
# Check Permissions
chmod +x script.sh

# Check Approval
# Set REQUIRE_APPROVAL=false in .env (nicht empfohlen)
```

### Performance Probleme

```bash
# Kleineres Model verwenden
demon --model llama3.1:8b

# Oder nur CPU
OLLAMA_NUM_GPU=0 ollama serve
```

## Advanced Usage

### Custom System Prompt

Edit `code_demon/personality/prompts.py`:

```python
CUSTOM_PROMPT = """
Dein eigener System Prompt hier...
"""
```

### Custom Tools

Erstelle neue Tools in `code_demon/tools/`:

```python
from ..registry import Tool, ToolMetadata, ToolCategory, ToolParameter

class MyCustomTool(Tool):
    def _define_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="my_tool",
            description="Does something cool",
            category=ToolCategory.CODE,
            parameters=[...],
            requires_approval=False,
        )

    async def execute(self, **kwargs) -> str:
        # Your implementation
        return "Result"
```

Registriere in `__main__.py`:

```python
registry.register(MyCustomTool())
```

---

## Viel Erfolg mit Code Demon! 🔥
