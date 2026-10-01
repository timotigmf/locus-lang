"""Schemi di dominio iniettati nel compilatore, indipendenti dalla IF."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

Scalar = str | int | bool
ListValue = tuple[str, ...] | tuple[int, ...] | tuple[bool, ...]
Value = Scalar | ListValue
ValueKind = Literal[
    "numero",
    "testo",
    "logico",
    "elenco_testi",
    "elenco_numeri",
    "elenco_logici",
]
TypeSet = str | tuple[str, ...]
MAX_COMMAND_WORDS = 4
MAX_SEPARATOR_WORDS = 4

_ARTICULATED_PREPOSITIONS: dict[str, tuple[str, ...]] = {
    "a": ("a", "al", "alla", "allo", "ai", "agli", "alle", "all'"),
    "in": ("in", "nel", "nella", "nello", "nei", "negli", "nelle", "nell'"),
    "di": ("di", "del", "della", "dello", "dei", "degli", "delle", "dell'"),
    "da": ("da", "dal", "dalla", "dallo", "dai", "dagli", "dalle", "dall'"),
    "su": ("su", "sul", "sulla", "sullo", "sui", "sugli", "sulle", "sull'"),
    "con": ("con", "col", "coi"),
}


def type_ids(types: TypeSet) -> tuple[str, ...]:
    return (types,) if isinstance(types, str) else types


def is_subtype(actual: str, expected: str, parents: Mapping[str, str | None]) -> bool:
    """Confronto iterativo; il chiamante convalida prima l'assenza di cicli."""
    current: str | None = actual
    seen: set[str] = set()
    while current is not None and current not in seen:
        if current == expected:
            return True
        seen.add(current)
        current = parents.get(current)
    return False


def valid_value(kind: ValueKind, value: Value) -> bool:
    scalar_types = {"numero": int, "testo": str, "logico": bool}
    if kind in scalar_types:
        return type(value) is scalar_types[kind]
    if type(value) is not tuple:
        return False
    item_type = {
        "elenco_testi": str,
        "elenco_numeri": int,
        "elenco_logici": bool,
    }[kind]
    return all(type(item) is item_type for item in value)


def valid_list_item(kind: ValueKind, value: Value) -> bool:
    item_kinds: dict[ValueKind, ValueKind] = {
        "elenco_testi": "testo",
        "elenco_numeri": "numero",
        "elenco_logici": "logico",
    }
    return kind in item_kinds and valid_value(item_kinds[kind], value)


def valid_command_form(command: str) -> bool:
    words = command.split()
    return 1 <= len(words) <= MAX_COMMAND_WORDS and all(word.isalpha() for word in words)


def command_forms_conflict(commands: tuple[str, ...]) -> bool:
    """Vero se due forme sono uguali o una è prefisso token dell'altra."""
    tokenized = [tuple(command.split()) for command in commands]
    return any(
        left[: len(right)] == right or right[: len(left)] == left
        for index, left in enumerate(tokenized)
        for right in tokenized[index + 1 :]
    )


def valid_separator_form(separator: str) -> bool:
    words = separator.split()
    return 1 <= len(words) <= MAX_SEPARATOR_WORDS and all(word.isalpha() for word in words)


def separator_variants(separator: str) -> tuple[tuple[str, ...], ...]:
    """Espande l'ultima preposizione nelle forme articolate italiane."""
    words = separator.split()
    if not words:
        return ()
    endings = _ARTICULATED_PREPOSITIONS.get(words[-1], (words[-1],))
    return tuple((*words[:-1], ending) for ending in endings)


def separator_forms_conflict(separators: tuple[str, ...]) -> bool:
    variants = tuple(variant for item in separators for variant in separator_variants(item))
    return any(
        left[: len(right)] == right or right[: len(left)] == left
        for index, left in enumerate(variants)
        for right in variants[index + 1 :]
    )


@dataclass(frozen=True, slots=True)
class RelationSpec:
    id: str
    source_type: TypeSet
    target_type: TypeSet
    reverse_operands: bool = False
    inverse_id: str | None = None
    acyclic: bool = False
    verb: str | None = None
    mutable: bool = False
    route_aliases: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class PropertySpec:
    id: str
    owner_types: tuple[str, ...]
    value_kind: ValueKind
    default: Value
    choices: tuple[Value, ...] = ()

    def accepts(self, value: Value) -> bool:
        return valid_value(self.value_kind, value) and (not self.choices or value in self.choices)

    def accepts_item(self, value: Value) -> bool:
        return valid_list_item(self.value_kind, value)


@dataclass(frozen=True, slots=True)
class ActionSpec:
    id: str
    min_args: int
    max_args: int
    target_types: tuple[str, ...] = ()
    indirect_types: tuple[str, ...] = ()
