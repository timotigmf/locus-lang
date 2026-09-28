import pytest

from locus.diagnostics import CompileError
from locus.ir import IR_VERSION
from locus.player import Intent, parse_command
from locus.runtime import has_type, instantiate
from locus.stdlib import (
    BALANCE,
    MERCHANDISE,
    MERCHANT,
    MERCHANT_CASH,
    OFFERS,
    RESALE_PRICE,
)
from locus.stdlib.authoring import compile_story
from locus.stdlib.game import Session, Transition, start, step
from locus.stdlib.render import render
from locus.stdlib.validation import property_value

SOURCE = """
La Bottega è una stanza.
Il credito portuale è una valuta.
Il credito portuale ha saldo 20.
La Ada è una mercante nella Bottega.
La Ada ha cassa 30.
La bussola è un prodotto nella Bottega.
La bussola ha prezzo 7.
La bussola ha prezzo di rivendita 3.
La Ada vende la bussola.
"""


def command(session: Session, text: str) -> Transition:
    return step(session, parse_command(text, session.world.actions, commerce_enabled=True))


def entity_id(session: Session, label: str) -> str:
    return next(entity.id for entity in session.world.entities if entity.label == label)


def value(session: Session, label: str, property_id: str) -> object:
    return property_value(session.world, entity_id(session, label), property_id)


def test_merchant_stock_is_typed_and_lowered_in_ir20() -> None:
    program = compile_story(SOURCE)
    world = instantiate(program)
    merchant = next(entity for entity in world.entities if entity.label == "Ada")
    item = next(entity for entity in world.entities if entity.label == "bussola")
    assert IR_VERSION == 21
    assert has_type(world, merchant.type_id, MERCHANT)
    assert has_type(world, item.type_id, MERCHANDISE)
    assert property_value(world, merchant.id, MERCHANT_CASH) == 30
    assert property_value(world, item.id, RESALE_PRICE) == 3
    assert any(
        edge.source_id == item.id and edge.predicate_id == OFFERS and edge.target_id == merchant.id
        for edge in world.relations
    )


@pytest.mark.parametrize(
    ("text", "intent"),
    [
        ("compra bussola da Ada", Intent("buy", "bussola", "ada")),
        ("buy bussola from Ada", Intent("buy", "bussola", "ada")),
        ("vendi la bussola ad Ada", Intent("sell", "bussola", "ada")),
        ("vendere bussola alla Ada", Intent("sell", "bussola", "ada")),
        ("sell bussola to Ada", Intent("sell", "bussola", "ada")),
        ("vendi bussola", Intent("sell", "bussola")),
    ],
)
def test_merchant_command_forms(text: str, intent: Intent) -> None:
    assert parse_command(text, commerce_enabled=True) == intent


def test_buy_and_sell_transfer_stock_ownership_and_both_balances() -> None:
    initial = start(instantiate(compile_story(SOURCE)))
    bought = command(initial, "compra bussola da Ada")
    item_id = entity_id(bought.session, "bussola")
    merchant_id = entity_id(bought.session, "Ada")
    assert bought.event.entities == (
        item_id,
        entity_id(bought.session, "credito portuale"),
        merchant_id,
    )
    assert item_id in bought.session.inventory
    assert item_id in bought.session.owned_ids
    assert value(bought.session, "credito portuale", BALANCE) == 13
    assert value(bought.session, "Ada", MERCHANT_CASH) == 37
    assert not any(edge.predicate_id == OFFERS for edge in bought.session.world.relations)
    assert "da Ada" in render(bought)

    sold = command(bought.session, "vendi bussola a Ada")
    assert sold.event.kind == "sold"
    assert item_id not in sold.session.inventory
    assert item_id not in sold.session.owned_ids
    assert value(sold.session, "credito portuale", BALANCE) == 16
    assert value(sold.session, "Ada", MERCHANT_CASH) == 34
    assert any(
        edge.source_id == item_id and edge.predicate_id == OFFERS and edge.target_id == merchant_id
        for edge in sold.session.world.relations
    )
    assert render(sold) == (
        "Hai venduto: bussola a Ada per 3 unità di credito portuale. Saldo: 16."
    )

    bought_again = command(sold.session, "compra bussola")
    assert bought_again.event.kind == "purchased"
    assert value(bought_again.session, "credito portuale", BALANCE) == 9


