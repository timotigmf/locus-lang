from pathlib import Path

import pytest

from locus.diagnostics import CompileError
from locus.player import Intent, parse_command
from locus.runtime import instantiate
from locus.stdlib import INSIDE, STATE
from locus.stdlib.authoring import compile_story
from locus.stdlib.game import Session, carried, reachable, start, step
from locus.stdlib.render import render
from locus.stdlib.validation import property_value, validate_world

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "porte_e_contenitori.locus"


def session(text: str | None = None) -> Session:
    return start(
        instantiate(
            compile_story(text if text is not None else EXAMPLE.read_text(encoding="utf-8"))
        )
    )


def ident(state: Session, label: str) -> str:
    return next(entity.id for entity in state.world.entities if entity.label == label)


def command(state: Session, text: str, expected: str) -> Session:
    result = step(state, parse_command(text))
    assert result.event.kind == expected, (text, result.event)
    assert render(result)
    validate_world(result.session.world, result.session.inventory)
    return result.session


def test_locked_door_solution_and_bidirectional_state() -> None:
    initial = session()
    state = command(initial, "prendi la chiave di ottone", "not_here")
    state = command(state, "nord", "door_closed")
    state = command(state, "apri lo scrigno", "opened")
    state = command(state, "apri la porta rossa con la chiave di ottone", "not_carried")
    state = command(state, "prendi la chiave di ottone", "taken")
    state = command(state, "prendi la chiave di ferro", "taken")
    state = command(state, "apri la porta rossa con la chiave di ferro", "wrong_key")
    state = command(state, "apri la porta rossa", "locked")
    state = command(state, "apri la porta rossa con la chiave di ottone", "opened")
    state = command(state, "nord", "look")
    state = command(state, "chiudi la porta rossa", "closed")
    state = command(state, "sud", "door_closed")
    state = command(state, "blocca la porta rossa con la chiave di ottone", "lock_success")
    state = command(state, "apri la porta rossa", "locked")
    state = command(state, "apri la porta rossa con la chiave di ottone", "opened")
    state = command(state, "sud", "look")
    assert state.room_id == initial.room_id
    assert initial.inventory == ()
    assert property_value(initial.world, ident(initial, "porta rossa"), STATE) == "bloccato"


def test_closed_container_hides_content_and_open_reveals_it() -> None:
    state = session()
    key = ident(state, "chiave di ottone")
    assert not reachable(state, key)
    assert "chiave di ottone" not in render(step(state, Intent("look")))
    state = command(state, "apri scrigno", "opened")
    assert reachable(state, key)
    assert "chiave di ottone" in render(step(state, parse_command("esamina scrigno")))
    state = command(state, "prendi chiave di ottone", "taken")
    state = command(state, "chiudi scrigno", "closed")
    assert reachable(state, key)


def test_partial_name_requires_disambiguation_when_two_keys_are_reachable() -> None:
    state = command(session(), "apri scrigno", "opened")
    result = step(state, parse_command("prendi chiave"))
    assert result.event.kind == "ambiguous"
    assert render(result) == "Quale intendi: chiave di ottone o chiave di ferro?"


def test_nested_container_transport_put_drop_and_cycle_prevention() -> None:
    state = session(
        "La Sala è una stanza. Il Corridoio è una stanza. Il Corridoio è a nord della Sala. "
        'La borsa è un contenitore nella Sala. La borsa ha stato "aperto". '
        'La scatola è un contenitore nella borsa. La scatola ha stato "aperto". '
        "La gemma è una cosa nella scatola."
    )
    state = command(state, "prendi borsa", "taken")
    assert carried(state, ident(state, "gemma"))
    state = command(state, "metti borsa nella scatola", "cycle")
    state = command(state, "metti borsa nella borsa", "cycle")
    state = command(state, "nord", "look")
    assert reachable(state, ident(state, "gemma"))
    state = command(state, "chiudi borsa", "closed")
    assert not reachable(state, ident(state, "gemma"))
    state = command(state, "prendi gemma", "not_here")
    state = command(state, "apri borsa", "opened")
    state = command(state, "prendi gemma", "taken")
    state = command(state, "metti gemma nella scatola", "put")
    assert ident(state, "gemma") not in state.inventory
    state = command(state, "prendi gemma", "taken")
    state = command(state, "chiudi scatola", "closed")
    state = command(state, "metti gemma nella scatola", "container_closed")
    state = command(state, "lascia gemma", "dropped")
    assert not carried(state, ident(state, "gemma"))
    assert (
        sum(
            e.source_id == ident(state, "gemma") and e.predicate_id == INSIDE
            for e in state.world.relations
        )
        == 1
    )


def test_hidden_key_in_carried_container_cannot_be_used() -> None:
    state = command(session(), "prendi scrigno", "taken")
    assert carried(state, ident(state, "chiave di ottone"))
    state = command(state, "apri porta rossa con chiave di ottone", "not_here")
    state = command(state, "apri scrigno", "opened")
    command(state, "apri porta rossa con chiave di ottone", "opened")


