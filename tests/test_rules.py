from dataclasses import replace
from pathlib import Path
from typing import cast

import pytest

from locus.diagnostics import CompileError
from locus.player import parse_command
from locus.rule_model import ActionCall, Address, RelationChange, RelationEdge, TableChange
from locus.rules import ActionResult, Execution, execute
from locus.runtime import instantiate
from locus.schema import Scalar, Value
from locus.stdlib.authoring import compile_story
from locus.stdlib.game import Session, start, step
from locus.stdlib.render import render
from locus.stdlib.validation import property_value

BASE = """La Sala è una stanza.
La leva è una cosa nella Sala.
Lo scrigno è un contenitore nella Sala.
La attiva è una proprietà logica.
La punti è una proprietà numerica.
""".replace("I punti", "La punti")

AUTHOR_ACTIONS = """
Una persona è un tipo di cosa.
Il custode è una persona nella Sala.
Il sigillo è una cosa nella Sala.
Azione "attendere" senza oggetti con comando "attendi" e sinonimo "aspetta".
Azione "salutare" su una persona con comando "saluta" e sinonimo "riverisci".
Azione "mostrare" su una cosa con una persona con comando "mostra"
    e sinonimo "esibisci" e sinonimo "fai vedere"
    e separatore "a" e separatore "verso".
Regola "attesa" per attendere nella fase invece: dì "Il tempo passa."; Fine regola.
Regola "saluto" per salutare "custode" nella fase invece:
    dì "Il custode ricambia il saluto.";
Fine regola.
Regola "mostra sigillo" per mostrare "sigillo" con "custode" nella fase invece:
    dì "Il custode riconosce il sigillo.";
Fine regola.
"""


def rule(
    body: str, phase: str = "prima", name: str = "prova", action: str = "guardare", extra: str = ""
) -> str:
    return f'Regola "{name}" per {action} nella fase {phase} {extra}: {body} Fine regola.\n'


def session(source: str) -> Session:
    return start(instantiate(compile_story(BASE + source)))


def points(state: Session) -> int:
    entity = next(e for e in state.world.entities if e.label == "leva")
    spec = next(p for p in state.world.property_specs if p.id.endswith("punti"))
    value = property_value(state.world, entity.id, spec.id)
    assert type(value) is int
    return value


def clues(state: Session) -> tuple[str, ...]:
    entity = next(e for e in state.world.entities if e.label == "leva")
    spec = next(p for p in state.world.property_specs if p.id.endswith("indizi"))
    value = property_value(state.world, entity.id, spec.id)
    assert type(value) is tuple and all(type(item) is str for item in value)
    return cast(tuple[str, ...], value)


def test_priority_order_and_continue() -> None:
    source = (
        rule('dì "A";', name="a")
        + rule('dì "B"; continua;', name="b", extra="priorità 20")
        + rule('dì "C";', name="c")
    )
    result = step(session(source), parse_command("guarda"))
    assert render(result).startswith("B\nA\nC\nSala")
    assert [t.name for t in result.trace] == ["b", "a", "c"]
    assert result.trace[0].origin.line > 1


@pytest.mark.parametrize(
    "condition,expected",
    [
        ("vero o falso e falso", True),
        ("(vero o falso) e falso", False),
        ("non falso e vero", True),
        ('"punti" di "leva" è almeno 0', True),
        ('"punti" di "leva" è maggiore di 0', False),
        ('"punti" di "leva" è minore di 1', True),
        ('"punti" di "leva" è al massimo 0', True),
        ('"punti" di "leva" è diverso da 0', False),
    ],
)
def test_conditions(condition: str, expected: bool) -> None:
    result = step(
        session(rule('dì "segnale";', extra="quando " + condition)), parse_command("guarda")
    )
    assert ("segnale" in render(result)) is expected
    assert result.trace[0].condition is expected


def test_mutation_and_interruption() -> None:
    source = rule('aumenta "punti" di "leva" di 3; diminuisci "punti" di "leva" di 1; interrompi;')
    initial = session(source)
    result = step(initial, parse_command("guarda"))
    assert points(result.session) == 2
    assert points(initial) == 0
    assert result.event.kind == "rule"


