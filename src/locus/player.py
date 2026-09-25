"""Parser dei comandi: nessuna dipendenza dal frontend autore."""

from dataclasses import dataclass
from typing import Literal

from locus.diagnostics import canonical

Verb = Literal["look", "inventory", "take", "north", "south", "quit", "unknown"]


@dataclass(frozen=True, slots=True)
class Intent:
    verb: Verb
    noun: str | None = None


def parse_command(text: str) -> Intent:
    command = canonical(text).replace("’", "'")
    commands: dict[str, Verb] = {
        "guarda": "look",
        "inventario": "inventory",
        "nord": "north",
        "sud": "south",
        "esci": "quit",
    }
    if command in commands:
        return Intent(commands[command])
    if command.startswith("prendi "):
        noun = command[len("prendi ") :]
        if noun.startswith("l'"):
            noun = noun[2:].strip()
        elif noun.split()[0] in {"il", "lo", "la", "i", "gli", "le"}:
            noun = " ".join(noun.split()[1:])
        if noun:
            return Intent("take", noun)
    return Intent("unknown")
