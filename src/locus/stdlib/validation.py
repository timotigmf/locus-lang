"""Vincoli del dominio narrativo, separati dal compilatore generale."""

from locus.graph import cycle_node
from locus.runtime import World, has_type
from locus.schema import Value
from locus.stdlib import (
    BALANCE,
    CONTAINER,
    CURRENCY,
    DOOR,
    DOWN,
    EAST,
    INSIDE,
    LOCATABLE,
    MERCHANDISE,
    MERCHANT,
    MERCHANT_CASH,
    NORTH,
    NORTHEAST,
    NORTHWEST,
    OFFERS,
    OPENABLE,
    PERSON,
    PORTABLE,
    PRICE,
    RESALE_PRICE,
    ROOM,
    SIDE_A,
    SIDE_B,
    SOUTH,
    SOUTHEAST,
    SOUTHWEST,
    STATE,
    UP,
    VEHICLE,
    WEST,
)


class WorldError(ValueError):
    def __init__(self, message: str, entity_id: str, code: str = "E201") -> None:
        self.entity_id = entity_id
        self.code = code
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


def integer_property_value(
    world: World,
    entity_id: str,
    property_id: str,
    default: int = 0,
    code: str = "E124",
) -> int:
    value = property_value(world, entity_id, property_id, default)
    if not isinstance(value, int) or isinstance(value, bool):
        raise WorldError("La proprietà commerciale deve essere numerica.", entity_id, code)
    return value


def validate_world(
    world: World,
    inventory: tuple[str, ...] = (),
    owned_ids: tuple[str, ...] = (),
) -> None:
    entities = {entity.id: entity for entity in world.entities}
    if world.entry_id is not None and (
        world.entry_id not in entities
        or not has_type(world, entities[world.entry_id].type_id, ROOM)
    ):
        raise WorldError("Il punto iniziale deve essere una stanza.", world.entry_id)
    parents = {
        edge.source_id: edge.target_id for edge in world.relations if edge.predicate_id == INSIDE
    }
    for dialogue in world.dialogues:
        speaker = entities.get(dialogue.speaker_id)
        if speaker is None or not has_type(world, speaker.type_id, PERSON):
            raise WorldError(
                "Il partecipante di un dialogo deve essere una persona.",
                dialogue.speaker_id,
            )
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
        if has_type(world, entities[child].type_id, VEHICLE) and not has_type(
            world, entities[parent].type_id, ROOM
        ):
            raise WorldError("Un veicolo deve trovarsi direttamente in una stanza.", child, "E123")
    currencies = [entity for entity in world.entities if has_type(world, entity.type_id, CURRENCY)]
    merchandise = [
        entity for entity in world.entities if has_type(world, entity.type_id, MERCHANDISE)
    ]
    merchants = [entity for entity in world.entities if has_type(world, entity.type_id, MERCHANT)]
    if len(currencies) > 1:
        raise WorldError(
            "Questa versione ammette una sola valuta per storia.", currencies[1].id, "E124"
        )
    if merchandise and not currencies:
        raise WorldError(
            "Dichiara una valuta prima di usare oggetti in vendita.",
            merchandise[0].id,
            "E124",
        )
    if merchants and not currencies:
        raise WorldError("Dichiara una valuta prima di usare un mercante.", merchants[0].id, "E125")
    for currency in currencies:
        if integer_property_value(world, currency.id, BALANCE) < 0:
            raise WorldError("Il saldo iniziale non può essere negativo.", currency.id, "E124")
    for item in merchandise:
        if integer_property_value(world, item.id, PRICE) <= 0:
            raise WorldError(
                "Il prezzo di una merce deve essere maggiore di zero.", item.id, "E124"
            )
        if integer_property_value(world, item.id, RESALE_PRICE, code="E125") < 0:
            raise WorldError("Il prezzo di rivendita non può essere negativo.", item.id, "E125")
    for merchant in merchants:
        if integer_property_value(world, merchant.id, MERCHANT_CASH, code="E125") < 0:
            raise WorldError(
                "La cassa di un mercante non può essere negativa.", merchant.id, "E125"
            )
    offers = [edge for edge in world.relations if edge.predicate_id == OFFERS]
    offered_ids = {edge.source_id for edge in offers}
    if len(offered_ids) != len(offers):
        raise WorldError("Una merce può avere un solo mercante.", offers[-1].source_id, "E125")
    if merchants:
        for item in merchandise:
            is_owned = item.id in owned_ids
            is_offered = item.id in offered_ids
            if is_owned == is_offered:
                message = (
                    "Una merce posseduta non può restare nella scorta di un mercante."
                    if is_owned
                    else "Associa ogni merce non posseduta a un mercante con «vende»."
                )
                raise WorldError(message, item.id, "E125")
    for offer in offers:
        offered_item = entities.get(offer.source_id)
        offering_merchant = entities.get(offer.target_id)
        if (
            offered_item is None
            or offering_merchant is None
            or not has_type(world, offered_item.type_id, MERCHANDISE)
            or not has_type(world, offering_merchant.type_id, MERCHANT)
        ):
            raise WorldError("La scorta collega una merce a un mercante.", offer.source_id, "E125")
        if parents.get(offered_item.id) is None or parents.get(offered_item.id) != parents.get(
            offering_merchant.id
        ):
            raise WorldError(
                "La merce e il mercante devono trovarsi direttamente nella stessa stanza.",
                offered_item.id,
                "E125",
            )
        location = parents[offered_item.id]
        if not has_type(world, entities[location].type_id, ROOM):
            raise WorldError(
                "La scorta di un mercante deve trovarsi direttamente in una stanza.",
                offered_item.id,
                "E125",
            )
    inventory_seen: set[str] = set()
    for ident in inventory:
        if (
            ident not in entities
            or has_type(world, entities[ident].type_id, PERSON)
            or not any(has_type(world, entities[ident].type_id, expected) for expected in PORTABLE)
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
            and edge.predicate_id
            in {
                NORTH,
                SOUTH,
                EAST,
                WEST,
                NORTHEAST,
                SOUTHEAST,
                SOUTHWEST,
                NORTHWEST,
                UP,
                DOWN,
            }
            for edge in world.relations
        ):
            raise WorldError(
                "Le stanze della porta devono avere un collegamento direzionale.", entity.id
            )


