"""Transizioni IF minime e pure: nessun parsing sorgente, I/O o rule engine."""

from dataclasses import dataclass, replace
from typing import Literal

from locus.diagnostics import canonical
from locus.player import Intent
from locus.runtime import World
from locus.stdlib import INSIDE, NORTH, ROOM, SOUTH, THING

EventKind = Literal[
    "look",
    "inventory",
    "taken",
    "already_carried",
    "not_here",
    "not_portable",
    "ambiguous",
    "no_exit",
    "unknown",
    "quit",
]


@dataclass(frozen=True, slots=True)
class Session:
    world: World
    room_id: str
    inventory: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Event:
    kind: EventKind
    entities: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Transition:
    session: Session
    event: Event


def start(world: World) -> Session:
    rooms = [entity.id for entity in world.entities if entity.type_id == ROOM]
    if not rooms:
        raise ValueError("Per giocare occorre dichiarare almeno una stanza.")
    return Session(world, rooms[0])


def visible(session: Session) -> tuple[str, ...]:
    return tuple(
        edge.source_id
        for edge in session.world.relations
        if edge.predicate_id == INSIDE
        and edge.target_id == session.room_id
        and edge.source_id not in session.inventory
    )


def step(session: Session, intent: Intent) -> Transition:
    if intent.verb == "look":
        return Transition(session, Event("look", (session.room_id, *visible(session))))
    if intent.verb == "inventory":
        return Transition(session, Event("inventory", session.inventory))
    if intent.verb in {"north", "south"}:
        predicate = NORTH if intent.verb == "north" else SOUTH
        target = next(
            (
                edge.target_id
                for edge in session.world.relations
                if edge.source_id == session.room_id and edge.predicate_id == predicate
            ),
            None,
        )
        if target is None:
            return Transition(session, Event("no_exit"))
        return step(replace(session, room_id=target), Intent("look"))
    if intent.verb == "take" and intent.noun:
        accessible = {session.room_id, *visible(session), *session.inventory}
        matches = [
            entity
            for entity in session.world.entities
            if entity.id in accessible and canonical(entity.label) == canonical(intent.noun)
        ]
        if not matches:
            return Transition(session, Event("not_here"))
        if len(matches) > 1:
            return Transition(session, Event("ambiguous", tuple(entity.id for entity in matches)))
        entity = matches[0]
        if entity.id in session.inventory:
            return Transition(session, Event("already_carried", (entity.id,)))
        if entity.type_id != THING:
            return Transition(session, Event("not_portable", (entity.id,)))
        return Transition(
            replace(session, inventory=(*session.inventory, entity.id)),
            Event("taken", (entity.id,)),
        )
    if intent.verb == "quit":
        return Transition(session, Event("quit"))
    return Transition(session, Event("unknown"))
