"""Contratto interno indipendente dalla grammatica italiana."""

from dataclasses import dataclass

IR_VERSION = 2


@dataclass(frozen=True, slots=True)
class EntityIR:
    id: str
    label: str
    type_id: str


@dataclass(frozen=True, slots=True)
class RelationIR:
    source_id: str
    predicate_id: str
    target_id: str


@dataclass(frozen=True, slots=True)
class ProgramIR:
    version: int
    entities: tuple[EntityIR, ...]
    relations: tuple[RelationIR, ...] = ()