def test_typed_list_mutation_membership_and_single_removal() -> None:
    source = "La indizi è una proprietà elenco di testi."
    source += rule(
        'aggiungi "orma" a "indizi" di "leva"; '
        'aggiungi "fibra" a "indizi" di "leva"; '
        'aggiungi "orma" a "indizi" di "leva";',
        name="raccogli",
    )
    source += rule(
        'rimuovi "orma" da "indizi" di "leva";',
        phase="dopo",
        name="scarta",
        extra='quando "indizi" di "leva" contiene "fibra"',
    )
    source += rule(
        'dì "Resta un\'orma.";',
        phase="descrivi",
        name="verifica indizio",
        extra='quando "indizi" di "leva" contiene "orma"',
    )
    result = step(session(source), parse_command("guarda"))
    assert clues(result.session) == ("fibra", "orma")
    assert "Resta un'orma." in render(result)


def test_list_mutation_rolls_back_with_rule_failure() -> None:
    source = "La indizi è una proprietà elenco di testi."
    source += rule('aggiungi "orma" a "indizi" di "leva"; fallisci "Indagine annullata";')
    initial = session(source)
    result = step(initial, parse_command("guarda"))
    assert result.session is initial
    assert clues(result.session) == ()
    assert render(result) == "Indagine annullata"


@pytest.mark.parametrize("phase", ["prima", "verifica", "esegui", "dopo", "descrivi"])
def test_failure_rolls_back_all_phases(phase: str) -> None:
    source = rule(
        'aumenta "punti" di "leva" di 5; dì "da scartare";',
        name="prepara",
        action='prendere "leva"',
        extra="priorità 10",
    )
    source += rule('fallisci "Negato";', phase=phase, action='prendere "leva"')
    initial = session(source)
    result = step(initial, parse_command("prendi leva"))
    assert result.session is initial
    assert render(result) == "Negato"


def test_default_action_failure_rolls_back() -> None:
    initial = session(rule('aumenta "punti" di "leva" di 5;', action="andare a nord"))
    result = step(initial, parse_command("nord"))
    assert result.session is initial
    assert result.event.kind == "no_exit"


def test_instead_and_description() -> None:
    initial = session(
        rule('dì "Personalizzato";', phase="invece") + rule('dì "Dopo";', phase="dopo", name="dopo")
    )
    assert render(step(initial, parse_command("guarda"))) == "Personalizzato\nDopo"
    initial = session(rule('dì "Panorama";', phase="descrivi"))
    assert render(step(initial, parse_command("guarda"))) == "Panorama"
    initial = session(rule('dì "Premessa"; continua;', phase="invece"))
    assert render(step(initial, parse_command("guarda"))).startswith("Premessa\nSala")


def test_replacement_and_cycle() -> None:
    initial = session(rule('sostituisci con prendere "leva";'))
    result = step(initial, parse_command("guarda"))
    assert result.event.kind == "taken"
    assert len(result.session.inventory) == 1
    initial = session(rule('aumenta "punti" di "leva" di 1; sostituisci con guardare;'))
    result = step(initial, parse_command("guarda"))
    assert result.session is initial
    assert "ciclica" in render(result)


@pytest.mark.parametrize(
    "literal,value", [("vero", True), ("falso", False), ("0", 0), ('"risposta"', "risposta")]
)
def test_typed_return(literal: str, value: str | int | bool) -> None:
    result = step(session(rule(f"restituisci {literal};")), parse_command("guarda"))
    assert type(result.result) is type(value)
    assert result.result == value


def test_selector_and_missing_target() -> None:
    initial = session(rule('fallisci "Protetta";', action='prendere "leva"'))
    assert render(step(initial, parse_command("prendi leva"))) == "Protetta"
    assert step(initial, parse_command("apri scrigno")).event.kind == "opened"
    assert not step(initial, parse_command("prendi assente")).trace


def test_author_actions_with_zero_one_and_two_typed_objects() -> None:
    current = session(AUTHOR_ACTIONS)

    def run(command: str) -> str:
        intent = parse_command(command, current.world.actions)
        return render(step(current, intent))

    assert run("attendi") == "Il tempo passa."
    assert run("aspetta") == "Il tempo passa."
    assert run("saluta il custode") == "Il custode ricambia il saluto."
    assert run("riverisci il custode") == "Il custode ricambia il saluto."
    assert run("mostra il sigillo al custode") == "Il custode riconosce il sigillo."
    assert run("esibisci il sigillo verso il custode") == "Il custode riconosce il sigillo."
    assert run("fai vedere il sigillo al custode") == "Il custode riconosce il sigillo."
    assert run("saluta sigillo") == "Questo comando non si applica a quell'elemento."
    assert run("mostra custode a sigillo") == "Questo comando non si applica a quell'elemento."
    assert parse_command("mostra sigillo", current.world.actions).verb == "unknown"


