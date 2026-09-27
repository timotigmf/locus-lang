"""Vocabolario narrativo sostituibile, esterno al compilatore."""

from locus.schema import ActionSpec, PropertySpec, RelationSpec

ROOM = "mondo.stanza"
THING = "mondo.cosa"
SCENERY = "mondo.scenario"
CONTAINER = "mondo.contenitore"
DOOR = "mondo.porta"
KEY = "mondo.chiave"
PORTABLE = (THING,)
LOCATABLE = (THING, SCENERY)
OPENABLE = (CONTAINER, DOOR)
INSIDE = "mondo.dentro"
NORTH = "mondo.nord"
SOUTH = "mondo.sud"
EAST = "mondo.est"
WEST = "mondo.ovest"
SIDE_A = "mondo.lato_a"
SIDE_B = "mondo.lato_b"
UNLOCKS = "mondo.apre"
STATE = "mondo.stato"
DESCRIPTION = "base.descrizione"
VISIBLE = "mondo.visibile"


def default_kinds() -> dict[str, str]:
    return {
        "stanza": ROOM,
        "cosa": THING,
        "scenario": SCENERY,
        "contenitore": CONTAINER,
        "porta": DOOR,
        "chiave": KEY,
    }


def default_kind_parents() -> dict[str, str | None]:
    return {
        ROOM: None,
        THING: None,
        SCENERY: None,
        CONTAINER: THING,
        DOOR: None,
        KEY: THING,
    }


def default_relations() -> dict[str, RelationSpec]:
    return {
        "nella": RelationSpec(INSIDE, LOCATABLE, (ROOM, CONTAINER), acyclic=True),
        "nord": RelationSpec(
            NORTH, ROOM, ROOM, reverse_operands=True, inverse_id=SOUTH, mutable=True
        ),
        "sud": RelationSpec(
            SOUTH, ROOM, ROOM, reverse_operands=True, inverse_id=NORTH, mutable=True
        ),
        "est": RelationSpec(EAST, ROOM, ROOM, reverse_operands=True, inverse_id=WEST, mutable=True),
        "ovest": RelationSpec(
            WEST, ROOM, ROOM, reverse_operands=True, inverse_id=EAST, mutable=True
        ),
        "collega da": RelationSpec(SIDE_A, DOOR, ROOM),
        "collega a": RelationSpec(SIDE_B, DOOR, ROOM),
        "apre": RelationSpec(UNLOCKS, KEY, OPENABLE, verb="apre"),
    }


def default_properties() -> dict[str, PropertySpec]:
    return {
        "descrizione": PropertySpec(DESCRIPTION, tuple(default_kinds().values()), "testo", ""),
        "stato": PropertySpec(STATE, OPENABLE, "testo", "chiuso", ("aperto", "chiuso", "bloccato")),
        "visibile": PropertySpec(VISIBLE, LOCATABLE, "logico", True),
    }


def default_actions() -> dict[str, ActionSpec]:
    return {
        "guardare": ActionSpec("look", 0, 0),
        "inventariare": ActionSpec("inventory", 0, 0),
        "andare a nord": ActionSpec("north", 0, 0),
        "andare a sud": ActionSpec("south", 0, 0),
        "andare a est": ActionSpec("east", 0, 0),
        "andare a ovest": ActionSpec("west", 0, 0),
        "prendere": ActionSpec("take", 1, 1),
        "aprire": ActionSpec("open", 1, 2),
        "chiudere": ActionSpec("close", 1, 1),
        "mettere": ActionSpec("put", 2, 2),
        "lasciare": ActionSpec("drop", 1, 1),
        "esaminare": ActionSpec("examine", 1, 1),
        "bloccare": ActionSpec("lock", 2, 2),
    }