def test_purchase_from_wrong_merchant_is_rejected_without_changes() -> None:
    source = SOURCE + "La Bea è una mercante nella Bottega. La Bea ha cassa 10."
    current = start(instantiate(compile_story(source)))
    result = command(current, "compra bussola da Bea")
    assert result.event.kind == "wrong_merchant"
    assert result.session is current
    assert render(result) == "Bea non vende bussola."


def test_sale_requires_an_explicit_merchant_when_more_than_one_is_reachable() -> None:
    source = SOURCE + "La Bea è una mercante nella Bottega. La Bea ha cassa 10."
    current = start(instantiate(compile_story(source)))
    bought = command(current, "compra bussola")
    ambiguous = command(bought.session, "vendi bussola")
    assert ambiguous.event.kind == "ambiguous"
    assert set(ambiguous.event.entities) == {
        entity_id(bought.session, "Ada"),
        entity_id(bought.session, "Bea"),
    }
    sold = command(bought.session, "vendi bussola a Bea")
    assert sold.event.kind == "sold"


def test_merchant_can_refuse_or_lack_cash_without_partial_changes() -> None:
    refuses = SOURCE.replace("prezzo di rivendita 3", "prezzo di rivendita 0")
    bought = command(start(instantiate(compile_story(refuses))), "compra bussola")
    result = command(bought.session, "vendi bussola a Ada")
    assert result.event.kind == "merchant_refuses"
    assert result.session is bought.session

    insolvent = SOURCE.replace("cassa 30", "cassa 0").replace(
        "prezzo di rivendita 3", "prezzo di rivendita 10"
    )
    bought = command(start(instantiate(compile_story(insolvent))), "compra bussola")
    result = command(bought.session, "vendi bussola a Ada")
    assert result.event.kind == "merchant_no_funds"
    assert result.session is bought.session
    assert "cassa disponibile 7" in render(result)


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ("La Sala è una stanza. La Ada è una mercante nella Sala.", "valuta"),
        (
            SOURCE.replace("La Ada vende la bussola.", ""),
            "Associa ogni merce",
        ),
        (
            SOURCE.replace("La Ada ha cassa 30.", "La Ada ha cassa -1."),
            "cassa",
        ),
        (
            SOURCE.replace(
                "La bussola ha prezzo di rivendita 3.",
                "La bussola ha prezzo di rivendita -1.",
            ),
            "rivendita",
        ),
        (
            SOURCE.replace(
                "La Ada è una mercante nella Bottega.",
                "La Piazza è una stanza. La Ada è una mercante nella Piazza.",
            ),
            "stessa stanza",
        ),
    ],
)
def test_invalid_merchant_contracts_report_e125(source: str, message: str) -> None:
    with pytest.raises(CompileError) as caught:
        compile_story(source, "mercanti.locus")
    assert caught.value.code == "E125"
    assert message in caught.value.message
    assert caught.value.span.source == "mercanti.locus"


def test_sell_participates_in_rules() -> None:
    source = SOURCE + (
        'Regola "ricevuta di vendita" per vendere "bussola" con "Ada" nella fase dopo: '
        'dì "Ada firma la ricevuta."; Fine regola.'
    )
    bought = command(start(instantiate(compile_story(source))), "compra bussola")
    sold = command(bought.session, "vendi bussola a Ada")
    assert sold.event.kind == "sold"
    assert "firma la ricevuta" in render(sold)


def test_rule_cannot_make_merchant_cash_negative() -> None:
    source = SOURCE + (
        'Regola "cassa impossibile" per vendere "bussola" con "Ada" nella fase prima: '
        'diminuisci "cassa" di "Ada" di 100; Fine regola.'
    )
    bought = command(start(instantiate(compile_story(source))), "compra bussola")
    result = command(bought.session, "vendi bussola a Ada")
    assert result.session is bought.session
    assert result.trace[-1].outcome == "errore con ripristino"
    assert value(result.session, "credito portuale", BALANCE) == 13
    assert value(result.session, "Ada", MERCHANT_CASH) == 37
