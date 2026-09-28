from dataclasses import replace

import pytest

from locus.diagnostics import CompileError
from locus.ir import IR_VERSION
from locus.player import Intent, parse_command
from locus.runtime import has_type, instantiate
from locus.stdlib import BALANCE, CURRENCY, MERCHANDISE, PRICE
from locus.stdlib.authoring import compile_story
from locus.stdlib.game import Session, Transition, start, step
from locus.stdlib.render import render
from locus.stdlib.validation import WorldError, property_value, validate_session

SOURCE = """
La Bottega è una stanza.
Il credito portuale è una valuta.
Il credito portuale ha saldo 12.
Una provvista è un tipo di prodotto.
La bussola tascabile è una provvista nella Bottega.
La bussola tascabile ha prezzo 7.
La campana è una cosa nella Bottega.
"""


def command(session: Session, text: str) -> Transition:
    return step(
        session,
        parse_command(text, session.world.actions, commerce_enabled=True),
    )


def currency_id(session: Session) -> str:
    return next(
        entity.id
        for entity in session.world.entities
        if has_type(session.world, entity.type_id, CURRENCY)
    )


def test_currency_and_merchandise_are_lowered_in_ir20() -> None:
    program = compile_story(SOURCE)
    world = instantiate(program)
    currency = next(entity for entity in world.entities if entity.label == "credito portuale")
    item = next(entity for entity in world.entities if entity.label == "bussola tascabile")
    assert IR_VERSION == 21
    assert has_type(world, currency.type_id, CURRENCY)
    assert has_type(world, item.type_id, MERCHANDISE)
    assert property_value(world, currency.id, BALANCE) == 12
    assert property_value(world, item.id, PRICE) == 7


@pytest.mark.parametrize(
    ("text", "intent"),
    [
        ("compra la bussola", Intent("buy", "bussola")),
        ("acquista bussola tascabile", Intent("buy", "bussola tascabile")),
        ("buy the bussola", Intent("buy", "bussola")),
        ("purchase bussola", Intent("buy", "bussola")),
        ("denaro", Intent("money")),
        ("saldo", Intent("money")),
        ("money", Intent("money")),
        ("balance", Intent("money")),
    ],
)
def test_commerce_commands(text: str, intent: Intent) -> None:
    assert parse_command(text, commerce_enabled=True) == intent


def test_commerce_commands_are_opt_in() -> None:
    assert parse_command("compra bussola").verb == "unknown"
    assert parse_command("denaro").verb == "unknown"


def test_purchase_is_atomic_and_owned_item_can_be_taken_again() -> None:
    current = start(instantiate(compile_story(SOURCE)))
    assert command(current, "prendi bussola").event.kind == "must_buy"
    assert render(command(current, "denaro")) == "Saldo: 12 unità di credito portuale."

    bought = command(current, "compra bussola")
    item_id = bought.event.entities[0]
    assert bought.event.kind == "purchased"
    assert item_id in bought.session.inventory
    assert item_id in bought.session.owned_ids
    assert property_value(bought.session.world, currency_id(bought.session), BALANCE) == 5
    assert "Hai comprato: bussola tascabile per 7" in render(bought)

    dropped = command(bought.session, "lascia bussola")
    assert item_id not in dropped.session.inventory
    assert item_id in dropped.session.owned_ids
    assert command(dropped.session, "compra bussola").event.kind == "already_owned"
    taken = command(dropped.session, "prendi bussola")
    assert taken.event.kind == "taken"
    assert property_value(taken.session.world, currency_id(taken.session), BALANCE) == 5


def test_failed_purchase_does_not_change_money_or_location() -> None:
    source = SOURCE.replace("saldo 12", "saldo 3")
    current = start(instantiate(compile_story(source)))
    result = command(current, "buy bussola")
    assert result.event.kind == "insufficient_funds"
    assert result.session == current
    assert render(result) == "Fondi insufficienti: servono 7 unità, saldo disponibile 3."


def test_only_merchandise_can_be_purchased() -> None:
    current = start(instantiate(compile_story(SOURCE)))
    assert command(current, "compra campana").event.kind == "not_for_sale"


@pytest.mark.parametrize(
    ("source", "message"),
    [
        (
            "La Sala è una stanza. La bussola è un prodotto nella Sala. La bussola ha prezzo 2.",
            "Dichiara una valuta",
        ),
        (
            "La Sala è una stanza. Il credito è una valuta. La bussola è un prodotto nella Sala.",
            "prezzo",
        ),
        (
            "La Sala è una stanza. Il credito è una valuta. Il credito ha saldo -1.",
            "saldo",
        ),
        (
            "La Sala è una stanza. Il credito è una valuta. Il gettone è una valuta.",
            "una sola valuta",
        ),
    ],
)
def test_invalid_commerce_contracts_report_e124(source: str, message: str) -> None:
    with pytest.raises(CompileError) as caught:
        compile_story(source, "commercio.locus")
    assert caught.value.code == "E124"
    assert message in caught.value.message
    assert caught.value.span.source == "commercio.locus"


def test_purchase_participates_in_rules() -> None:
    source = (
        SOURCE
        + 'Regola "ricevuta" per comprare "bussola tascabile" nella fase dopo: '
        + 'dì "Il bottegaio consegna la ricevuta."; Fine regola.'
    )
    current = start(instantiate(compile_story(source)))
    result = command(current, "compra bussola")
    assert result.event.kind == "purchased"
    assert "ricevuta" in render(result)


def test_rule_cannot_make_commerce_state_invalid() -> None:
    source = (
        SOURCE
        + 'Regola "sconto impossibile" per comprare "bussola tascabile" nella fase prima: '
        + 'diminuisci "prezzo" di "bussola tascabile" di 7; Fine regola.'
    )
    current = start(instantiate(compile_story(source)))
    result = command(current, "compra bussola")
    assert result.session is current
    assert result.trace[-1].outcome == "errore con ripristino"
    assert property_value(result.session.world, currency_id(result.session), BALANCE) == 12
    assert not result.session.inventory


def test_session_validation_rejects_unpaid_merchandise_in_inventory() -> None:
    current = start(instantiate(compile_story(SOURCE)))
    item = next(
        entity.id
        for entity in current.world.entities
        if has_type(current.world, entity.type_id, MERCHANDISE)
    )
    ordinary_item = next(
        entity.id for entity in current.world.entities if entity.label == "campana"
    )
    world = replace(
        current.world,
        relations=tuple(
            edge for edge in current.world.relations if edge.source_id not in {item, ordinary_item}
        ),
    )
    invalid = replace(current, world=world, inventory=(ordinary_item, item))
    with pytest.raises(WorldError, match="non acquistata") as caught:
        validate_session(
            invalid.world,
            invalid.inventory,
            invalid.room_id,
            invalid.vehicle_id,
            invalid.owned_ids,
        )
    assert caught.value.entity_id == item


def test_author_can_use_buy_words_without_commerce() -> None:
    source = (
        "La Sala è una stanza. "
        'Azione "contemplare" senza oggetti con comando "compra". '
        'Regola "eco" per contemplare nella fase invece: dì "Osservi."; Fine regola.'
    )
    world = instantiate(compile_story(source))
    result = step(start(world), parse_command("compra", world.actions))
    assert render(result) == "Osservi."


def test_buy_words_are_reserved_when_commerce_exists() -> None:
    with pytest.raises(CompileError) as caught:
        compile_story(
            "La Sala è una stanza. Il credito è una valuta. "
            'Azione "contemplare" senza oggetti con comando "compra".'
        )
    assert caught.value.code == "E311"
