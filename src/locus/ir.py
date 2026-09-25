"""Contratto interno indipendente dalla grammatica italiana."""

from dataclasses import dataclass

IR_VERSION = 1


@dataclass(frozen=True, slots=True)
class EntityIR:
    id: str
    label: str
    type_id: str


@dataclass(frozen=True, slots=True)
class ProgramIR:
    version: int
    entities: tuple[EntityIR, ...]
