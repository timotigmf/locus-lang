"""Istanziazione minima: il runtime non conosce il linguaggio sorgente."""

from dataclasses import dataclass

from locus.ir import IR_VERSION, ProgramIR


@dataclass(frozen=True, slots=True)
class Entity:
    id: str
    label: str
    type_id: str


@dataclass(frozen=True, slots=True)
class World:
    entities: tuple[Entity, ...]


def instantiate(program: ProgramIR) -> World:
    if program.version != IR_VERSION:
        raise ValueError(f"Versione IR non supportata: {program.version}.")
    if len({entity.id for entity in program.entities}) != len(program.entities):
        raise ValueError("Identificatori di entità duplicati nell'IR.")
    return World(tuple(Entity(item.id, item.label, item.type_id) for item in program.entities))
