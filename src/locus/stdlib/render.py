"""Presentazione italiana degli eventi narrativi, separata dalle transizioni."""

from locus.runtime import has_type
from locus.stdlib import (
    BALANCE,
    CONTAINER,
    CURRENCY,
    DESCRIPTION,
    MERCHANT_CASH,
    OPENABLE,
    PRICE,
    RESALE_PRICE,
    STATE,
    VEHICLE,
)
from locus.stdlib.game import Transition
from locus.stdlib.validation import property_value


def render(transition: Transition) -> str:
    if transition.outputs:
        return "\n".join(
            item if isinstance(item, str) else render(Transition(transition.session, item))
            for item in transition.outputs
        )
    world = transition.session.world
    entities = {entity.id: entity for entity in world.entities}
    names = [entities[ident].label for ident in transition.event.entities]
    kind = transition.event.kind
    if kind == "look":
        objects = ", ".join(names[1:]) if len(names) > 1 else "nessun oggetto"
        description = property_value(world, transition.event.entities[0], DESCRIPTION)
        detail = f"\n{description}" if description else ""
        aboard = ""
        if transition.session.vehicle_id is not None:
            vehicle = entities[transition.session.vehicle_id].label
            aboard = f"\nSei a bordo di: {vehicle}."
        return f"{names[0]}{detail}{aboard}\nVedi: {objects}."
    if kind == "inventory":
        return "Inventario: " + (", ".join(names) if names else "vuoto") + "."
    if kind == "score":
        return f"Punteggio: {transition.session.score}."
    if kind == "time":
        return f"Turno: {transition.session.turn}."
    if kind == "money":
        balance = property_value(world, transition.event.entities[0], BALANCE, 0)
        return f"Saldo: {balance} unità di {names[0]}."
    if kind == "taken":
        return f"Hai preso: {names[0]}."
    if kind == "put":
        return f"Hai messo {names[0]} dentro {names[1]}."
    if kind == "examined":
        ident = transition.event.entities[0]
        description = property_value(world, ident, DESCRIPTION)
        lines = [names[0], str(description) if description else "Non noti nulla di particolare."]
        state = property_value(world, ident, STATE, "chiuso")
        if any(has_type(world, entities[ident].type_id, expected) for expected in OPENABLE):
            lines.append(f"Stato: {state}.")
        if has_type(world, entities[ident].type_id, CONTAINER) and state == "aperto":
            lines.append(
                "Contiene: " + (", ".join(names[1:]) if len(names) > 1 else "nessun oggetto") + "."
            )
        return "\n".join(lines)
    named = {
        "opened": "Hai aperto",
        "closed": "Hai chiuso",
        "lock_success": "Hai bloccato",
        "dropped": "Hai lasciato",
    }
    if kind in named:
        return f"{named[kind]}: {names[0]}."
    if kind == "ambiguous":
        alternatives = "; ".join(f"{index}) {name}" for index, name in enumerate(names, start=1))
        return (
            f"Quale intendi? {alternatives}. "
            "Rispondi con il numero o il nome, oppure scrivi «annulla»."
        )
    if kind == "invalid_clarification":
        return (
            "La risposta non identifica una sola alternativa. "
            "Scegli un numero o un nome indicato, oppure scrivi «annulla»."
        )
    if kind == "clarification_cancelled":
        return "Chiarimento annullato."
    if kind == "custom":
        return "Non accade nulla."
    if kind == "dialogue":
        return f"La conversazione con {names[0]} continua."
    if kind == "dialogue_end":
        return f"La conversazione con {names[0]} termina." if names else "La conversazione termina."
    if kind == "no_dialogue":
        return f"{names[0]} non ha ancora un dialogo definito."
    if kind == "invalid_choice":
        return "Scegli una delle opzioni indicate, usando il numero o il testo della scelta."
    if kind == "dialogue_active":
        return "La conversazione è in corso: scegli un'opzione oppure scrivi «basta»."
    if kind == "no_active_dialogue":
        return "Non c'è una conversazione in corso."
    if kind == "boarded":
        return f"Sei salito a bordo di: {names[0]}."
    if kind == "disembarked":
        return f"Sei sceso da: {names[0]}."
    if kind == "not_vehicle":
        return "Quell'elemento non è un veicolo."
    if kind == "already_aboard":
        return f"Sei già a bordo di: {names[0]}."
    if kind == "already_in_vehicle":
        return f"Devi prima scendere da: {names[0]}."
    if kind == "not_in_vehicle":
        return "Non sei a bordo di alcun veicolo."
    if kind == "wrong_vehicle":
        return "Non sei a bordo di quel veicolo."
    if kind == "purchased":
        price = property_value(world, transition.event.entities[0], PRICE, 0)
        balance = property_value(world, transition.event.entities[1], BALANCE, 0)
        seller = f" da {names[2]}" if len(names) > 2 else ""
        return (
            f"Hai comprato: {names[0]}{seller} per {price} unità di {names[1]}. Saldo: {balance}."
        )
    if kind == "sold":
        resale = property_value(world, transition.event.entities[0], RESALE_PRICE, 0)
        balance = property_value(world, transition.event.entities[1], BALANCE, 0)
        return (
            f"Hai venduto: {names[0]} a {names[2]} per {resale} unità di {names[1]}. "
            f"Saldo: {balance}."
        )
    if kind == "insufficient_funds":
        price = property_value(world, transition.event.entities[0], PRICE, 0)
        balance = property_value(world, transition.event.entities[1], BALANCE, 0)
        return f"Fondi insufficienti: servono {price} unità, saldo disponibile {balance}."
    if kind == "not_for_sale":
        return "Quell'elemento non è in vendita."
    if kind == "not_sellable":
        return "Quell'elemento non è una merce rivendibile."
    if kind == "no_merchant":
        return "Non c'è alcun mercante disponibile qui."
    if kind == "not_merchant":
        return f"{names[0]} non è un mercante."
    if kind == "wrong_merchant":
        return f"{names[0]} non vende {names[1]}."
    if kind == "merchant_refuses":
        return f"{names[0]} non acquista {names[1]}."
    if kind == "merchant_no_funds":
        resale = property_value(world, transition.event.entities[1], RESALE_PRICE, 0)
        cash = property_value(world, transition.event.entities[0], MERCHANT_CASH, 0)
        return f"{names[0]} non ha fondi sufficienti: servono {resale}, cassa disponibile {cash}."
    if kind == "must_buy":
        return f"Devi prima comprare: {names[0]}."
    if kind == "already_owned":
        return f"Hai già acquistato: {names[0]}. Puoi prenderlo senza pagare di nuovo."
    if kind == "no_currency":
        return "La storia non dichiara alcuna valuta."
    unknown = (
        "Comando non riconosciuto. Usa guarda, esamina, prendi, lascia, metti, "
        "apri, chiudi, blocca, inventario, nord, sud, est, ovest, nordest, "
        "sudest, sudovest, nordovest, su, giù, dentro, fuori o esci. Sono "
        "disponibili anche le abbreviazioni l, x, i, n, s, e, o, ne, se, so, "
        "no, u, d e q; dopo un oggetto noto puoi usare esso, essa o forme come prendila."
    )
    if world.dialogues:
        unknown += " Per conversare usa parla con NOME."
    if world.scenes:
        unknown += " Usa turno per il tempo e punteggio per i punti."
    if any(has_type(world, entity.type_id, VEHICLE) for entity in world.entities):
        unknown += " Per i veicoli usa sali/entra e scendi."
    if any(has_type(world, entity.type_id, CURRENCY) for entity in world.entities):
        unknown += " Per il commercio usa compra NOME, vendi NOME a MERCANTE e denaro per il saldo."
    messages = {
        "rule": "Azione gestita dalle regole.",
        "already_carried": "Hai già questo oggetto.",
        "not_here": "Non trovi qui quell'oggetto.",
        "not_portable": "Non puoi prendere questo elemento.",
        "no_exit": "Non c'è alcun passaggio in quella direzione.",
        "unknown": unknown,
        "missing_noun": "Indica quale oggetto vuoi esaminare o manipolare.",
        "no_referent": "Non c'è ancora un oggetto a cui riferire il pronome.",
        "no_indirect_referent": ("Non c'è ancora una destinazione a cui riferire il clitico «ci»."),
        "missing_direction": "Indica in quale direzione vuoi andare.",
        "invalid_direction": (
            "Direzione non riconosciuta. Usa nord, sud, est, ovest, le diagonali, "
            "su, giù, dentro o fuori."
        ),
        "quit": "A presto.",
        "locked": "È bloccato: serve una chiave adatta.",
        "already_open": "È già aperto.",
        "already_closed": "È già chiuso.",
        "already_locked": "È già bloccato.",
        "not_openable": "Questo elemento non si apre e non si chiude.",
        "wrong_key": "Questa chiave non è adatta.",
        "not_carried": "Devi avere con te l'oggetto da usare.",
        "container_closed": "Il contenitore è chiuso.",
        "door_closed": "La porta è chiusa: devi aprirla prima di passare.",
        "not_container": "La destinazione non è un contenitore.",
        "cycle": "Un contenitore non può contenere sé stesso, nemmeno indirettamente.",
        "must_close": "Devi chiuderlo prima di bloccarlo.",
        "wrong_kind": "Questo comando non si applica a quell'elemento.",
    }
    return messages[kind]