def test_author_action_without_rules_has_an_explicit_default() -> None:
    current = session('Azione "meditare" senza oggetti con comando "medita".')
    result = step(current, parse_command("medita", current.world.actions))
    assert render(result) == "Non accade nulla."
    assert result.event.kind == "custom"


def test_multiword_zero_object_action_consumes_the_complete_form() -> None:
    current = session(
        'Azione "tacere" senza oggetti con comando "fai silenzio" '
        'e sinonimo "resta immobile". '
        'Regola "silenzio" per tacere nella fase invece: dì "Tutto tace."; Fine regola.'
    )
    for command in ("fai silenzio", "resta immobile"):
        assert render(step(current, parse_command(command, current.world.actions))) == "Tutto tace."
    assert parse_command("fai", current.world.actions).verb == "unknown"
    assert parse_command("fai silenzio ora", current.world.actions).verb == "unknown"


def test_author_action_expands_italian_articulated_separators() -> None:
    source = """
Una persona è un tipo di cosa.
Il custode è una persona nella Sala.
L'amuleto è una cosa nella Sala.
Azione "parlare" su una persona con una cosa con comando "parla"
    e separatore "di" e separatore "su".
Regola "racconto" per parlare "custode" con "amuleto" nella fase invece:
    dì "Il custode ascolta il racconto.";
Fine regola.
"""
    current = session(source)
    for command in ("parla custode dell'amuleto", "parla custode sull'amuleto"):
        assert render(step(current, parse_command(command, current.world.actions))) == (
            "Il custode ascolta il racconto."
        )


def test_author_action_accepts_multiword_separators() -> None:
    source = """
La moneta è una cosa nella Sala.
La chiave di vetro è una cosa nella Sala.
Azione "scambiare" su una cosa con una cosa con comando "scambia"
    e separatore "in cambio di" e separatore "insieme a".
Regola "baratto" per scambiare "moneta" con "chiave di vetro" nella fase invece:
    dì "Lo scambio è concluso.";
Fine regola.
"""
    current = session(source)
    for command in (
        "scambia moneta in cambio della chiave di vetro",
        "scambia moneta insieme alla chiave di vetro",
    ):
        assert render(step(current, parse_command(command, current.world.actions))) == (
            "Lo scambio è concluso."
        )
    assert parse_command("scambia moneta in chiave di vetro", current.world.actions).verb == (
        "unknown"
    )


def test_replacement_can_invoke_an_author_action() -> None:
    source = AUTHOR_ACTIONS + rule(
        'sostituisci con salutare "custode";',
        name="delega saluto",
    )
    current = session(source)
    result = step(current, parse_command("guarda", current.world.actions))
    assert render(result) == "Il custode ricambia il saluto."


@pytest.mark.parametrize(
    "source,code",
    [
        (rule('dì "x";') * 2, "E301"),
        (rule('dì "x";', action="volare"), "E303"),
        (rule('imposta "ignota" di "leva" a 1;'), "E304"),
        (rule('imposta "punti" di "leva" a vero;'), "E305"),
        (rule('dì "x";', extra='quando "attiva" di "leva" è maggiore di vero'), "E305"),
        (rule("sostituisci con prendere;"), "E306"),
        (rule('imposta "punti" di "leva" a 1;', phase="verifica"), "E307"),
        (rule('continua; dì "x";'), "E308"),
        (rule('dì "x";', extra="priorità 1000001"), "E309"),
        (rule('dì "x";', extra="quando " + "non " * 66 + "vero"), "E302"),
        (rule('crea relazione "ignota" da "Sala" a "Sala";'), "E312"),
        (rule('crea relazione a senso unico "ignota" da "Sala" a "Sala";'), "E312"),
        (rule('crea relazione "nella" da "leva" a "Sala";'), "E312"),
        (rule('crea relazione "nord" da "leva" a "Sala";'), "E305"),
        (rule('crea relazione "nord" da "Sala" a "Sala";'), "E312"),
        (rule('aggiungi "x" a "punti" di "leva";'), "E313"),
        (
            "La indizi è una proprietà elenco di testi." + rule('aggiungi 1 a "indizi" di "leva";'),
            "E313",
        ),
        (
            "La indizi è una proprietà elenco di testi."
            + rule('dì "x";', extra='quando "indizi" di "leva" contiene 1'),
            "E313",
        ),
        (
            "La indizi è una proprietà elenco di testi."
            + rule('aggiungi "x" a "indizi" di "leva";', phase="verifica"),
            "E307",
        ),
        (
            rule('crea relazione "nord" da "Sala" a "Sala";', phase="verifica"),
            "E307",
        ),
    ],
)
def test_static_errors(source: str, code: str) -> None:
    with pytest.raises(CompileError) as caught:
        compile_story(BASE + source, "regole.locus")
    assert caught.value.code == code
    assert caught.value.span.source == "regole.locus"


