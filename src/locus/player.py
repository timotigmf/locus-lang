"""Parser dei comandi: nomi quotati, oggetto diretto e indiretto, nessun frontend autore."""

from collections.abc import Sequence
from dataclasses import dataclass

from locus.diagnostics import canonical
from locus.ir import ActionIR
from locus.schema import separator_variants

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
    "nordest": "northeast",
    "ne": "northeast",
    "northeast": "northeast",
    "sudest": "southeast",
    "se": "southeast",
    "southeast": "southeast",
    "sudovest": "southwest",
    "so": "southwest",
    "southwest": "southwest",
    "nordovest": "northwest",
    "no": "northwest",
    "nw": "northwest",
    "northwest": "northwest",
    "su": "up",
    "alto": "up",
    "u": "up",
    "up": "up",
    "giù": "down",
    "giu": "down",
    "basso": "down",
    "d": "down",
    "down": "down",
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


def standard_commands(
    *,
    include_dialogue: bool = False,
    include_scenes: bool = False,
    include_vehicles: bool = False,
    include_commerce: bool = False,
) -> frozenset[str]:
    dialogue_commands = (
        ("parla", "p", "talk", "scegli", "basta", "fine dialogo") if include_dialogue else ()
    )
    scene_commands = ("punteggio", "score", "turno", "tempo") if include_scenes else ()
    vehicle_commands = (
        ("sali", "entra", "scendi", "board", "enter", "exit") if include_vehicles else ()
    )
    commerce_commands = (
        (
            "compra",
            "acquista",
            "buy",
            "purchase",
            "vendi",
            "vendere",
            "sell",
            "denaro",
            "saldo",
            "money",
            "balance",
        )
        if include_commerce
        else ()
    )
    return frozenset(
        (
            *_SIMPLE_COMMANDS,
            *_ACTION_COMMANDS,
            *dialogue_commands,
            *scene_commands,
            *vehicle_commands,
            *commerce_commands,
        )
    )


def _without_initial_preposition(
    tokens: list[tuple[str, bool]], prepositions: frozenset[str]
) -> list[tuple[str, bool]]:
    if tokens and not tokens[0][1] and tokens[0][0] in prepositions:
        return tokens[1:]
    return tokens


def _vehicle_intent(tokens: list[tuple[str, bool]]) -> Intent | None:
    verb = tokens[0][0]
    if verb in {"sali", "entra", "board", "enter"}:
        rest = tokens[1:]
        if len(rest) >= 2 and rest[:2] == [("a", False), ("bordo", False)]:
            rest = rest[2:]
            rest = _without_initial_preposition(
                rest,
                frozenset({"di", "del", "della", "dello", "dei", "degli", "delle", "dell'"}),
            )
        else:
            rest = _without_initial_preposition(
                rest,
                frozenset(
                    {
                        "in",
                        "nel",
                        "nella",
                        "nello",
                        "nei",
                        "negli",
                        "nelle",
                        "nell'",
                        "su",
                        "sul",
                        "sulla",
                        "sullo",
                        "sui",
                        "sugli",
                        "sulle",
                        "sull'",
                    }
                ),
            )
        return Intent("board", _noun(rest))
    get_out = verb == "get" and len(tokens) >= 2 and tokens[1] == ("out", False)
    if verb in {"scendi", "exit"} or (verb == "esci" and len(tokens) > 1) or get_out:
        rest = tokens[2:] if get_out else tokens[1:]
        rest = _without_initial_preposition(
            rest,
            frozenset(
                {
                    "da",
                    "dal",
                    "dalla",
                    "dallo",
                    "dai",
                    "dagli",
                    "dalle",
                    "dall'",
                    "of",
                    "from",
                }
            ),
        )
        return Intent("exit_vehicle", _noun(rest))
    return None


def _commerce_intent(tokens: list[tuple[str, bool]]) -> Intent | None:
    verb = tokens[0][0]
    if verb in {"denaro", "saldo", "money", "balance"}:
        return Intent("money") if len(tokens) == 1 else Intent("unknown")
    if verb in {"compra", "acquista", "buy", "purchase"}:
        return _commerce_transfer_intent(
            "buy",
            tokens[1:],
            frozenset({"da", "dal", "dalla", "dallo", "dai", "dagli", "dalle", "dall'", "from"}),
        )
    if verb in {"vendi", "vendere", "sell"}:
        return _commerce_transfer_intent(
            "sell",
            tokens[1:],
            frozenset({"a", "ad", "al", "alla", "allo", "ai", "agli", "alle", "all'", "to"}),
        )
    return None


