"""Invarianti di grafi funzionali, indipendenti da sintassi e dominio."""

from collections.abc import Mapping


def cycle_node(parents: Mapping[str, str]) -> str | None:
    complete: set[str] = set()
    for root in parents:
        path: set[str] = set()
        current = root
        while current in parents and current not in complete:
            if current in path:
                return current
            path.add(current)
            current = parents[current]
        complete.update(path)
    return None
