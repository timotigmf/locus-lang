from dataclasses import replace

import pytest

from locus.diagnostics import CompileError
from locus.ir import IR_VERSION, ProgramIR, TableColumnIR, TableIR
from locus.player import parse_command
from locus.runtime import instantiate
from locus.stdlib.authoring import compile_story
from locus.stdlib.game import start, step
from locus.stdlib.render import render

BASE = """
La Sala è una stanza.
Azione "aggiornare" senza oggetti con comando "aggiorna".
Tabella "scorte":
    Colonna "articolo" testuale.
    Colonna "prezzo" numerica.
    Colonna "disponibile" logica.
    Riga "corda" 5 vero.
    Riga "corda" 5 vero.
Fine tabella.
"""


def table_rows(source: str) -> tuple[tuple[str | int | bool, ...], ...]:
    session = start(instantiate(compile_story(source)))
    return session.world.tables[0].rows


def test_table_schema_and_rows_are_compiled_in_order() -> None:
    program = compile_story(BASE)
    table = program.tables[0]
    assert table.label == "scorte"
    assert [(column.label, column.value_kind) for column in table.columns] == [
        ("articolo", "testo"),
        ("prezzo", "numero"),
        ("disponibile", "logico"),
    ]
    assert table.rows == (("corda", 5, True), ("corda", 5, True))


def test_table_condition_addition_and_single_removal() -> None:
    source = (
        BASE
        + """
Regola "cambia scorte" per aggiornare nella fase invece
quando tabella "scorte" contiene riga "corda" 5 vero:
    rimuovi riga "corda" 5 vero da tabella "scorte";
    aggiungi riga "lanterna" 12 falso a tabella "scorte";
    dì "Scorte aggiornate.";
Fine regola.
"""
    )
    current = start(instantiate(compile_story(source)))
    result = step(current, parse_command("aggiorna", current.world.actions))
    assert render(result) == "Scorte aggiornate."
    assert result.session.world.tables[0].rows == (
        ("corda", 5, True),
        ("lanterna", 12, False),
    )
    assert current.world.tables[0].rows == (("corda", 5, True), ("corda", 5, True))


def test_table_mutation_rolls_back() -> None:
    source = (
        BASE
        + """
Regola "annulla" per aggiornare nella fase prima:
    aggiungi riga "gesso" 2 vero a tabella "scorte";
    fallisci "Operazione annullata.";
Fine regola.
"""
    )
    current = start(instantiate(compile_story(source)))
    result = step(current, parse_command("aggiorna", current.world.actions))
    assert result.session is current
    assert render(result) == "Operazione annullata."


@pytest.mark.parametrize(
    ("source", "code"),
    [
        (
            BASE + 'Tabella "SCORTE": Colonna "x" testuale. Fine tabella.',
            "E115",
        ),
        ('Tabella "vuota": Fine tabella.', "E116"),
        (
            'Tabella "x": Colonna "nome" testuale. Colonna "NOME" numerica. Fine tabella.',
            "E116",
        ),
        ('Tabella "x": Colonna "numero" numerica. Riga "uno". Fine tabella.', "E117"),
        (
            BASE + 'Regola "x" per aggiornare nella fase dopo: '
            'aggiungi riga "x" 1 vero a tabella "ignota"; Fine regola.',
            "E314",
        ),
        (
            BASE + 'Regola "x" per aggiornare nella fase dopo: '
            'aggiungi riga "x" vero vero a tabella "scorte"; Fine regola.',
            "E314",
        ),
        (
            BASE + 'Regola "x" per aggiornare nella fase dopo '
            'quando tabella "scorte" contiene riga "x" 1: dì "x"; Fine regola.',
            "E314",
        ),
        (
            BASE + 'Regola "x" per aggiornare nella fase verifica: '
            'rimuovi riga "corda" 5 vero da tabella "scorte"; Fine regola.',
            "E307",
        ),
    ],
)
def test_table_diagnostics(source: str, code: str) -> None:
    with pytest.raises(CompileError) as caught:
        compile_story(source, "tabelle.locus")
    assert caught.value.code == code
    assert caught.value.span.source == "tabelle.locus"


def test_runtime_rejects_invalid_table_ir() -> None:
    column = TableColumnIR("prezzo", "prezzo", "numero")
    valid = TableIR("t1", "prezzi", (column,), ((1,),))
    instantiate(ProgramIR(IR_VERSION, (), tables=(valid,)))
    with pytest.raises(ValueError, match="tabella"):
        instantiate(
            ProgramIR(
                IR_VERSION,
                (),
                tables=(replace(valid, rows=((True,),)),),
            )
        )
    with pytest.raises(ValueError, match="tabella"):
        instantiate(
            ProgramIR(
                IR_VERSION,
                (),
                tables=tuple(
                    replace(valid, id=f"t{index}", label=f"prezzi {index}") for index in range(65)
                ),
            )
        )
