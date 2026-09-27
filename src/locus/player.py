"""Parser dei comandi: nomi quotati, oggetto diretto e indiretto, nessun frontend autore."""

from collections.abc import Sequence
from dataclasses import dataclass

from locus.diagnostics import canonical
from locus.ir import ActionIR

Verb = str

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
    "est": "east",
    "e": "east",
    "east": "east",
    "ovest": "west",
    "o": "west",
    "w": "west",
    "west": "west",
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
            if word.startswith(("nell'", "all'", "dell'", "dall'", "sull'")):
                prefix = word[:5]
                tokens.append((prefix, False))
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


def standard_commands() -> frozenset[str]:
    return frozenset((*_SIMPLE_COMMANDS, *_ACTION_COMMANDS))


def _author_intent(action: ActionIR, tokens: list[tuple[str, bool]]) -> Intent:
    rest = tokens[1:]
    if action.target_type_id is None:
        return Intent(action.id) if not rest else Intent("unknown")
    if not rest:
        return Intent(action.id)
    if action.indirect_type_id is None:
        direct = _noun(rest)
        return Intent(action.id, direct) if direct else Intent("unknown")
    separator_words: set[str] = set()
    articulated = {
        "a": {"a", "al", "alla", "allo", "ai", "agli", "alle", "all'"},
        "in": {"in", "nel", "nella", "nello", "nei", "negli", "nelle", "nell'"},
        "di": {"di", "del", "della", "dello", "dei", "degli", "delle", "dell'"},
        "da": {"da", "dal", "dalla", "dallo", "dai", "dagli", "dalle", "dall'"},
        "su": {"su", "sul", "sulla", "sullo", "sui", "sugli", "sulle", "sull'"},
        "con": {"con", "col", "coi"},
    }
    for separator in action.separators:
        separator_words.update(articulated.get(separator, {separator}))
    splits = [
        index for index, (word, quoted) in enumerate(rest) if not quoted and word in separator_words
    ]
    if len(splits) != 1:
        return Intent("unknown")
    index = splits[0]
    direct = _noun(rest[:index])
    indirect = _noun(rest[index + 1 :])
    return Intent(action.id, direct, indirect) if direct and indirect else Intent("unknown")


def parse_command(text: str, actions: Sequence[ActionIR] = ()) -> Intent:
    tokens = _tokens(canonical(text).replace("’", "'"))
    if not tokens:
        return Intent("unknown")
    verb, quoted = tokens[0]
    if quoted:
        return Intent("unknown")
    authored = next((action for action in actions if verb in action.commands), None)
    if len(tokens) == 1:
        standard = _SIMPLE_COMMANDS.get(verb, _ACTION_COMMANDS.get(verb))
        return (
            Intent(standard)
            if standard is not None
            else (_author_intent(authored, tokens) if authored is not None else Intent("unknown"))
        )
    if authored is not None and verb not in _ACTION_COMMANDS:
        return _author_intent(authored, tokens)
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
