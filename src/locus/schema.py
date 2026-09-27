"""Schemi di dominio iniettati nel compilatore, indipendenti dalla IF."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

Value = str | int | bool
ValueKind = Literal["numero", "testo", "logico"]
TypeSet = str | tuple[str, ...]
MAX_COMMAND_WORDS = 4


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
    return type(value) is {"numero": int, "testo": str, "logico": bool}[kind]


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


@dataclass(frozen=True, slots=True)
class RelationSpec:
    id: str
    source_type: TypeSet
    target_type: TypeSet
    reverse_operands: bool = False
    inverse_id: str | None = None
    acyclic: bool = False
    verb: str | None = None


@dataclass(frozen=True, slots=True)
class PropertySpec:
    id: str
    owner_types: tuple[str, ...]
    value_kind: ValueKind
    default: Value
    choices: tuple[Value, ...] = ()

    def accepts(self, value: Value) -> bool:
        return valid_value(self.value_kind, value) and (not self.choices or value in self.choices)


@dataclass(frozen=True, slots=True)
class ActionSpec:
    id: str
    min_args: int
    max_args: int
    target_types: tuple[str, ...] = ()
    indirect_types: tuple[str, ...] = ()
