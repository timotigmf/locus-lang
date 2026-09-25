from pathlib import Path

import pytest

from locus.compiler import compile_source
from locus.player import Intent, parse_command
from locus.runtime import Entity, World, instantiate
from locus.stdlib import ROOM, THING, default_kinds, default_relations
from locus.stdlib.game import Session, start, step
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
        ("inventario", Intent("inventory")),
        ("nord", Intent("north")),
        ("sud", Intent("south")),
        ("esci", Intent("quit")),
        ("prendi chiave", Intent("take", "chiave")),
        ("prendi la chiave", Intent("take", "chiave")),
        ("prendi l’oggetto", Intent("take", "oggetto")),
        ("prendi il caffè", Intent("take", "caffè")),
        ("prendi lo scudo", Intent("take", "scudo")),
        ("prendi la chiave di ottone", Intent("take", "chiave di ottone")),
        ("prendi la", Intent("unknown")),
        ("prendi", Intent("unknown")),
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
        "Non puoi andare in quella direzione.",
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


def test_world_without_rooms_compiles_but_cannot_start_game() -> None:
    world = instantiate(compile_source("La chiave è una cosa.", default_kinds()))
    with pytest.raises(ValueError, match="almeno una stanza"):
        start(world)


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
    assert result.session is session
