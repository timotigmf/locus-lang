from dataclasses import replace

import pytest

from locus.diagnostics import CompileError
from locus.ir import IR_VERSION
from locus.player import Intent, parse_command
from locus.runtime import has_type, instantiate
from locus.stdlib import INSIDE, VEHICLE
from locus.stdlib.authoring import compile_story
from locus.stdlib.game import Session, Transition, start, step
from locus.stdlib.render import render
from locus.stdlib.validation import WorldError, validate_session

SOURCE = """
La Rimessa è una stanza.
La Piazza è una stanza.
La Piazza è a est della Rimessa.
Una bicicletta da carico è un tipo di veicolo.
La saetta rossa è una bicicletta da carico nella Rimessa.
La saetta rossa ha descrizione "Un telaio rosso con un grande portapacchi.".
"""


def command(session: Session, text: str) -> Transition:
    return step(
        session,
        parse_command(text, session.world.actions, vehicle_enabled=True),
    )


def vehicle_location(session: Session) -> str | None:
    return next(
        (
            edge.target_id
            for edge in session.world.relations
            if edge.source_id == session.vehicle_id and edge.predicate_id == INSIDE
        ),
        None,
    )


def test_vehicle_type_is_lowered_in_ir18() -> None:
    program = compile_story(SOURCE)
    world = instantiate(program)
    vehicle = next(entity for entity in world.entities if entity.label == "saetta rossa")
    assert IR_VERSION == 18
    assert has_type(world, vehicle.type_id, VEHICLE)
    assert any(item.id == VEHICLE and item.parent_id is None for item in program.types)


@pytest.mark.parametrize(
    ("text", "intent"),
    [
        ("sali sulla saetta rossa", Intent("board", "saetta rossa")),
        ("entra nella saetta", Intent("board", "saetta")),
        ("sali a bordo della saetta", Intent("board", "saetta")),
        ("board saetta", Intent("board", "saetta")),
        ("enter the saetta", Intent("board", "saetta")),
        ("scendi", Intent("exit_vehicle")),
        ("scendi dalla saetta", Intent("exit_vehicle", "saetta")),
        ("esci dalla saetta", Intent("exit_vehicle", "saetta")),
        ("get out of the saetta", Intent("exit_vehicle", "saetta")),
        ("exit", Intent("exit_vehicle")),
    ],
)
def test_vehicle_commands(text: str, intent: Intent) -> None:
    assert parse_command(text, vehicle_enabled=True) == intent


def test_vehicle_commands_are_opt_in() -> None:
    assert parse_command("sali sulla bicicletta").verb == "unknown"
    assert parse_command("exit").verb == "unknown"
    assert parse_command("esci").verb == "quit"


def test_board_move_and_disembark_move_vehicle_atomically() -> None:
    current = start(instantiate(compile_story(SOURCE)))
    boarded = command(current, "sali sulla saetta")
    assert boarded.event.kind == "boarded"
    assert "salito a bordo" in render(boarded)
    assert boarded.session.vehicle_id == boarded.event.entities[0]
    assert vehicle_location(boarded.session) == current.room_id

    moved = command(boarded.session, "e")
    assert moved.event.kind == "look"
    assert moved.session.room_id == vehicle_location(moved.session)
    assert "Sei a bordo di: saetta rossa." in render(moved)
    assert "saetta rossa" not in render(moved).split("Vedi: ", 1)[1]

    left = command(moved.session, "scendi dalla saetta")
    assert left.event.kind == "disembarked"
    assert left.session.vehicle_id is None
    vehicle_id = left.event.entities[0]
    assert any(
        edge.source_id == vehicle_id
        and edge.predicate_id == INSIDE
        and edge.target_id == moved.session.room_id
        for edge in left.session.world.relations
    )

    returned = command(left.session, "o")
    assert returned.session.room_id == current.room_id
    assert command(returned.session, "entra nella saetta").event.kind == "not_here"


def test_vehicle_errors_are_specific_and_do_not_corrupt_state() -> None:
    source = SOURCE + "La campana è una cosa nella Rimessa. La mula è un veicolo nella Rimessa."
    current = start(instantiate(compile_story(source)))
    assert command(current, "scendi").event.kind == "not_in_vehicle"
    assert command(current, "sali sulla campana").event.kind == "not_vehicle"
    assert command(current, "prendi saetta").event.kind == "not_portable"

    boarded = command(current, "entra nella saetta")
    assert command(boarded.session, "sali sulla saetta").event.kind == "already_aboard"
    assert command(boarded.session, "sali sulla mula").event.kind == "already_in_vehicle"
    assert command(boarded.session, "scendi dalla mula").event.kind == "wrong_vehicle"
    validate_session(
        boarded.session.world,
        boarded.session.inventory,
        boarded.session.room_id,
        boarded.session.vehicle_id,
    )


def test_vehicle_must_be_directly_in_a_room() -> None:
    source = (
        "La Rimessa è una stanza. "
        "Il cassone è un contenitore nella Rimessa. "
        "La bicicletta è un veicolo nel cassone."
    )
    with pytest.raises(CompileError) as caught:
        compile_story(source, "veicolo.locus")
    assert caught.value.code == "E123"
    assert caught.value.span.source == "veicolo.locus"


def test_session_validation_rejects_vehicle_in_another_room() -> None:
    current = start(instantiate(compile_story(SOURCE)))
    boarded = command(current, "sali sulla saetta").session
    other_room = next(
        entity.id
        for entity in boarded.world.entities
        if entity.id != boarded.room_id and entity.label == "Piazza"
    )
    with pytest.raises(WorldError, match="veicolo guidato"):
        invalid = replace(boarded, room_id=other_room)
        validate_session(invalid.world, invalid.inventory, invalid.room_id, invalid.vehicle_id)


def test_vehicle_actions_participate_in_rules() -> None:
    source = (
        SOURCE
        + 'Regola "partenza" per salire "saetta rossa" nella fase dopo: '
        + 'dì "Il campanello squilla."; Fine regola. '
        + 'Regola "arrivo" per scendere nella fase dopo: '
        + 'dì "Appoggi il cavalletto."; Fine regola.'
    )
    current = start(instantiate(compile_story(source)))
    boarded = command(current, "sali sulla saetta")
    assert "Il campanello squilla." in render(boarded)
    left = command(boarded.session, "scendi")
    assert "Appoggi il cavalletto." in render(left)


def test_author_can_use_vehicle_words_when_story_has_no_vehicle() -> None:
    source = (
        "La Sala è una stanza. "
        'Azione "varcare" senza oggetti con comando "entra". '
        'Regola "varco" per varcare nella fase invece: dì "Attraversi il varco."; Fine regola.'
    )
    world = instantiate(compile_story(source))
    current = start(world)
    result = step(current, parse_command("entra", world.actions))
    assert render(result) == "Attraversi il varco."


def test_vehicle_commands_are_reserved_when_a_vehicle_exists() -> None:
    with pytest.raises(CompileError) as caught:
        compile_story(
            "La Sala è una stanza. La barca è un veicolo nella Sala. "
            'Azione "varcare" senza oggetti con comando "entra".'
        )
    assert caught.value.code == "E311"
