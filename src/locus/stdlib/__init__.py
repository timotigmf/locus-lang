"""Vocabolario narrativo sostituibile, esterno al compilatore."""

from locus.schema import RelationSpec

ROOM = "mondo.stanza"
THING = "mondo.cosa"
INSIDE = "mondo.dentro"
NORTH = "mondo.nord"
SOUTH = "mondo.sud"


def default_kinds() -> dict[str, str]:
    return {"stanza": ROOM, "cosa": THING}


def default_relations() -> dict[str, RelationSpec]:
    return {
        "nella": RelationSpec(INSIDE, THING, ROOM),
        "nord": RelationSpec(NORTH, ROOM, ROOM, reverse_operands=True, inverse_id=SOUTH),
        "sud": RelationSpec(SOUTH, ROOM, ROOM, reverse_operands=True, inverse_id=NORTH),
    }