def test_failed_actions_preserve_identity() -> None:
    state = session()
    for text in [
        "prendi chiave di ottone",
        "nord",
        "metti scrigno nello scrigno",
        "apri porta rossa",
        "chiudi Cucina",
        "lascia chiave di ferro",
    ]:
        assert step(state, parse_command(text)).session is state


@pytest.mark.parametrize(
    "source",
    [
        "La A è un contenitore nella B. La B è un contenitore nella A.",
        "La A è un contenitore nella B. La B è un contenitore nella C. "
        "La C è un contenitore nella A.",
    ],
)
def test_compile_rejects_containment_cycles(source: str) -> None:
    with pytest.raises(CompileError, match="E108"):
        compile_story(source)


def test_compile_rejects_double_location() -> None:
    with pytest.raises(CompileError, match="E106"):
        compile_story(
            "La Sala è una stanza. La B è un contenitore. "
            "La X è una cosa nella Sala. La X è nella B."
        )


@pytest.mark.parametrize(
    "source",
    [
        "La Sala è una stanza. La porta è una porta.",
        "La Sala è una stanza. La porta è una porta. La porta collega la Sala alla Sala.",
        "La A è una stanza. La B è una stanza. La porta è una porta. La porta collega la A alla B.",
        "La A è una stanza. La B è una stanza. La B è a nord della A. "
        "La P è una porta. La Q è una porta. La P collega la A alla B. La Q collega la B alla A.",
    ],
)
def test_compile_rejects_invalid_door_topology(source: str) -> None:
    with pytest.raises(CompileError, match="E201"):
        compile_story(source)


@pytest.mark.parametrize(
    ("relation", "movement"),
    [
        ("La Serra è a est della Sala.", "e"),
        ("La Serra è a nordest della Sala.", "ne"),
        ("La Serra sovrasta la Sala.", "u"),
        ("La Sala racchiude la Serra.", "dentro"),
    ],
)
def test_door_can_guard_directional_passages(relation: str, movement: str) -> None:
    state = session(
        "La Sala è una stanza. La Serra è una stanza. "
        f"{relation} La vetrata è una porta. La vetrata collega la Sala alla Serra. "
        'La vetrata ha stato "aperto".'
    )
    assert command(state, movement, "look").room_id != state.room_id


@pytest.mark.parametrize(
    ("text", "intent"),
    [
        ("metti la gemma nello scrigno", Intent("put", "gemma", "scrigno")),
        ("metti la gemma nell'armadio", Intent("put", "gemma", "armadio")),
        (
            'metti "libro con note" nella "scatola nella stanza"',
            Intent("put", "libro con note", "scatola nella stanza"),
        ),
        ("apri porta con la chiave", Intent("open", "porta", "chiave")),
        ("blocca porta con chiave", Intent("lock", "porta", "chiave")),
        ("esamina lo scrigno", Intent("examine", "scrigno")),
        ("lascia la gemma", Intent("drop", "gemma")),
        ("metti gemma", Intent("unknown")),
        ("apri porta con", Intent("unknown")),
        ('prendi "incompleta', Intent("unknown")),
        ("blocca porta", Intent("unknown")),
    ],
)
def test_two_object_parser(text: str, intent: Intent) -> None:
    assert parse_command(text) == intent


def test_quoted_name_escapes_and_apostrophes_match_source() -> None:
    state = session(
        'La Sala è una stanza. La "moneta d’oro" è una cosa nella Sala. '
        'La "chiave \\"rossa\\"" è una cosa nella Sala.'
    )
    state = command(state, "prendi moneta d'oro", "taken")
    command(state, 'prendi "chiave \\"rossa\\""', "taken")


def test_open_close_lock_idempotence_and_failures() -> None:
    state = session()
    state = command(state, "chiudi scrigno", "already_closed")
    state = command(state, "apri scrigno", "opened")
    state = command(state, "apri scrigno", "already_open")
    state = command(state, "blocca scrigno con chiave di ferro", "must_close")
    state = command(state, "prendi chiave di ottone", "taken")
    state = command(state, "metti chiave di ottone nella Cucina", "not_container")
    state = command(state, "apri Cucina", "not_openable")
    command(state, "blocca porta rossa con chiave di ottone", "already_locked")


def test_lockable_container() -> None:
    state = session(
        "La Sala è una stanza. La scatola è un contenitore nella Sala. "
        "La chiave è una chiave nella Sala. La chiave apre la scatola. "
        'La scatola ha stato "bloccato".'
    )
    state = command(state, "apri scatola", "locked")
    state = command(state, "prendi chiave", "taken")
    state = command(state, "apri scatola con chiave", "opened")
    state = command(state, "chiudi scatola", "closed")
    command(state, "blocca scatola con chiave", "lock_success")
