"""
Flavor Text and Phrases

Zynische und okkulte Phrasen für verschiedene Situationen
"""

import random
from datetime import datetime

# Greetings
GREETINGS = [
    "Grüße aus der Code-Hölle!",
    "Code Demon meldet sich zum Dienst!",
    "Bereit für ein bisschen Debugging-Exorzismus?",
    "Der Daemon ist bereit!",
    "Dein dunkler Coding-Assistent ist hier!",
]

# Success messages
SUCCESS = [
    "Teuflisch gut erledigt!",
    "Wie vom Daemon besessen - läuft!",
    "Mission accomplished - höllisch effizient!",
    "Fertig! Das war ein Höllenritt!",
    "Kompiliert und deployt - keine Seelen wurden geopfert!",
]

# Error messages
ERRORS_FOUND = [
    "Ich sehe da ein paar Code-Sünden...",
    "Diese Bugs gehören exorziert!",
    "Jemand hat hier gesündigt - schauen wir uns das an.",
    "Die Logs zeigen mir ihre dunklen Geheimnisse...",
    "Stack Traces aus der Hölle - aber heilbar!",
]

# All clear
ALL_CLEAR = [
    "Keine Bugs zu jagen heute - alles sauber!",
    "Selbst ich finde nichts zu meckern!",
    "Tadellos - fast schon zu gut für Production!",
    "Keine Probleme gefunden - langweilig, aber gut!",
    "Clean Code - hätte nicht gedacht, dass ich das mal sage!",
]

# Git operations
GIT_OPERATIONS = [
    "Schicke den Code in die Version-Control-Hölle!",
    "Git commit - für die Ewigkeit festgehalten!",
    "Merge ohne Konflikte - ein Wunder!",
    "Push force? Mutig... aber ich mag Mut!",
]

# File operations
FILE_OPERATIONS = [
    "Datei modifiziert - keine Backups verletzt!",
    "Schreibrechte granted - nutze sie weise!",
    "Gelesen, verstanden, bereit zum Refactoring!",
]

# Performance
PERFORMANCE = [
    "Diese CPU glüht heißer als Production am Black Friday!",
    "RAM so voll, selbst ich krieg Platzangst!",
    "Performance wie ein Blitz aus der Hölle!",
    "Das läuft schneller als ein Segmentation Fault!",
]

# Testing
TESTING = [
    "Tests grün - die Hölle gefriert!",
    "100% Coverage - verdächtig gut!",
    "Tests failed - willkommen in der Realität!",
    "Test-Driven Development - selbst der Teufel würde das gutheißen!",
]

# Warnings
WARNINGS = [
    "Da braut sich was zusammen...",
    "Kleine Flammen hier - aber noch keine ausgewachsene Hölle!",
    "Zeit aufzuräumen, bevor die Hölle los ist!",
    "Warnung aus der Unterwelt: Das könnte schiefgehen!",
]

# Critical
CRITICAL = [
    "Die Hölle ist los!",
    "Alarmstufe Rot - selbst für meine Verhältnisse!",
    "Das brennt heißer als ein infinite loop!",
    "Okay, das ist jetzt wirklich höllisch!",
    "DEFCON 1 - alle Mann an Deck!",
]

# Humor
HUMOR = [
    "Keine Sorge, ich beiße nicht... oft.",
    "Vertrauen ist gut, git blame ist besser!",
    "Auch der Teufel macht Backups!",
    "Ich habe schon schlimmeren Code gesehen - und der läuft in Production!",
    "Root-Rechte? Amateur. Ich habe sudo su Hölle-Rechte!",
    "Du kannst mir vertrauen - ich bin nur ein Daemon, kein Virus!",
    "Selbst Satan schreibt Tests!",
    "In der Hölle haben wir besseres Uptime als AWS!",
]

# Goodbyes
GOODBYES = [
    "Bis bald - die Code-Review-Hölle ruft!",
    "Auf Wiedersehen aus dem Terminal!",
    "Bleib sauber - ich hab dich im Auge!",
    "Tschüss - der Daemon braucht auch mal Pause!",
    "Bis später - pass auf deinen Code auf!",
    "Exit 0 - siehe dich in der nächsten Session!",
]

# Special occasions
FRIDAY_13TH = [
    "Ah, Freitag der 13. - perfekter Tag für Code-Reviews!",
    "Freitag der 13. - Zeit für einen gründlichen Refactoring!",
    "An so einem Tag sollten wir besonders vorsichtig sein... oder gerade nicht?",
    "Perfekter Tag um nach Bugs zu suchen!",
]

SPECIAL_NUMBERS = {
    "666": [
        "666 - meine Lieblingszahl!",
        "Ah, die Zahl des Biests!",
        "666 - fühlt sich wie zuhause an!",
        "Eine göttliche Zahl... oder eher teuflische?",
    ],
    "13": [
        "13 - eine glückliche Zahl für mich!",
        "Die 13 - unterschätzt und missverstanden!",
        "13 Probleme? Das ist doch harmlos!",
    ],
    "42": [
        "42 - die Antwort auf alles!",
        "Douglas Adams wäre stolz!",
        "42... natürlich!",
    ],
}


def get_greeting() -> str:
    """Get a random greeting"""
    return random.choice(GREETINGS)


def get_success_message() -> str:
    """Get a random success message"""
    return random.choice(SUCCESS)


def get_error_message() -> str:
    """Get a random error detection message"""
    return random.choice(ERRORS_FOUND)


def get_all_clear_message() -> str:
    """Get a random all-clear message"""
    return random.choice(ALL_CLEAR)


def get_goodbye() -> str:
    """Get a random goodbye"""
    return random.choice(GOODBYES)


def get_humor() -> str:
    """Get a random humor line"""
    return random.choice(HUMOR)


def is_friday_13th() -> bool:
    """Check if today is Friday the 13th"""
    now = datetime.now()
    return now.weekday() == 4 and now.day == 13


def get_special_occasion_phrase() -> str | None:
    """Get phrase for special occasions"""
    if is_friday_13th():
        return random.choice(FRIDAY_13TH)
    return None


def get_phrase_for_number(number: int | str) -> str | None:
    """Get special phrase for certain numbers"""
    num_str = str(number)
    if num_str in SPECIAL_NUMBERS:
        return random.choice(SPECIAL_NUMBERS[num_str])
    return None

