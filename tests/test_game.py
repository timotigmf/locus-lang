from pathlib import Path

import pytest

from locus.compiler import compile_source
from locus.player import Intent, parse_command
from locus.runtime import Entity, World, instantiate
from locus.stdlib import ROOM, THING, default_kinds, default_relations
from locus.stdlib.authoring import compile_story
from locus.stdlib.game import Session, parse_session_command, start, step
from locus.stdlib.render import render

ROOT = Path(__file__).resolve().parents[1]


def make_session() -> Session:
    source = (ROOT / "examples" / "prima_storia.locus").read_text(encoding="utf-8")
    return start(
        instantiate(compile_source(source, default_kinds(), relations=default_relations()))
    )


@pytest.mark.parametrize(
    ("command", "intent"),
    [
        (" GUARDA ", Intent("look")),
        ("l", Intent("look")),
        ("look", Intent("look")),
        ("inventario", Intent("inventory")),
        ("i", Intent("inventory")),
        ("inv", Intent("inventory")),
        ("nord", Intent("north")),
        ("n", Intent("north")),
        ("sud", Intent("south")),
        ("s", Intent("south")),
        ("est", Intent("east")),
        ("e", Intent("east")),
        ("east", Intent("east")),
        ("ovest", Intent("west")),
        ("o", Intent("west")),
        ("w", Intent("west")),
        ("west", Intent("west")),
        ("nordest", Intent("northeast")),
        ("ne", Intent("northeast")),
        ("northeast", Intent("northeast")),
        ("sudest", Intent("southeast")),
        ("se", Intent("southeast")),
        ("southeast", Intent("southeast")),
        ("sudovest", Intent("southwest")),
        ("so", Intent("southwest")),
        ("southwest", Intent("southwest")),
        ("nordovest", Intent("northwest")),
        ("no", Intent("northwest")),
        ("nw", Intent("northwest")),
        ("northwest", Intent("northwest")),
        ("su", Intent("up")),
        ("alto", Intent("up")),
        ("u", Intent("up")),
        ("up", Intent("up")),
        ("giù", Intent("down")),
        ("giu", Intent("down")),
        ("basso", Intent("down")),
        ("d", Intent("down")),
        ("down", Intent("down")),
        ("dentro", Intent("inward")),
        ("interno", Intent("inward")),
        ("in", Intent("inward")),
        ("inside", Intent("inward")),
        ("fuori", Intent("outward")),
        ("esterno", Intent("outward")),
        ("out", Intent("outward")),
        ("outside", Intent("outward")),
        ("esci", Intent("quit")),
        ("q", Intent("quit")),
        ("prendi chiave", Intent("take", "chiave")),
        ("take the key", Intent("take", "key")),
        ("get chiave", Intent("take", "chiave")),
        ("x custodia", Intent("examine", "custodia")),
        ("examine custodia", Intent("examine", "custodia")),
        ("prendi la chiave", Intent("take", "chiave")),
        ("prendi l’oggetto", Intent("take", "oggetto")),
        ("prendi il caffè", Intent("take", "caffè")),
        ("prendi lo scudo", Intent("take", "scudo")),
        ("prendi la chiave di ottone", Intent("take", "chiave di ottone")),
        ("prendila", Intent("take", "essa")),
        ("esaminalo", Intent("examine", "esso")),
        ("aprila", Intent("open", "essa")),
        ("chiudilo", Intent("close", "esso")),
        ("lasciala", Intent("drop", "essa")),
        ("prendi la", Intent("unknown")),
        ("prendi", Intent("take")),
        ("x", Intent("examine")),
        ("", Intent("unknown")),
        ("raccoglila", Intent("unknown")),
        ("nord sud", Intent("unknown")),
    ],
)
def test_player_parser(command: str, intent: Intent) -> None:
    assert parse_command(command) == intent


