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
NORTHEAST = "mondo.nordest"
SOUTHEAST = "mondo.sudest"
SOUTHWEST = "mondo.sudovest"
NORTHWEST = "mondo.nordovest"
UP = "mondo.sopra"
DOWN = "mondo.sotto"
INWARD = "mondo.interno"
OUTWARD = "mondo.esterno"
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
IMAGE = "media.immagine"
SOUND = "media.suono"
ALTERNATIVE_TEXT = "media.testo_alternativo"


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
        "nordest": RelationSpec(
            NORTHEAST,
            ROOM,
            ROOM,
            reverse_operands=True,
            inverse_id=SOUTHWEST,
            mutable=True,
        ),
        "sudest": RelationSpec(
            SOUTHEAST,
            ROOM,
            ROOM,
            reverse_operands=True,
            inverse_id=NORTHWEST,
            mutable=True,
        ),
        "sudovest": RelationSpec(
            SOUTHWEST,
            ROOM,
            ROOM,
            reverse_operands=True,
            inverse_id=NORTHEAST,
            mutable=True,
        ),
        "nordovest": RelationSpec(
            NORTHWEST,
            ROOM,
            ROOM,
            reverse_operands=True,
            inverse_id=SOUTHEAST,
            mutable=True,
        ),
        "sopra": RelationSpec(
            UP,
            ROOM,
            ROOM,
            reverse_operands=True,
            inverse_id=DOWN,
            verb="sovrasta",
            mutable=True,
            route_aliases=("su",),
        ),
        "sotto": RelationSpec(
            DOWN,
            ROOM,
            ROOM,
            reverse_operands=True,
            inverse_id=UP,
            mutable=True,
            route_aliases=("giù", "giu"),
        ),
        "dentro": RelationSpec(
            INWARD,
            ROOM,
            ROOM,
            inverse_id=OUTWARD,
            verb="racchiude",
            mutable=True,
        ),
        "fuori": RelationSpec(
            OUTWARD,
            ROOM,
            ROOM,
            inverse_id=INWARD,
            mutable=True,
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
    all_kinds = tuple(default_kinds().values())
    return {
        "descrizione": PropertySpec(DESCRIPTION, all_kinds, "testo", ""),
        "stato": PropertySpec(STATE, OPENABLE, "testo", "chiuso", ("aperto", "chiuso", "bloccato")),
        "visibile": PropertySpec(VISIBLE, LOCATABLE, "logico", True),
        "saldo": PropertySpec(BALANCE, (CURRENCY,), "numero", 0),
        "prezzo": PropertySpec(PRICE, (MERCHANDISE,), "numero", 0),
        "prezzo di rivendita": PropertySpec(RESALE_PRICE, (MERCHANDISE,), "numero", 0),
        "cassa": PropertySpec(MERCHANT_CASH, (MERCHANT,), "numero", 0),
        "immagine": PropertySpec(IMAGE, all_kinds, "testo", ""),
        "suono": PropertySpec(SOUND, all_kinds, "testo", ""),
        "testo alternativo": PropertySpec(ALTERNATIVE_TEXT, all_kinds, "testo", ""),
    }


def default_actions() -> dict[str, ActionSpec]:
    return {
        "guardare": ActionSpec("look", 0, 0),
        "inventariare": ActionSpec("inventory", 0, 0),
        "andare a nord": ActionSpec("north", 0, 0),
        "andare a sud": ActionSpec("south", 0, 0),
        "andare a est": ActionSpec("east", 0, 0),
        "andare a ovest": ActionSpec("west", 0, 0),
        "andare a nordest": ActionSpec("northeast", 0, 0),
        "andare a sudest": ActionSpec("southeast", 0, 0),
        "andare a sudovest": ActionSpec("southwest", 0, 0),
        "andare a nordovest": ActionSpec("northwest", 0, 0),
        "andare su": ActionSpec("up", 0, 0),
        "andare giù": ActionSpec("down", 0, 0),
        "andare dentro": ActionSpec("inward", 0, 0),
        "andare fuori": ActionSpec("outward", 0, 0),
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