@pytest.mark.parametrize(
    ("source", "code"),
    [
        (
            'Azione "salutare" senza oggetti con comando "saluta". '
            'Azione "SALUTARE" senza oggetti con comando "inchina".',
            "E310",
        ),
        ('Azione "parlare con" senza oggetti con comando "parla".', "E310"),
        ('Azione "salutare" senza oggetti con comando "guarda".', "E311"),
        ('Azione "riporre" senza oggetti con comando "mettila".', "E311"),
        ('Azione "riporre" senza oggetti con comando "metticela".', "E311"),
        ('Azione "riporre" senza oggetti con comando "mettici".', "E311"),
        (
            'Azione "salutare" senza oggetti con comando "saluta". '
            'Azione "inchinarsi" senza oggetti con comando "saluta".',
            "E311",
        ),
        ('Azione "salutare" senza oggetti con comando "di-buon-giorno".', "E311"),
        (
            'Azione "salutare" senza oggetti con comando "saluta" e sinonimo "x".',
            "E311",
        ),
        (
            'Azione "salutare" senza oggetti con comando "saluta" e sinonimo "SALUTA".',
            "E311",
        ),
        (
            'Azione "tacere" senza oggetti con comando "fai" e sinonimo "fai silenzio".',
            "E311",
        ),
        ('Azione "osservare" senza oggetti con comando "guarda bene".', "E311"),
        (
            'Azione "tacere" senza oggetti con comando "questa forma contiene cinque parole".',
            "E311",
        ),
        (
            'Azione "salutare" senza oggetti con comando "saluta" e separatore "a".',
            "E311",
        ),
        (
            "Una persona è un tipo di cosa. "
            'Azione "mostrare" su una cosa con una persona con comando "mostra" '
            'e separatore "a" e separatore "A".',
            "E311",
        ),
        (
            'Azione "scambiare" su una cosa con una cosa con comando "scambia" '
            'e separatore "in" e separatore "in cambio di".',
            "E311",
        ),
        (
            'Azione "scambiare" su una cosa con una cosa con comando "scambia" '
            'e separatore "a" e separatore "al posto di".',
            "E311",
        ),
        (
            'Azione "scambiare" su una cosa con una cosa con comando "scambia" '
            'e separatore "con una locuzione di cinque parole".',
            "E311",
        ),
        (
            "Una persona è un tipo di cosa. "
            'Azione "mostrare" su una cosa con una persona con comando "mostra".',
            "E311",
        ),
        ('Azione "domare" su un drago con comando "doma".', "E102"),
        (
            "Una persona è un tipo di cosa. Il custode è una persona nella Sala. "
            'Azione "salutare" su una persona con comando "saluta". '
            'Regola "errata" per salutare "leva" nella fase invece: dì "x"; Fine regola.',
            "E305",
        ),
    ],
)
def test_author_action_diagnostics(source: str, code: str) -> None:
    with pytest.raises(CompileError) as caught:
        compile_story(BASE + source, "azioni.locus")
    assert caught.value.code == code