def test_complete_solution_transcript_and_replay() -> None:
    commands = [
        "guarda",
        "prendi la chiave",
        "prendi la chiave",
        "inventario",
        "nord",
        "nord",
        "sud",
        "guarda",
        "inventario",
        "esci",
    ]
    expected = [
        "Cucina\nVedi: chiave.",
        "Hai preso: chiave.",
        "Hai già questo oggetto.",
        "Inventario: chiave.",
        "Corridoio\nVedi: nessun oggetto.",
        "Non c'è alcun passaggio in quella direzione.",
        "Cucina\nVedi: nessun oggetto.",
        "Cucina\nVedi: nessun oggetto.",
        "Inventario: chiave.",
        "A presto.",
    ]
    for _ in range(2):
        session = make_session()
        initial = session
        actual = []
        for command in commands:
            result = step(session, parse_command(command))
            session = result.session
            actual.append(render(result))
        assert actual == expected
        assert initial.inventory == ()
        assert session.inventory == ("e3",)
        assert session.room_id == initial.room_id
        assert session.world is not initial.world
        assert len(initial.world.relations) == 3
        assert len(session.world.relations) == 2


def test_absent_and_unreachable_objects_do_not_change_state() -> None:
    session = make_session()
    for command, kind in [
        ("prendi fantasma", "not_here"),
        ("prendi Cucina", "not_portable"),
        ("sud", "no_exit"),
        ("e", "no_exit"),
        ("o", "no_exit"),
        ("ne", "no_exit"),
        ("se", "no_exit"),
        ("so", "no_exit"),
        ("no", "no_exit"),
        ("u", "no_exit"),
        ("d", "no_exit"),
        ("dentro", "no_exit"),
        ("fuori", "no_exit"),
        ("salta", "unknown"),
    ]:
        result = step(session, parse_command(command))
        assert result.event.kind == kind
        assert result.session is session
    north = step(session, Intent("north")).session
    assert step(north, Intent("take", "chiave")).event.kind == "not_here"
    assert render(step(session, Intent("inventory"))) == "Inventario: vuoto."


def test_sessions_are_independent() -> None:
    session = make_session()
    assert step(session, Intent("take", "chiave")).session.inventory
    assert make_session() == session


def test_east_west_movement_and_inverse() -> None:
    world = instantiate(
        compile_source(
            "La Sala è una stanza. La Serra è una stanza. La Serra è a est della Sala.",
            default_kinds(),
            relations=default_relations(),
        )
    )
    current = start(world)
    moved = step(current, parse_command("e"))
    assert moved.event.kind == "look"
    assert next(e.label for e in world.entities if e.id == moved.session.room_id) == "Serra"
    returned = step(moved.session, parse_command("o"))
    assert returned.event.kind == "look"
    assert returned.session.room_id == current.room_id


@pytest.mark.parametrize(
    ("predicate", "outbound", "inbound", "destination"),
    [
        ("nordest", "ne", "so", "Belvedere"),
        ("sudest", "se", "no", "Darsena"),
    ],
)
def test_diagonal_movement_and_inverse(
    predicate: str, outbound: str, inbound: str, destination: str
) -> None:
    world = instantiate(
        compile_source(
            f"La Sala è una stanza. La {destination} è una stanza. "
            f"La {destination} è a {predicate} della Sala.",
            default_kinds(),
            relations=default_relations(),
        )
    )
    current = start(world)
    moved = step(current, parse_command(outbound))
    assert next(e.label for e in world.entities if e.id == moved.session.room_id) == destination
    returned = step(moved.session, parse_command(inbound))
    assert returned.session.room_id == current.room_id


def test_vertical_movement_and_inverse() -> None:
    world = instantiate(
        compile_story(
            "La Sala è una stanza. La Soffitta è una stanza. La Soffitta sovrasta la Sala."
        )
    )
    current = start(world)
    moved = step(current, parse_command("u"))
    assert next(e.label for e in world.entities if e.id == moved.session.room_id) == "Soffitta"
    returned = step(moved.session, parse_command("d"))
    assert returned.session.room_id == current.room_id


