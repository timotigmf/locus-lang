"""Istanziazione minima: il runtime non conosce il linguaggio sorgente."""

from dataclasses import dataclass

from locus.ir import IR_VERSION, ProgramIR, RelationIR


@dataclass(frozen=True, slots=True)
class Entity:
    id: str
    label: str
    type_id: str


@dataclass(frozen=True, slots=True)
class World:
    entities: tuple[Entity, ...]
    relations: tuple[RelationIR, ...] = ()


def instantiate(program: ProgramIR) -> World:
    if program.version != IR_VERSION:
        raise ValueError(f"Versione IR non supportata: {program.version}.")
    if len({entity.id for entity in program.entities}) != len(program.entities):
        raise ValueError("Identificatori di entità duplicati nell'IR.")
    identifiers = {entity.id for entity in program.entities}
    if any(
        edge.source_id not in identifiers or edge.target_id not in identifiers
        for edge in program.relations
    ):
        raise ValueError("Riferimento a entità assente nell'IR.")
    keys = {(edge.source_id, edge.predicate_id) for edge in program.relations}
    if len(keys) != len(program.relations):
        raise ValueError("Relazioni duplicate o in conflitto nell'IR.")
    return World(
        tuple(Entity(item.id, item.label, item.type_id) for item in program.entities),
        program.relations,
    )
