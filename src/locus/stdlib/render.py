"""Presentazione italiana degli eventi narrativi, separata dalle transizioni."""

from locus.stdlib import CONTAINER, DESCRIPTION, OPENABLE, STATE
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
        return f"{names[0]}{detail}\nVedi: {objects}."
    if kind == "inventory":
        return "Inventario: " + (", ".join(names) if names else "vuoto") + "."
    if kind == "taken":
        return f"Hai preso: {names[0]}."
    if kind == "put":
        return f"Hai messo {names[0]} dentro {names[1]}."
    if kind == "examined":
        ident = transition.event.entities[0]
        description = property_value(world, ident, DESCRIPTION)
        lines = [names[0], str(description) if description else "Non noti nulla di particolare."]
        state = property_value(world, ident, STATE, "chiuso")
        if entities[ident].type_id in OPENABLE:
            lines.append(f"Stato: {state}.")
        if entities[ident].type_id == CONTAINER and state == "aperto":
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
    messages = {
        "rule": "Azione gestita dalle regole.",
        "already_carried": "Hai già questo oggetto.",
        "not_here": "Non trovi qui quell'oggetto.",
        "not_portable": "Non puoi prendere questo elemento.",
        "ambiguous": "Il nome indica più oggetti: specifica meglio.",
        "no_exit": "Non puoi andare in quella direzione.",
        "unknown": (
            "Comando non riconosciuto. Usa guarda, esamina, prendi, lascia, metti, "
            "apri, chiudi, blocca, inventario, nord, sud o esci."
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
    }
    return messages[kind]