@pytest.mark.parametrize(
    "source",
    [
        rule('dì "x"'),
        rule(""),
        rule('dì "x";').replace("Fine regola.", ""),
        rule('dì "x";', phase="ignota"),
        rule('dì "x";', extra="quando (vero"),
        'Azione "salutare" senza oggetti con comando "saluta" e alternativa "ciao".',
    ],
)
def test_syntax_errors(source: str) -> None:
    with pytest.raises(CompileError):
        compile_story(BASE + source)


def test_engine_works_without_narrative_state() -> None:
    class CounterHost:
        def read(self, state: int, address: Address) -> int:
            return state

        def write(self, state: int, address: Address, value: Value) -> int:
            assert type(value) is int
            return value

        def relate(self, state: int, change: RelationChange, present: bool) -> int:
            return state

        def rows(self, state: int, table_id: str) -> tuple[tuple[Scalar, ...], ...]:
            return ()

        def change_table(self, state: int, change: TableChange, present: bool) -> int:
            return state

        def perform(self, state: int, action: ActionCall) -> ActionResult[int, str]:
            return ActionResult(state + 1, True, ("eseguita",))

    compiled = compile_story(BASE + rule('aumenta "punti" di "leva" di 5;'))
    custom = replace(compiled.rules[0], selector=ActionCall("incremento"))
    result: Execution[int, str] = execute(10, ActionCall("incremento"), (custom,), CounterHost())
    assert result.state == 16
    assert result.outputs == ("eseguita",)


def test_transcript_replay() -> None:
    from pathlib import Path

    compiled = compile_story(Path("examples/regole.locus").read_text(encoding="utf-8"))

    def replay() -> tuple[Session, list[str], list[str]]:
        current = start(instantiate(compiled))
        outputs: list[str] = []
        names: list[str] = []
        for command in [
            "apri scrigno",
            "esamina leva",
            "apri scrigno",
            "prendi gemma",
            "lascia gemma",
            "prendi gemma",
        ]:
            transition = step(current, parse_command(command))
            current = transition.session
            outputs.append(render(transition))
            names.extend(t.name for t in transition.trace)
        return current, outputs, names

    first = replay()
    assert first == replay()
    assert first[1][0] == "La serratura resiste. Esamina la leva."
    assert "dieci punti" in first[1][3]
    assert "dieci punti" not in first[1][-1]


def test_replacement_failure_rolls_back_parent() -> None:
    source = rule('aumenta "punti" di "leva" di 4; sostituisci con andare a nord;')
    initial = session(source)
    result = step(initial, parse_command("guarda"))
    assert result.session is initial
    assert result.event.kind == "no_exit"


def test_runtime_write_error_rolls_back() -> None:
    from locus.rule_model import Effect

    initial = session(rule('imposta "stato" di "scrigno" a "aperto";'))
    original = initial.world.rules[0]
    invalid = replace(
        original, effects=(Effect("imposta", "impossibile", original.effects[0].address),)
    )
    initial = replace(initial, world=replace(initial.world, rules=(invalid,)))
    result = step(initial, parse_command("guarda"))
    assert result.session is initial
    assert result.trace[-1].outcome == "errore con ripristino"


def test_secret_passage_adds_and_removes_both_directions() -> None:
    source = """
La Cripta è una stanza.
Azione "sigillare" senza oggetti con comando "sigilla varco".
Regola "rivela il passaggio" per esaminare "leva" nella fase dopo:
    crea relazione "nord" da "Sala" a "Cripta";
    dì "La parete scorre e rivela un passaggio.";
Fine regola.
Regola "sigilla il passaggio" per sigillare nella fase invece:
    rimuovi relazione "nord" da "Sala" a "Cripta";
    dì "La parete torna al suo posto.";
Fine regola.
"""
    initial = session(source)
    assert step(initial, parse_command("nord")).event.kind == "no_exit"

    revealed = step(initial, parse_command("esamina leva"))
    assert "rivela un passaggio" in render(revealed)
    assert len(revealed.session.world.relations) == len(initial.world.relations) + 2
    in_crypt = step(revealed.session, parse_command("nord"))
    assert in_crypt.session.room_id != revealed.session.room_id
    returned = step(in_crypt.session, parse_command("sud"))
    assert returned.session.room_id == revealed.session.room_id

    repeated = step(returned.session, parse_command("esamina leva"))
    assert repeated.session.world.relations == returned.session.world.relations
    hidden = step(
        repeated.session,
        parse_command("sigilla varco", repeated.session.world.actions),
    )
    assert len(hidden.session.world.relations) == len(initial.world.relations)
    assert step(hidden.session, parse_command("nord")).event.kind == "no_exit"


