"""Vincoli del dominio narrativo, separati dal compilatore generale."""

from locus.graph import cycle_node
from locus.runtime import World, has_type
from locus.schema import Value
from locus.stdlib import (
    CONTAINER,
    DOOR,
    EAST,
    INSIDE,
    LOCATABLE,
    NORTH,
    OPENABLE,
    PORTABLE,
    ROOM,
    SIDE_A,
    SIDE_B,
    SOUTH,
    STATE,
    WEST,
)


class WorldError(ValueError):
    def __init__(self, message: str, entity_id: str) -> None:
        self.entity_id = entity_id
        super().__init__(message)


def property_value(world: World, entity_id: str, property_id: str, default: Value = "") -> Value:
    return next(
        (
            prop.value
            for prop in world.properties
            if prop.entity_id == entity_id and prop.property_id == property_id
        ),
        default,
    )


def validate_world(world: World, inventory: tuple[str, ...] = ()) -> None:
    entities = {entity.id: entity for entity in world.entities}
    if world.entry_id is not None and (
        world.entry_id not in entities
        or not has_type(world, entities[world.entry_id].type_id, ROOM)
    ):
        raise WorldError("Il punto iniziale deve essere una stanza.", world.entry_id)
    parents = {
        edge.source_id: edge.target_id for edge in world.relations if edge.predicate_id == INSIDE
    }
    if len(parents) != sum(edge.predicate_id == INSIDE for edge in world.relations):
        raise WorldError("Un oggetto non può avere due posizioni.", next(iter(parents)))
    cyclic = cycle_node(parents)
    if cyclic is not None:
        raise WorldError("Il contenimento forma un ciclo.", cyclic)
    for child, parent in parents.items():
        if child not in entities or parent not in entities:
            raise WorldError("Il contenimento riferisce un'entità inesistente.", child)
        if not any(
            has_type(world, entities[child].type_id, expected) for expected in LOCATABLE
        ) or not any(
            has_type(world, entities[parent].type_id, expected) for expected in (ROOM, CONTAINER)
        ):
            raise WorldError("Tipi non validi per il contenimento.", child)
    inventory_seen: set[str] = set()
    for ident in inventory:
        if ident not in entities or not any(
            has_type(world, entities[ident].type_id, expected) for expected in PORTABLE
        ):
            raise WorldError("L'inventario contiene un elemento non trasportabile.", ident)
        if ident in parents or ident in inventory_seen:
            raise WorldError("Un oggetto non può avere due posizioni.", ident)
        inventory_seen.add(ident)
    passage_doors: set[frozenset[str]] = set()
    for entity in world.entities:
        if any(has_type(world, entity.type_id, expected) for expected in OPENABLE):
            if property_value(world, entity.id, STATE, "chiuso") not in {
                "aperto",
                "chiuso",
                "bloccato",
            }:
                raise WorldError("Stato di apertura non valido.", entity.id)
        if not has_type(world, entity.type_id, DOOR):
            continue
        sides = {
            edge.predicate_id: edge.target_id
            for edge in world.relations
            if edge.source_id == entity.id and edge.predicate_id in {SIDE_A, SIDE_B}
        }
        if len(sides) != 2 or sides[SIDE_A] == sides[SIDE_B]:
            raise WorldError("Una porta deve collegare due stanze distinte.", entity.id)
        left, right = sides[SIDE_A], sides[SIDE_B]
        if any(
            side not in entities or not has_type(world, entities[side].type_id, ROOM)
            for side in (left, right)
        ):
            raise WorldError("Gli estremi di una porta devono essere stanze.", entity.id)
        pair = frozenset((left, right))
        if pair in passage_doors:
            raise WorldError("Due porte occupano lo stesso passaggio.", entity.id)
        passage_doors.add(pair)
        if not any(
            edge.source_id == left
            and edge.target_id == right
            and edge.predicate_id in {NORTH, SOUTH, EAST, WEST}
            for edge in world.relations
        ):
            raise WorldError(
                "Le stanze della porta devono avere un collegamento direzionale.", entity.id
            )
