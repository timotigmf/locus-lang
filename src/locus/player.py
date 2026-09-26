"""Parser dei comandi: nomi quotati, oggetto diretto e indiretto, nessun frontend autore."""

from dataclasses import dataclass
from typing import Literal

from locus.diagnostics import canonical

Verb = Literal[
    "look",
    "inventory",
    "take",
    "north",
    "south",
    "quit",
    "unknown",
    "open",
    "close",
    "put",
    "drop",
    "examine",
    "lock",
]

_SIMPLE_COMMANDS: dict[str, Verb] = {
    "guarda": "look",
    "l": "look",
    "look": "look",
    "inventario": "inventory",
    "i": "inventory",
    "inv": "inventory",
    "inventory": "inventory",
    "nord": "north",
    "n": "north",
    "north": "north",
    "sud": "south",
    "s": "south",
    "south": "south",
    "esci": "quit",
    "q": "quit",
    "quit": "quit",
}

_ACTION_COMMANDS: dict[str, Verb] = {
    "prendi": "take",
    "get": "take",
    "take": "take",
    "apri": "open",
    "open": "open",
    "chiudi": "close",
    "close": "close",
    "metti": "put",
    "put": "put",
    "lascia": "drop",
    "drop": "drop",
    "esamina": "examine",
    "examine": "examine",
    "x": "examine",
    "blocca": "lock",
    "lock": "lock",
}


@dataclass(frozen=True, slots=True)
class Intent:
    verb: Verb
    noun: str | None = None
    indirect: str | None = None


def _tokens(text: str) -> list[tuple[str, bool]] | None:
    tokens: list[tuple[str, bool]] = []
    index = 0
    while index < len(text):
        if text[index].isspace():
            index += 1
            continue
        if text[index] == '"':
            index += 1
            quoted: list[str] = []
            while index < len(text) and text[index] != '"':
                if text[index] == "\\":
                    index += 1
                    if index >= len(text) or text[index] not in '\\"':
                        return None
                quoted.append(text[index])
                index += 1
            if index == len(text) or not "".join(quoted).strip():
                return None
            tokens.append(("".join(quoted), True))
            index += 1
        else:
            end = index
            while end < len(text) and not text[end].isspace() and text[end] != '"':
                end += 1
            word = text[index:end]
            if word.startswith("nell'"):
                tokens.append(("nell'", False))
                if word[5:]:
                    tokens.append((word[5:], False))
            else:
                tokens.append((word, False))
            index = end
    return tokens


def _noun(tokens: list[tuple[str, bool]]) -> str | None:
    if tokens and not tokens[0][1]:
        first = tokens[0][0]
        if first in {"il", "lo", "la", "i", "gli", "le", "the"}:
            tokens = tokens[1:]
        elif first.startswith("l'"):
            tokens = ([(first[2:], False)] if first[2:] else []) + tokens[1:]
    return " ".join(token for token, _ in tokens) or None


def parse_command(text: str) -> Intent:
    tokens = _tokens(canonical(text).replace("’", "'"))
    if not tokens:
        return Intent("unknown")
    verb, quoted = tokens[0]
    if quoted:
        return Intent("unknown")
    if len(tokens) == 1:
        return Intent(_SIMPLE_COMMANDS.get(verb, _ACTION_COMMANDS.get(verb, "unknown")))
    if verb not in _ACTION_COMMANDS:
        return Intent("unknown")
    action = _ACTION_COMMANDS[verb]
    rest = tokens[1:]
    delimiters = (
        {"in", "into", "nel", "nella", "nello", "nell'"} if action == "put" else {"con", "with"}
    )
    splits = [i for i, (word, quoted) in enumerate(rest) if not quoted and word in delimiters]
    indirect = None
    if action in {"put", "open", "lock"} and splits:
        if len(splits) != 1:
            return Intent("unknown")
        index = splits[0]
        indirect = _noun(rest[index + 1 :])
        direct = _noun(rest[:index])
        if not indirect or not direct:
            return Intent("unknown")
    else:
        direct = _noun(rest)
    if not direct or (action in {"put", "lock"} and not indirect):
        return Intent("unknown")
    return Intent(action, direct, indirect)