def test_inward_outward_movement_and_inverse() -> None:
    world = instantiate(
        compile_story("La Villa è una stanza. L'Atrio è una stanza. La Villa racchiude l'Atrio.")
    )
    current = start(world)
    moved = step(current, parse_command("dentro"))
    assert next(e.label for e in world.entities if e.id == moved.session.room_id) == "Atrio"
    returned = step(moved.session, parse_command("fuori"))
    assert returned.session.room_id == current.room_id


def test_world_without_rooms_compiles_but_cannot_start_game() -> None:
    world = instantiate(compile_source("La chiave è una cosa.", default_kinds()))
    with pytest.raises(ValueError, match="almeno una stanza"):
        start(world)


def test_author_room_container_key_and_thing_types_keep_their_capabilities() -> None:
    source = (
        "Un santuario è un tipo di stanza. "
        "Un reliquiario è un tipo di contenitore. "
        "Una chiave rituale è un tipo di chiave. "
        "Una reliquia è un tipo di cosa. "
        "La Cripta è un santuario. "
        'Inizia nella "Cripta". '
        'La Cripta ha descrizione "Una camera votiva.". '
        "Il cofano è un reliquiario nella Cripta. "
        'Il cofano ha stato "bloccato". '
        "La chiave di bronzo è una chiave rituale nella Cripta. "
        "La chiave di bronzo apre il cofano. "
        "Il rubino è una reliquia nel cofano. "
        'Regola "eco" per prendere "rubino" nella fase dopo: '
        'imposta "descrizione" di "Cripta" a "Il cofano è vuoto."; Fine regola.'
    )
    current = start(instantiate(compile_story(source)))
    assert "Una camera votiva." in render(step(current, parse_command("guarda")))
    current = step(current, parse_command("prendi chiave")).session
    current = step(current, parse_command("apri cofano con chiave")).session
    taken = step(current, parse_command("prendi rubino"))
    assert taken.event.kind == "taken"
    assert "rubino" in render(taken)
    assert "Il cofano è vuoto." in render(step(taken.session, parse_command("guarda")))


def test_unplaced_objects_are_not_accessible() -> None:
    world = instantiate(compile_source("La A è una stanza. La chiave è una cosa.", default_kinds()))
    assert step(start(world), Intent("take", "chiave")).event.kind == "not_here"


def test_ambiguous_intent_on_world_constructed_by_host() -> None:
    world = World(
        (Entity("r", "Sala", ROOM), Entity("a", "chiave", THING), Entity("b", "chiave", THING))
    )
    session = Session(world, "r", ("a", "b"))
    result = step(session, Intent("take", "chiave"))
    assert result.event.kind == "ambiguous"
    assert result.session.inventory == session.inventory
    assert result.session.clarification is not None


def test_partial_name_resolves_only_when_unique_in_current_scope() -> None:
    world = World(
        (
            Entity("r", "Sala", ROOM),
            Entity("a", "chiave di rame", THING),
            Entity("b", "chiave di ferro", THING),
        )
    )
    one_key = Session(world, "r", ("a",))
    taken = step(one_key, parse_command("prendi chiave"))
    assert taken.event.kind == "already_carried"
    assert taken.event.entities == ("a",)

    two_keys = Session(world, "r", ("a", "b"))
    ambiguous = step(two_keys, parse_command("prendi chiave"))
    assert ambiguous.event.kind == "ambiguous"
    assert render(ambiguous) == (
        "Quale intendi? 1) chiave di rame; 2) chiave di ferro. "
        "Rispondi con il numero o il nome, oppure scrivi «annulla»."
    )