def test_secret_one_way_passage_changes_only_the_requested_arc() -> None:
    source = """
La Cripta è una stanza.
Azione "sigillare" senza oggetti con comando "sigilla varco".
Regola "rivela la caduta" per esaminare "leva" nella fase dopo:
    crea relazione a senso unico "nord" da "Sala" a "Cripta";
Fine regola.
Regola "sigilla la caduta" per sigillare nella fase invece:
    rimuovi relazione a senso unico "nord" da "Sala" a "Cripta";
Fine regola.
"""
    initial = session(source)
    revealed = step(initial, parse_command("esamina leva"))
    assert len(revealed.session.world.relations) == len(initial.world.relations) + 1
    moved = step(revealed.session, parse_command("nord"))
    assert moved.session.room_id != revealed.session.room_id
    assert step(moved.session, parse_command("sud")).event.kind == "no_exit"

    hidden = step(
        moved.session,
        parse_command("sigilla varco", moved.session.world.actions),
    )
    assert hidden.session.world.relations == initial.world.relations


def test_dynamic_one_way_route_alias_is_structured_in_ir() -> None:
    compiled = compile_story(
        BASE
        + """
La Cripta è una stanza.
Regola "apri la botola" per esaminare "leva" nella fase dopo:
    crea relazione a senso unico "giù" da "Sala" a "Cripta";
Fine regola.
"""
    )
    change = compiled.rules[0].effects[0].relation
    assert change is not None
    assert change.edges == (RelationEdge("e1", "mondo.sotto", "e4"),)


def test_one_way_removal_preserves_the_opposite_arc() -> None:
    initial = session(
        """
La Cripta è una stanza.
La Cripta è a nord della Sala.
Regola "blocca la salita" per esaminare "leva" nella fase dopo:
    rimuovi relazione a senso unico "nord" da "Sala" a "Cripta";
Fine regola.
"""
    )
    changed = step(initial, parse_command("esamina leva"))
    triples = {
        (edge.source_id, edge.predicate_id, edge.target_id)
        for edge in changed.session.world.relations
    }
    assert ("e1", "mondo.nord", "e4") not in triples
    assert ("e4", "mondo.sud", "e1") in triples


def test_relation_change_rolls_back_on_failure_and_conflict() -> None:
    source = """
La Cripta è una stanza.
Regola "apri e annulla" per esaminare "leva" nella fase dopo:
    crea relazione "nord" da "Sala" a "Cripta";
    fallisci "Il meccanismo si blocca.";
Fine regola.
"""
    initial = session(source)
    failed = step(initial, parse_command("esamina leva"))
    assert failed.session is initial
    assert render(failed) == "Il meccanismo si blocca."

    conflict_source = """
La Cripta è una stanza.
La Torre è una stanza.
La Torre è a nord della Sala.
Regola "destinazione incompatibile" per esaminare "leva" nella fase dopo:
    crea relazione "nord" da "Sala" a "Cripta";
Fine regola.
"""
    conflicted_initial = session(conflict_source)
    conflicted = step(conflicted_initial, parse_command("esamina leva"))
    assert conflicted.session is conflicted_initial
    assert "destinazione diversa" in render(conflicted)
    assert conflicted.trace[-1].outcome == "errore con ripristino"


def test_dynamic_relation_is_structured_in_ir() -> None:
    compiled = compile_story(
        BASE
        + """
La Cripta è una stanza.
Regola "rivela" per esaminare "leva" nella fase dopo:
    crea relazione "nord" da "Sala" a "Cripta";
Fine regola.
"""
    )
    change = compiled.rules[0].effects[0].relation
    assert change is not None
    assert change.edges == (
        RelationEdge("e1", "mondo.nord", "e4"),
        RelationEdge("e4", "mondo.sud", "e1"),
    )


