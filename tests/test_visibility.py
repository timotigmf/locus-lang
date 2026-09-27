import pytest

from locus.diagnostics import CompileError
from locus.player import parse_command
from locus.runtime import instantiate
from locus.stdlib import VISIBLE
from locus.stdlib.authoring import compile_story
from locus.stdlib.game import Session, reachable, start, step, visible
from locus.stdlib.render import render
from locus.stdlib.validation import property_value

SOURCE = """
La Sala è una stanza.
Inizia nella "Sala".
Il mosaico è uno scenario nella Sala.
Il mosaico ha descrizione "Le tessere formano una costellazione.".
La "chiave d'argento" è una cosa nella Sala.
La "chiave d'argento" ha visibile falso.

Regola "rivela la chiave" per esaminare "mosaico" nella fase dopo
quando "visibile" di "chiave d'argento" è falso:
    imposta "visibile" di "chiave d'argento" a vero;
    dì "Una tessera scatta e scopre la chiave d'argento.";
Fine regola.
"""


def make_session(source: str = SOURCE) -> Session:
    return start(instantiate(compile_story(source)))


def entity_id(session: Session, label: str) -> str:
    return next(entity.id for entity in session.world.entities if entity.label == label)


def test_hidden_object_is_not_listed_or_resolved_until_revealed() -> None:
    initial = make_session()
    key_id = entity_id(initial, "chiave d'argento")
    mosaic_id = entity_id(initial, "mosaico")
    assert visible(initial) == (mosaic_id,)
    assert not reachable(initial, key_id)
    assert "Vedi: mosaico." in render(step(initial, parse_command("guarda")))
    assert step(initial, parse_command("x chiave")).event.kind == "not_here"
    assert step(initial, parse_command("prendi chiave")).event.kind == "not_here"

    revealed = step(initial, parse_command("x mosaico"))
    assert "scopre la chiave" in render(revealed)
    assert property_value(revealed.session.world, key_id, VISIBLE) is True
    assert reachable(revealed.session, key_id)
    assert visible(revealed.session) == (mosaic_id, key_id)
    assert step(revealed.session, parse_command("prendi chiave")).event.kind == "taken"


def test_scenery_is_examinable_but_not_portable() -> None:
    current = make_session()
    assert "costellazione" in render(step(current, parse_command("esamina mosaico")))
    result = step(current, parse_command("prendi mosaico"))
    assert result.event.kind == "not_portable"
    assert result.session is current


def test_hidden_container_hides_descendants_and_closed_container_blocks_access() -> None:
    current = make_session(
        """
La Sala è una stanza.
Il pulsante è uno scenario nella Sala.
Lo scrigno è un contenitore nella Sala.
Lo scrigno ha visibile falso.
La gemma è una cosa nello scrigno.
Regola "rivela lo scrigno" per esaminare "pulsante" nella fase dopo:
    imposta "visibile" di "scrigno" a vero;
Fine regola.
"""
    )
    chest_id = entity_id(current, "scrigno")
    gem_id = entity_id(current, "gemma")
    assert not reachable(current, chest_id)
    assert not reachable(current, gem_id)

    revealed = step(current, parse_command("x pulsante"))
    assert reachable(revealed.session, chest_id)
    assert not reachable(revealed.session, gem_id)
    opened = step(revealed.session, parse_command("apri scrigno"))
    assert reachable(opened.session, gem_id)


def test_visibility_change_rolls_back_with_the_rule() -> None:
    source = SOURCE.replace(
        'dì "Una tessera scatta e scopre la chiave d\'argento.";',
        'fallisci "Il meccanismo torna indietro.";',
    )
    initial = make_session(source)
    key_id = entity_id(initial, "chiave d'argento")
    result = step(initial, parse_command("x mosaico"))
    assert result.session is initial
    assert render(result) == "Il meccanismo torna indietro."
    assert property_value(result.session.world, key_id, VISIBLE) is False


def test_hidden_carried_object_is_omitted_from_inventory_until_revealed() -> None:
    current = make_session(
        """
La Sala è una stanza.
La moneta è una cosa nella Sala.
La oscurato è una proprietà logica.
Regola "oscura" per inventariare nella fase prima
quando "oscurato" di "moneta" è falso:
    imposta "visibile" di "moneta" a falso;
    imposta "oscurato" di "moneta" a vero;
Fine regola.
Regola "rivela" per guardare nella fase prima:
    imposta "visibile" di "moneta" a vero;
Fine regola.
"""
    )
    carried = step(current, parse_command("prendi moneta")).session
    hidden = step(carried, parse_command("inventario"))
    assert render(hidden) == "Inventario: vuoto."
    revealed = step(hidden.session, parse_command("guarda"))
    assert render(step(revealed.session, parse_command("inventario"))) == "Inventario: moneta."


@pytest.mark.parametrize(
    "assignment",
    [
        'La chiave ha visibile "forse".',
        "La Sala ha visibile falso.",
    ],
)
def test_visibility_assignments_are_statically_typed(assignment: str) -> None:
    with pytest.raises(CompileError) as caught:
        compile_story("La Sala è una stanza. La chiave è una cosa nella Sala. " + assignment)
    assert caught.value.code == "E111"