def test_ambiguity_can_be_resolved_on_the_next_turn_by_number_or_partial_name() -> None:
    world = World(
        (
            Entity("r", "Sala", ROOM),
            Entity("a", "chiave di rame", THING),
            Entity("b", "chiave di ferro", THING),
        )
    )
    initial = Session(world, "r", ("a", "b"))
    asked = step(initial, parse_session_command(initial, "prendi chiave"))
    assert asked.session.turn == 0
    assert asked.session.clarification is not None

    invalid = step(asked.session, parse_session_command(asked.session, "legno"))
    assert invalid.event.kind == "invalid_clarification"
    assert invalid.session.clarification == asked.session.clarification
    assert invalid.session.turn == 0

    selected = step(invalid.session, parse_session_command(invalid.session, "ferro"))
    assert selected.event.kind == "already_carried"
    assert selected.event.entities == ("b",)
    assert selected.session.clarification is None

    asked_again = step(initial, parse_session_command(initial, "prendi chiave"))
    first = step(asked_again.session, parse_session_command(asked_again.session, "1"))
    assert first.event.kind == "already_carried"
    assert first.event.entities == ("a",)


def test_clarification_can_be_cancelled_or_replaced_by_a_new_command() -> None:
    world = World(
        (
            Entity("r", "Sala", ROOM),
            Entity("a", "chiave di rame", THING),
            Entity("b", "chiave di ferro", THING),
        )
    )
    initial = Session(world, "r", ("a", "b"))
    asked = step(initial, parse_session_command(initial, "prendi chiave"))
    cancelled = step(asked.session, parse_session_command(asked.session, "annulla"))
    assert cancelled.event.kind == "clarification_cancelled"
    assert cancelled.session.clarification is None
    assert cancelled.session.turn == 0

    asked_again = step(initial, parse_session_command(initial, "prendi chiave"))
    looked = step(asked_again.session, parse_session_command(asked_again.session, "guarda"))
    assert looked.event.kind == "look"
    assert looked.session.clarification is None


def test_pronouns_and_clitics_reuse_the_last_direct_object() -> None:
    initial = make_session()
    missing = step(initial, parse_session_command(initial, "prendila"))
    assert missing.event.kind == "no_referent"
    assert missing.session is initial
    assert render(missing) == "Non c'è ancora un oggetto a cui riferire il pronome."

    examined = step(initial, parse_session_command(initial, "esamina chiave"))
    assert examined.session.pronoun_id == examined.event.entities[0]
    looked = step(examined.session, parse_session_command(examined.session, "guarda"))
    assert looked.session.pronoun_id == examined.session.pronoun_id
    taken = step(looked.session, parse_session_command(looked.session, "prendila"))
    assert taken.event.kind == "taken"
    assert taken.event.entities == (examined.session.pronoun_id,)
    dropped = step(taken.session, parse_session_command(taken.session, "drop it"))
    assert dropped.event.kind == "dropped"


def test_disambiguated_object_becomes_the_pronoun_referent() -> None:
    world = World(
        (
            Entity("r", "Sala", ROOM),
            Entity("a", "chiave di rame", THING),
            Entity("b", "chiave di ferro", THING),
        )
    )
    initial = Session(world, "r", ("a", "b"))
    asked = step(initial, parse_session_command(initial, "esamina chiave"))
    selected = step(asked.session, parse_session_command(asked.session, "2"))
    assert selected.event.kind == "examined"
    assert selected.session.pronoun_id == "b"
    again = step(selected.session, parse_session_command(selected.session, "esaminala"))
    assert again.event.entities[0] == "b"


def test_missing_object_gets_a_specific_prompt() -> None:
    assert render(step(make_session(), parse_command("x"))) == (
        "Indica quale oggetto vuoi esaminare o manipolare."
    )


def test_author_synonyms_resolve_in_scope_and_can_be_ambiguous() -> None:
    source = (
        "La Sala è una stanza. La custodia è una cosa nella Sala. "
        "La cassa blu è una cosa nella Sala. "
        'Comprendi "forziere" come "custodia". '
        'Comprendi "cassa rossa" come "custodia". '
        'Comprendi "baule" come "cassa blu".'
    )
    state = start(
        instantiate(compile_source(source, default_kinds(), relations=default_relations()))
    )
    assert step(state, parse_command("x forziere")).event.entities == ("e2",)
    assert step(state, parse_command("prendi baule")).event.entities == ("e3",)
    ambiguous = step(state, parse_command("x cassa"))
    assert ambiguous.event.kind == "ambiguous"