def test_dynamic_diagonal_relation_is_structured_and_navigable() -> None:
    initial = session(
        """
La Vedetta è una stanza.
Regola "rivela diagonale" per esaminare "leva" nella fase dopo:
    crea relazione "nordest" da "Sala" a "Vedetta";
Fine regola.
"""
    )
    revealed = step(initial, parse_command("esamina leva"))
    change = revealed.trace[-1]
    assert change.outcome == "completata"
    assert step(initial, parse_command("ne")).event.kind == "no_exit"
    moved = step(revealed.session, parse_command("ne"))
    assert moved.session.room_id != revealed.session.room_id
    returned = step(moved.session, parse_command("so"))
    assert returned.session.room_id == revealed.session.room_id


def test_dynamic_vertical_relation_is_navigable() -> None:
    initial = session(
        """
La Soffitta è una stanza.
Regola "abbassa scala" per esaminare "leva" nella fase dopo:
    crea relazione "sopra" da "Sala" a "Soffitta";
Fine regola.
"""
    )
    revealed = step(initial, parse_command("esamina leva"))
    assert step(initial, parse_command("u")).event.kind == "no_exit"
    moved = step(revealed.session, parse_command("u"))
    assert moved.session.room_id != revealed.session.room_id
    returned = step(moved.session, parse_command("d"))
    assert returned.session.room_id == revealed.session.room_id


def test_dynamic_inward_relation_is_navigable() -> None:
    initial = session(
        """
La Cripta è una stanza.
Regola "apri il varco interno" per esaminare "leva" nella fase dopo:
    crea relazione "dentro" da "Sala" a "Cripta";
Fine regola.
"""
    )
    revealed = step(initial, parse_command("esamina leva"))
    assert step(initial, parse_command("dentro")).event.kind == "no_exit"
    moved = step(revealed.session, parse_command("dentro"))
    assert moved.session.room_id != revealed.session.room_id
    returned = step(moved.session, parse_command("fuori"))
    assert returned.session.room_id == revealed.session.room_id


def test_debug_cli(
    tmp_path: "Path", monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from locus.cli import main

    path = tmp_path / "regole.locus"
    path.write_text(BASE + rule('dì "Ciao";'), encoding="utf-8")
    monkeypatch.setattr("builtins.input", lambda prompt: "esci")
    assert main(["debug", str(path)]) == 0
    output = capsys.readouterr()
    assert "Ciao" in output.out
    assert "[prima; priorità 0] prova: completata" in output.err
    assert main(["gioca", str(path)]) == 0
    assert not capsys.readouterr().err


def test_generic_catalog_and_replacement_limit() -> None:
    from locus.compiler import compile_source
    from locus.rule_model import Effect
    from locus.schema import ActionSpec

    compiled = compile_source(
        'Regola "avvia" per calcolare nella fase prima: restituisci 42; Fine regola.',
        {},
        actions={"calcolare": ActionSpec("calcolo", 0, 0)},
    )

    class Host:
        def read(self, state: int, address: Address) -> int:
            return state

        def write(self, state: int, address: Address, value: Value) -> int:
            assert type(value) is int
            return value

        def relate(self, state: int, change: RelationChange, present: bool) -> int:
            return state

        def rows(self, state: int, table_id: str) -> tuple[tuple[Scalar, ...], ...]:
            return ()

        def change_table(self, state: int, change: TableChange, present: bool) -> int:
            return state

        def perform(self, state: int, action: ActionCall) -> ActionResult[int, str]:
            return ActionResult(state, True)

    result: Execution[int, str] = execute(0, ActionCall("calcolo"), compiled.rules, Host())
    assert result.value == 42
    rules = tuple(
        replace(
            compiled.rules[0],
            id=str(i),
            selector=ActionCall(str(i)),
            effects=(Effect("sostituisci", action=ActionCall(str(i + 1))),),
        )
        for i in range(8)
    )
    result = execute(0, ActionCall("0"), rules, Host())
    assert result.outcome == "fallita"
    assert len(result.trace) == 8
    with pytest.raises(ValueError, match="positivo"):
        execute(0, ActionCall("0"), rules, Host(), max_actions=0)


def test_boolean_short_circuit() -> None:
    from locus.rule_model import Condition
    from locus.rules import evaluate

    def read(address: Address) -> int:
        raise AssertionError("Il ramo escluso non deve essere letto")

    comparison = Condition("uguale", Address("assente", "assente"), 0)
    assert evaluate(Condition("o", operands=(Condition("vero"), comparison)), read)
    assert not evaluate(Condition("e", operands=(Condition("falso"), comparison)), read)
