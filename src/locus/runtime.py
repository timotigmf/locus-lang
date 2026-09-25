"""Istanziazione minima: il runtime non conosce il linguaggio sorgente."""

from dataclasses import dataclass

from locus.ir import IR_VERSION, ProgramIR, PropertyIR, RelationIR
from locus.schema import PropertySpec


@dataclass(frozen=True, slots=True)
class Entity:
    id: str
    label: str
    type_id: str


@dataclass(frozen=True, slots=True)
class World:
    entities: tuple[Entity, ...]
    relations: tuple[RelationIR, ...] = ()
    property_specs: tuple[PropertySpec, ...] = ()
    properties: tuple[PropertyIR, ...] = ()


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
    specs = {spec.id: spec for spec in program.property_specs}
    if len(specs) != len(program.property_specs):
        raise ValueError("Schemi di proprietà duplicati nell'IR.")
    entities = {entity.id: entity for entity in program.entities}
    seen: set[tuple[str, str]] = set()
    for prop in program.properties:
        key = (prop.entity_id, prop.property_id)
        if key in seen or prop.entity_id not in entities or prop.property_id not in specs:
            raise ValueError("Proprietà duplicata o riferimento assente nell'IR.")
        spec = specs[prop.property_id]
        if entities[prop.entity_id].type_id not in spec.owner_types or not spec.accepts(prop.value):
            raise ValueError("Valore di proprietà non valido nell'IR.")
        seen.add(key)
    return World(
        tuple(Entity(item.id, item.label, item.type_id) for item in program.entities),
        program.relations,
        program.property_specs,
        program.properties,
    )
