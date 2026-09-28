"""Vocabolario narrativo sostituibile, esterno al compilatore."""

from locus.schema import ActionSpec, PropertySpec, RelationSpec

ROOM = "mondo.stanza"
THING = "mondo.cosa"
SCENERY = "mondo.scenario"
PERSON = "mondo.persona"
MERCHANT = "mondo.mercante"
VEHICLE = "mondo.veicolo"
CURRENCY = "mondo.valuta"
MERCHANDISE = "mondo.merce"
CONTAINER = "mondo.contenitore"
DOOR = "mondo.porta"
KEY = "mondo.chiave"
PORTABLE = (THING,)
LOCATABLE = (THING, SCENERY, PERSON, VEHICLE)
OPENABLE = (CONTAINER, DOOR)
INSIDE = "mondo.dentro"
NORTH = "mondo.nord"
SOUTH = "mondo.sud"
EAST = "mondo.est"
WEST = "mondo.ovest"
SIDE_A = "mondo.lato_a"
SIDE_B = "mondo.lato_b"
UNLOCKS = "mondo.apre"
OFFERS = "commercio.vende"
STATE = "mondo.stato"
DESCRIPTION = "base.descrizione"
VISIBLE = "mondo.visibile"
BALANCE = "commercio.saldo"
PRICE = "commercio.prezzo"
RESALE_PRICE = "commercio.rivendita"
MERCHANT_CASH = "commercio.cassa"


def default_kinds() -> dict[str, str]:
    return {
        "stanza": ROOM,
        "cosa": THING,
        "scenario": SCENERY,
        "persona": PERSON,
        "mercante": MERCHANT,
        "veicolo": VEHICLE,
        "valuta": CURRENCY,
        "prodotto": MERCHANDISE,
        "contenitore": CONTAINER,
        "porta": DOOR,
        "chiave": KEY,
    }


def default_kind_parents() -> dict[str, str | None]:
    return {
        ROOM: None,
        THING: None,
        SCENERY: None,
        PERSON: THING,
        MERCHANT: PERSON,
        VEHICLE: None,
        CURRENCY: None,
        MERCHANDISE: THING,
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
        "vende": RelationSpec(
            OFFERS,
            MERCHANDISE,
            MERCHANT,
            reverse_operands=True,
            verb="vende",
            mutable=True,
        ),
    }


def default_properties() -> dict[str, PropertySpec]:
    return {
        "descrizione": PropertySpec(DESCRIPTION, tuple(default_kinds().values()), "testo", ""),
        "stato": PropertySpec(STATE, OPENABLE, "testo", "chiuso", ("aperto", "chiuso", "bloccato")),
        "visibile": PropertySpec(VISIBLE, LOCATABLE, "logico", True),
        "saldo": PropertySpec(BALANCE, (CURRENCY,), "numero", 0),
        "prezzo": PropertySpec(PRICE, (MERCHANDISE,), "numero", 0),
        "prezzo di rivendita": PropertySpec(RESALE_PRICE, (MERCHANDISE,), "numero", 0),
        "cassa": PropertySpec(MERCHANT_CASH, (MERCHANT,), "numero", 0),
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
        "salire": ActionSpec("board", 1, 1, (VEHICLE,)),
        "scendere": ActionSpec("exit_vehicle", 0, 1, (VEHICLE,)),
        "comprare": ActionSpec("buy", 1, 2, (MERCHANDISE,), (MERCHANT,)),
        "vendere": ActionSpec("sell", 1, 2, (MERCHANDISE,), (MERCHANT,)),
    }
