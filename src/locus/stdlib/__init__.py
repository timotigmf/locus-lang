"""Vocabolario narrativo sostituibile, esterno al compilatore."""

from locus.schema import PropertySpec, RelationSpec

ROOM = "mondo.stanza"
THING = "mondo.cosa"
CONTAINER = "mondo.contenitore"
DOOR = "mondo.porta"
KEY = "mondo.chiave"
PORTABLE = (THING, CONTAINER, KEY)
OPENABLE = (CONTAINER, DOOR)
INSIDE = "mondo.dentro"
NORTH = "mondo.nord"
SOUTH = "mondo.sud"
SIDE_A = "mondo.lato_a"
SIDE_B = "mondo.lato_b"
UNLOCKS = "mondo.apre"
STATE = "mondo.stato"
DESCRIPTION = "base.descrizione"


def default_kinds() -> dict[str, str]:
    return {"stanza": ROOM, "cosa": THING, "contenitore": CONTAINER, "porta": DOOR, "chiave": KEY}


def default_relations() -> dict[str, RelationSpec]:
    return {
        "nella": RelationSpec(INSIDE, PORTABLE, (ROOM, CONTAINER), acyclic=True),
        "nord": RelationSpec(NORTH, ROOM, ROOM, reverse_operands=True, inverse_id=SOUTH),
        "sud": RelationSpec(SOUTH, ROOM, ROOM, reverse_operands=True, inverse_id=NORTH),
        "collega da": RelationSpec(SIDE_A, DOOR, ROOM),
        "collega a": RelationSpec(SIDE_B, DOOR, ROOM),
        "apre": RelationSpec(UNLOCKS, KEY, OPENABLE, verb="apre"),
    }


def default_properties() -> dict[str, PropertySpec]:
    return {
        "descrizione": PropertySpec(DESCRIPTION, tuple(default_kinds().values()), "testo", ""),
        "stato": PropertySpec(STATE, OPENABLE, "testo", "chiuso", ("aperto", "chiuso", "bloccato")),
    }