def _commerce_transfer_intent(
    action: str,
    tokens: list[tuple[str, bool]],
    separators: frozenset[str],
) -> Intent:
    splits = [
        index for index, (word, quoted) in enumerate(tokens) if not quoted and word in separators
    ]
    if len(splits) > 1:
        return Intent("unknown")
    if not splits:
        noun = _noun(tokens)
        return Intent(action, noun) if noun else Intent("missing_noun")
    index = splits[0]
    noun = _noun(tokens[:index])
    merchant = _noun(tokens[index + 1 :])
    return Intent(action, noun, merchant) if noun and merchant else Intent("unknown")


def _author_match(
    actions: Sequence[ActionIR], tokens: list[tuple[str, bool]]
) -> tuple[ActionIR, int] | None:
    matches: list[tuple[ActionIR, int]] = []
    for action in actions:
        for command in action.commands:
            words = command.split()
            prefix = tokens[: len(words)]
            if len(prefix) == len(words) and all(
                not quoted and token == word
                for (token, quoted), word in zip(prefix, words, strict=True)
            ):
                matches.append((action, len(words)))
    return matches[0] if len(matches) == 1 else None


def _author_intent(action: ActionIR, tokens: list[tuple[str, bool]], command_length: int) -> Intent:
    rest = tokens[command_length:]
    if action.target_type_id is None:
        return Intent(action.id) if not rest else Intent("unknown")
    if not rest:
        return Intent(action.id)
    if action.indirect_type_id is None:
        direct = _noun(rest)
        return Intent(action.id, direct) if direct else Intent("unknown")
    variants = {
        variant for separator in action.separators for variant in separator_variants(separator)
    }
    splits: list[tuple[int, int]] = []
    for index in range(len(rest)):
        for variant in variants:
            candidate = rest[index : index + len(variant)]
            if len(candidate) == len(variant) and all(
                not quoted and word == expected
                for (word, quoted), expected in zip(candidate, variant, strict=True)
            ):
                splits.append((index, len(variant)))
    if len(splits) != 1:
        return Intent("unknown")
    index, separator_length = splits[0]
    direct = _noun(rest[:index])
    indirect = _noun(rest[index + separator_length :])
    return Intent(action.id, direct, indirect) if direct and indirect else Intent("unknown")


def parse_command(
    text: str,
    actions: Sequence[ActionIR] = (),
    *,
    dialogue_enabled: bool = False,
    scene_enabled: bool = False,
    vehicle_enabled: bool = False,
    commerce_enabled: bool = False,
) -> Intent:
    tokens = _tokens(canonical(text).replace("’", "'"))
    if not tokens:
        return Intent("unknown")
    verb, quoted = tokens[0]
    if quoted:
        return Intent("unknown")
    if vehicle_enabled:
        vehicle = _vehicle_intent(tokens)
        if vehicle is not None:
            return vehicle
    if commerce_enabled:
        commerce = _commerce_intent(tokens)
        if commerce is not None:
            return commerce
    if scene_enabled and len(tokens) == 1:
        if verb in {"punteggio", "score"}:
            return Intent("score")
        if verb in {"turno", "tempo"}:
            return Intent("time")
    if dialogue_enabled:
        if len(tokens) == 1 and verb.isdecimal():
            return Intent("dialogue_choice", verb)
        if verb == "scegli":
            choice = _noun(tokens[1:])
            return Intent("dialogue_choice", choice) if choice else Intent("unknown")
        if verb == "basta" or (
            verb == "fine" and len(tokens) == 2 and tokens[1] == ("dialogo", False)
        ):
            return Intent("end_dialogue")
        if verb in {"parla", "p", "talk"}:
            rest = tokens[1:]
            if rest and not rest[0][1] and rest[0][0] in {"con", "to"}:
                rest = rest[1:]
            direct = _noun(rest)
            return Intent("talk", direct) if direct else Intent("missing_noun")
    authored = _author_match(actions, tokens)
    if len(tokens) == 1:
        standard = _SIMPLE_COMMANDS.get(verb, _ACTION_COMMANDS.get(verb))
        return (
            Intent(standard)
            if standard is not None
            else (
                _author_intent(authored[0], tokens, authored[1])
                if authored is not None
                else Intent("unknown")
            )
        )
    if authored is not None and verb not in _ACTION_COMMANDS and verb not in _SIMPLE_COMMANDS:
        return _author_intent(authored[0], tokens, authored[1])
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
