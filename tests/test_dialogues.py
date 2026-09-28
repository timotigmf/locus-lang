from dataclasses import replace

import pytest

from locus.diagnostics import CompileError
from locus.ir import IR_VERSION, DialogueChoiceIR, DialogueIR, DialogueNodeIR
from locus.player import parse_command
from locus.runtime import instantiate
from locus.stdlib.authoring import compile_story
from locus.stdlib.game import Session, Transition, start, step
from locus.stdlib.render import render

SOURCE = """
La Sala è una stanza.
La guida è una persona nella Sala.
La sentinella è una persona nella Sala.

Dialogo "segreti del faro" con "guida":
    Nodo "inizio" dice "La guida attende le tue domande.":
        Scelta "Chiedi del faro" porta a "faro".
        Scelta "Saluta e concludi" termina.
    Fine nodo.
    Nodo "faro" dice "Il faro protegge una chiave antica.":
        Scelta "Chiedi della chiave" porta a "chiave".
        Scelta "Torna indietro" porta a "inizio".
    Fine nodo.
    Nodo "chiave" dice "La chiave riposa sotto la campana.":
    Fine nodo.
Fine dialogo.
"""


def command(session: Session, text: str) -> Transition:
    return step(
        session,
        parse_command(text, session.world.actions, dialogue_enabled=bool(session.world.dialogues)),
    )


def test_dialogue_graph_is_lowered_with_stable_references() -> None:
    program = compile_story(SOURCE)
    dialogue = program.dialogues[0]
    assert dialogue.label == "segreti del faro"
    assert dialogue.speaker_id == program.entities[1].id
    assert dialogue.start_node_id == dialogue.nodes[0].id
    assert dialogue.nodes[0].choices[0].target_node_id == dialogue.nodes[1].id
    assert dialogue.nodes[0].choices[1].target_node_id is None


def test_dialogue_accepts_numbers_text_and_tracks_visited_nodes() -> None:
    current = start(instantiate(compile_story(SOURCE)))
    opened = command(current, "parla con guida")
    assert "La guida attende" in render(opened)
    assert "1. Chiedi del faro" in render(opened)
    assert opened.session.dialogue_node_id is not None
    assert opened.dialogue[0].choice_id is None

    lighthouse = command(opened.session, "1")
    assert "protegge una chiave" in render(lighthouse)
    assert lighthouse.dialogue[0].choice_label == "Chiedi del faro"

    key = command(lighthouse.session, "scegli chiave")
    assert render(key) == "La chiave riposa sotto la campana."
    assert key.session.dialogue_id is None
    assert key.dialogue[0].ended
    assert len(key.session.visited_dialogue_nodes) == 3

    repeated = command(key.session, "p guida")
    assert "La guida attende" in render(repeated)
    assert len(repeated.session.visited_dialogue_nodes) == 3


def test_active_dialogue_requires_a_choice_and_can_be_ended() -> None:
    current = start(instantiate(compile_story(SOURCE)))
    opened = command(current, "talk to guida")
    blocked = command(opened.session, "nord")
    assert blocked.session is opened.session
    assert "scegli un'opzione" in render(blocked)
    invalid = command(blocked.session, "scegli novantanove")
    assert invalid.session is opened.session
    assert "Scegli una delle opzioni" in render(invalid)
    ended = command(invalid.session, "fine dialogo")
    assert ended.session.dialogue_id is None
    assert "termina" in render(ended)


def test_people_are_visible_but_not_portable_and_may_lack_dialogue() -> None:
    current = start(instantiate(compile_story(SOURCE)))
    assert "guida" in render(command(current, "guarda"))
    assert "Non puoi prendere" in render(command(current, "prendi guida"))
    assert "non ha ancora un dialogo" in render(command(current, "parla sentinella"))


@pytest.mark.parametrize(
    ("source", "code"),
    [
        (
            SOURCE + 'Dialogo "ALTRO" con "guida": Nodo "x" dice "x": Fine nodo. Fine dialogo.',
            "E118",
        ),
        (
            "La Sala è una stanza. La guida è una persona nella Sala. "
            'Dialogo "vuoto" con "guida": Fine dialogo.',
            "E119",
        ),
        (
            "La Sala è una stanza. La guida è una persona nella Sala. "
            'Dialogo "x" con "guida": Nodo "a" dice "x": '
            'Scelta "vai" porta a "assente". Fine nodo. Fine dialogo.',
            "E119",
        ),
        (
            "La Sala è una stanza. La guida è una persona nella Sala. "
            'Dialogo "x" con "guida": Nodo "a" dice "x": Fine nodo. '
            'Nodo "b" dice "y": Fine nodo. Fine dialogo.',
            "E119",
        ),
        ('La Sala è una stanza. Dialogo "x" con "ignota": Fine dialogo.', "E120"),
        (
            "La Sala è una stanza. La statua è una cosa nella Sala. "
            'Dialogo "x" con "statua": Nodo "a" dice "x": Fine nodo. Fine dialogo.',
            "E120",
        ),
    ],
)
def test_dialogue_diagnostics(source: str, code: str) -> None:
    with pytest.raises(CompileError) as caught:
        compile_story(source, "dialogo.locus")
    assert caught.value.code == code
    assert caught.value.span.source == "dialogo.locus"


def test_runtime_rejects_a_dialogue_with_missing_target() -> None:
    program = compile_story(SOURCE)
    dialogue = program.dialogues[0]
    node = dialogue.nodes[0]
    bad_choice = replace(node.choices[0], target_node_id="assente")
    bad_node = replace(node, choices=(bad_choice, *node.choices[1:]))
    malformed = replace(
        program,
        dialogues=(replace(dialogue, nodes=(bad_node, *dialogue.nodes[1:])),),
    )
    with pytest.raises(ValueError, match="dialogo"):
        instantiate(malformed)


def test_runtime_accepts_a_minimal_generic_dialogue_ir() -> None:
    node = DialogueNodeIR("n1", "inizio", "Ciao.", (DialogueChoiceIR("c1", "Fine", None),))
    dialogue = DialogueIR("d1", "saluto", "e1", "n1", (node,))
    program = compile_story(
        "La Sala è una stanza. La guida è una persona nella Sala. "
        'Dialogo "x" con "guida": '
        'Nodo "a" dice "x": Fine nodo. Fine dialogo.'
    )
    instantiate(replace(program, dialogues=(replace(dialogue, speaker_id="e2"),)))
    assert IR_VERSION == 20