def validate_session(
    world: World,
    inventory: tuple[str, ...],
    room_id: str,
    vehicle_id: str | None,
    owned_ids: tuple[str, ...] = (),
) -> None:
    validate_world(world, inventory, owned_ids)
    entities = {entity.id: entity for entity in world.entities}
    if len(set(owned_ids)) != len(owned_ids) or any(
        ident not in entities or not has_type(world, entities[ident].type_id, MERCHANDISE)
        for ident in owned_ids
    ):
        raise WorldError("Il registro degli acquisti non è coerente.", owned_ids[0], "E124")
    if any(
        ident in entities
        and has_type(world, entities[ident].type_id, MERCHANDISE)
        and ident not in owned_ids
        for ident in inventory
    ):
        invalid = next(
            ident
            for ident in inventory
            if ident in entities
            and has_type(world, entities[ident].type_id, MERCHANDISE)
            and ident not in owned_ids
        )
        raise WorldError("L'inventario contiene una merce non acquistata.", invalid, "E124")
    if vehicle_id is None:
        return
    vehicle = entities.get(vehicle_id)
    location = next(
        (
            edge.target_id
            for edge in world.relations
            if edge.source_id == vehicle_id and edge.predicate_id == INSIDE
        ),
        None,
    )
    if (
        vehicle is None
        or not has_type(world, vehicle.type_id, VEHICLE)
        or vehicle_id in inventory
        or location != room_id
    ):
        raise WorldError("Lo stato del veicolo guidato non è coerente.", vehicle_id, "E123")
