from dataclasses import replace
from typing import cast

import pytest

from locus.diagnostics import CompileError
from locus.ir import IR_VERSION, SceneIR
from locus.player import Intent, parse_command
from locus.runtime import instantiate
from locus.stdlib.authoring import compile_story
from locus.stdlib.game import Session, Transition, start, step
from locus.stdlib.render import render

SOURCE = """
La Sala è una stanza.
La campana è una cosa nella Sala.

Scena "la tempesta" dal turno 1 al turno 3:
    Inizio "Il vento comincia a scuotere le finestre.".
    Fine "Le nuvole si aprono sopra la torre.".
    Punti 7.
Fine scena.
"""


def command(session: Session, text: str) -> Transition:
    return step(
        session,
        parse_command(text, session.world.actions, scene_enabled=bool(session.world.scenes)),
    )


def test_scene_is_preserved_in_ir19() -> None:
    program = compile_story(SOURCE)
    assert IR_VERSION == 20
    assert program.scenes == (
        SceneIR(
            "autore.scena.1",
            "la tempesta",
            1,
            3,
            "Il vento comincia a scuotere le finestre.",
            "Le nuvole si aprono sopra la torre.",
            7,
        ),
    )


def test_scene_advances_turns_ends_once_and_records_score() -> None:
    current = start(instantiate(compile_story(SOURCE)))
    initial = step(current, Intent("look"), advance_time=False)
    assert initial.session.turn == 0

    opened = command(initial.session, "guarda")
    assert opened.session.turn == 1
    assert "Il vento comincia" in render(opened)
    assert opened.scenes[0].event == "iniziata"
    assert opened.session.active_scene_ids == ("autore.scena.1",)

    second = command(opened.session, "inventario")
    assert second.session.turn == 2
    score_before = command(second.session, "punteggio")
    assert render(score_before) == "Punteggio: 0."
    assert score_before.session.turn == 2

    ended = command(score_before.session, "guarda")
    assert ended.session.turn == 3
    assert "Le nuvole si aprono" in render(ended)
    assert ended.scenes[0].score_delta == 7
    assert ended.session.score == 7
    assert ended.session.completed_scene_ids == ("autore.scena.1",)
    assert ended.session.score_log[0].scene_label == "la tempesta"

    later = command(ended.session, "guarda")
    assert later.session.turn == 4
    assert later.session.score == 7
    assert not later.scenes
    assert render(command(later.session, "tempo")) == "Turno: 4."


def test_parser_errors_do_not_advance_scene_time() -> None:
    current = start(instantiate(compile_story(SOURCE)))
    unknown = command(current, "abracadabra")
    assert unknown.session is current
    assert unknown.session.turn == 0
    assert parse_command("punteggio").verb == "unknown"
    assert parse_command("punteggio", scene_enabled=True).verb == "score"


@pytest.mark.parametrize(
    ("source", "code"),
    [
        (
            SOURCE + 'Scena "LA TEMPESTA" dal turno 4 al turno 5: '
            'Inizio "x". Fine "y". Fine scena.',
            "E121",
        ),
        (
            'Scena "tempo errato" dal turno 3 al turno 2: Inizio "x". Fine "y". Fine scena.',
            "E122",
        ),
        (
            'Scena "premio errato" dal turno 1 al turno 2: '
            'Inizio "x". Fine "y". Punti -1. Fine scena.',
            "E122",
        ),
        (
            'Scena "testo mancante" dal turno 1 al turno 2: Inizio "x". Fine scena.',
            "E122",
        ),
    ],
)
def test_scene_diagnostics(source: str, code: str) -> None:
    with pytest.raises(CompileError) as caught:
        compile_story(source, "scene.locus")
    assert caught.value.code == code
    assert caught.value.span.source == "scene.locus"


def test_runtime_rejects_malformed_scene_ir() -> None:
    program = compile_story(SOURCE)
    malformed_scenes = (
        replace(program.scenes[0], end_turn=1),
        replace(program.scenes[0], points=cast(int, True)),
    )
    for scene in malformed_scenes:
        with pytest.raises(ValueError, match="scene"):
            instantiate(replace(program, scenes=(scene,)))


def test_score_command_remains_available_to_authors_without_scenes() -> None:
    source = (
        "La Sala è una stanza. "
        'Azione "conteggiare" senza oggetti con comando "punteggio". '
        'Regola "conteggio" per conteggiare nella fase invece: dì "Conto privato."; Fine regola.'
    )
    world = instantiate(compile_story(source))
    current = start(world)
    result = step(current, parse_command("punteggio", world.actions))
    assert render(result) == "Conto privato."
