"""Presentazione italiana degli eventi narrativi M1."""

from locus.stdlib.game import Transition


def render(transition: Transition) -> str:
    labels = {entity.id: entity.label for entity in transition.session.world.entities}
    names = [labels[ident] for ident in transition.event.entities]
    kind = transition.event.kind
    if kind == "look":
        objects = ", ".join(names[1:]) if len(names) > 1 else "nessun oggetto"
        return f"{names[0]}\nVedi: {objects}."
    if kind == "inventory":
        return "Inventario: " + (", ".join(names) if names else "vuoto") + "."
    if kind == "taken":
        return f"Hai preso: {names[0]}."
    messages = {
        "already_carried": "Hai già questo oggetto.",
        "not_here": "Non trovi qui quell'oggetto.",
        "not_portable": "Non puoi prendere questo elemento.",
        "ambiguous": "Il nome indica più oggetti: specifica meglio.",
        "no_exit": "Non puoi andare in quella direzione.",
        "unknown": "Comando non riconosciuto. Usa guarda, prendi, inventario, nord, sud o esci.",
        "quit": "A presto.",
    }
    return messages[kind]
