"""Transizioni IF pure con contenimento, stati e intenti a due oggetti."""

from dataclasses import dataclass, replace
from typing import Literal

from locus.diagnostics import canonical
from locus.ir import ActionIR, DialogueIR, DialogueNodeIR, PropertyIR, RelationIR, TableIR
from locus.player import Intent, parse_command
from locus.rule_model import ActionCall, Address, RelationChange, TableChange, Trace
from locus.rules import ActionResult, RuleError, execute
from locus.runtime import Entity, World, has_type
from locus.schema import Scalar, Value, valid_value
from locus.stdlib import (
    BALANCE,
    CONTAINER,
    CURRENCY,
    DOOR,
    DOWN,
    EAST,
    INSIDE,
    INWARD,
    MERCHANDISE,
    MERCHANT,
    MERCHANT_CASH,
    NORTH,
    NORTHEAST,
    NORTHWEST,
    OFFERS,
    OPENABLE,
    OUTWARD,
    PERSON,
    PORTABLE,
    PRICE,
    RESALE_PRICE,
    ROOM,
    SIDE_A,
    SIDE_B,
    SOUTH,
    SOUTHEAST,
    SOUTHWEST,
    STATE,
    UNLOCKS,
    UP,
    VEHICLE,
    VISIBLE,
    WEST,
)
from locus.stdlib.validation import (
    integer_property_value,
    property_value,
    validate_session,
    validate_world,
)

EventKind = Literal[
    "rule",
    "look",
    "inventory",
    "taken",
    "already_carried",
    "not_here",
    "not_portable",
    "ambiguous",
    "invalid_clarification",
    "clarification_cancelled",
    "no_referent",
    "no_indirect_referent",
    "missing_direction",
    "invalid_direction",
    "no_previous_room",
    "cannot_return",
    "no_exit",
    "unknown",
    "missing_noun",
    "quit",
    "opened",
    "closed",
    "locked",
    "already_open",
    "already_closed",
    "already_locked",
    "not_openable",
    "wrong_key",
    "not_carried",
    "container_closed",
    "door_closed",
    "not_container",
    "cycle",
    "put",
    "dropped",
    "examined",
    "must_close",
    "lock_success",
    "custom",
    "wrong_kind",
    "dialogue",
    "no_dialogue",
    "invalid_choice",
    "dialogue_active",
    "dialogue_end",
    "no_active_dialogue",
    "score",
    "time",
    "boarded",
    "disembarked",
    "not_vehicle",
    "already_aboard",
    "already_in_vehicle",
    "not_in_vehicle",
    "wrong_vehicle",
    "money",
    "purchased",
    "no_currency",
    "not_for_sale",
    "insufficient_funds",
    "must_buy",
    "already_owned",
    "sold",
    "not_sellable",
    "no_merchant",
    "not_merchant",
    "wrong_merchant",
    "merchant_refuses",
    "merchant_no_funds",
]

DIRECTION_PREDICATES = {
    "north": NORTH,
    "south": SOUTH,
    "east": EAST,
    "west": WEST,
    "northeast": NORTHEAST,
    "southeast": SOUTHEAST,
    "southwest": SOUTHWEST,
    "northwest": NORTHWEST,
    "up": UP,
    "down": DOWN,
    "inward": INWARD,
    "outward": OUTWARD,
}


@dataclass(frozen=True, slots=True)
class Clarification:
    intent: Intent
    argument: Literal["noun", "indirect"]
    candidates: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Session:
    world: World
    room_id: str
    inventory: tuple[str, ...] = ()
    dialogue_id: str | None = None
    dialogue_node_id: str | None = None
    visited_dialogue_nodes: tuple[str, ...] = ()
    turn: int = 0
    score: int = 0
    active_scene_ids: tuple[str, ...] = ()
    completed_scene_ids: tuple[str, ...] = ()
    score_log: tuple["ScoreEntry", ...] = ()
    vehicle_id: str | None = None
    owned_ids: tuple[str, ...] = ()
    clarification: Clarification | None = None
    pronoun_id: str | None = None
    indirect_pronoun_id: str | None = None
    previous_room_id: str | None = None


@dataclass(frozen=True, slots=True)
class Event:
    kind: EventKind
    entities: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class DialogueStep:
    dialogue_id: str
    dialogue_label: str
    speaker_id: str
    node_id: str
    node_label: str
    choice_id: str | None = None
    choice_label: str | None = None
    ended: bool = False


@dataclass(frozen=True, slots=True)
class ScoreEntry:
    scene_id: str
    scene_label: str
    points: int
    turn: int


@dataclass(frozen=True, slots=True)
class SceneStep:
    scene_id: str
    scene_label: str
    event: Literal["iniziata", "terminata"]
    turn: int
    score_delta: int = 0


@dataclass(frozen=True, slots=True)
class Transition:
    session: Session
    event: Event
    outputs: tuple[Event | str, ...] = ()
    trace: tuple[Trace, ...] = ()
    result: Value | None = None
    dialogue: tuple[DialogueStep, ...] = ()
    scenes: tuple[SceneStep, ...] = ()


def start(world: World) -> Session:
    validate_world(world)
    rooms = [entity.id for entity in world.entities if has_type(world, entity.type_id, ROOM)]
    if not rooms:
        raise ValueError("Per giocare occorre dichiarare almeno una stanza.")
    return Session(world, world.entry_id or rooms[0])


def _parents(session: Session) -> dict[str, str]:
    return {
        edge.source_id: edge.target_id
        for edge in session.world.relations
        if edge.predicate_id == INSIDE
    }


def _state(session: Session, entity_id: str) -> str:
    return str(property_value(session.world, entity_id, STATE, "chiuso"))


def _sides(session: Session, door_id: str) -> frozenset[str]:
    return frozenset(
        edge.target_id
        for edge in session.world.relations
        if edge.source_id == door_id and edge.predicate_id in {SIDE_A, SIDE_B}
    )


def carried(session: Session, entity_id: str) -> bool:
    parents = _parents(session)
    current = entity_id
    seen: set[str] = set()
    while current not in seen:
        if current in session.inventory:
            return True
        seen.add(current)
        if current not in parents:
            return False
        current = parents[current]
    return False


def reachable(session: Session, entity_id: str) -> bool:
    if entity_id == session.room_id:
        return True
    if property_value(session.world, entity_id, VISIBLE, True) is not True:
        return False
    if session.room_id in _sides(session, entity_id):
        return True
    parents = _parents(session)
    current = entity_id
    seen: set[str] = set()
    while current not in seen:
        if current in session.inventory:
            return True
        seen.add(current)
        parent = parents.get(current)
        if parent == session.room_id:
            return True
        if (
            parent is None
            or property_value(session.world, parent, VISIBLE, True) is not True
            or _state(session, parent) != "aperto"
        ):
            return False
        current = parent
    return False


def visible(session: Session) -> tuple[str, ...]:
    return tuple(
        entity.id
        for entity in session.world.entities
        if entity.id != session.room_id
        and entity.id != session.vehicle_id
        and reachable(session, entity.id)
        and not carried(session, entity.id)
    )


def _resolve(session: Session, name: str, selected_id: str | None = None) -> Entity | Event:
    in_scope = [entity for entity in session.world.entities if reachable(session, entity.id)]
    if selected_id is not None:
        return next(
            (entity for entity in in_scope if entity.id == selected_id),
            Event("not_here"),
        )
    normalized = canonical(name)
    matches = [entity for entity in in_scope if canonical(entity.label) == normalized]
    if not matches:
        exact_targets = {
            synonym.target_id
            for synonym in session.world.synonyms
            if canonical(synonym.alias) == normalized
        }
        matches = [entity for entity in in_scope if entity.id in exact_targets]
    if not matches:
        words = set(normalized.split())
        partial_targets = {
            synonym.target_id
            for synonym in session.world.synonyms
            if words and words.issubset(set(canonical(synonym.alias).split()))
        }
        matches = [
            entity
            for entity in in_scope
            if words
            and (
                words.issubset(set(canonical(entity.label).split())) or entity.id in partial_targets
            )
        ]
    if not matches:
        return Event("not_here")
    if len(matches) > 1:
        return Event("ambiguous", tuple(entity.id for entity in matches))
    return matches[0]


def _changed(session: Session, kind: EventKind, *entities: str) -> Transition:
    validate_session(
        session.world,
        session.inventory,
        session.room_id,
        session.vehicle_id,
        session.owned_ids,
    )
    return Transition(session, Event(kind, entities))


def _move(session: Session, entity_id: str, destination: str | None) -> Session:
    edges = tuple(
        edge
        for edge in session.world.relations
        if not (edge.source_id == entity_id and edge.predicate_id == INSIDE)
    )
    inventory = tuple(ident for ident in session.inventory if ident != entity_id)
    if destination is None:
        inventory = (*inventory, entity_id)
    else:
        edges = (*edges, RelationIR(entity_id, INSIDE, destination))
    return replace(session, world=replace(session.world, relations=edges), inventory=inventory)


def _set_state(session: Session, entity_id: str, value: str) -> Session:
    properties = tuple(
        prop
        for prop in session.world.properties
        if not (prop.entity_id == entity_id and prop.property_id == STATE)
    )
    return replace(
        session,
        world=replace(session.world, properties=(*properties, PropertyIR(entity_id, STATE, value))),
    )


def _set_property(session: Session, entity_id: str, property_id: str, value: Value) -> Session:
    properties = tuple(
        prop
        for prop in session.world.properties
        if not (prop.entity_id == entity_id and prop.property_id == property_id)
    )
    return replace(
        session,
        world=replace(
            session.world,
            properties=(*properties, PropertyIR(entity_id, property_id, value)),
        ),
    )


def _key_error(
    session: Session, target_id: str, name: str, selected_id: str | None
) -> Event | None:
    key = _resolve(session, name, selected_id)
    if isinstance(key, Event):
        return key
    if not carried(session, key.id):
        return Event("not_carried", (key.id,))
    if not any(
        edge.source_id == key.id and edge.predicate_id == UNLOCKS and edge.target_id == target_id
        for edge in session.world.relations
    ):
        return Event("wrong_key", (key.id,))
    return None


def _opening(session: Session, intent: Intent, entity: Entity) -> Transition:
    if not any(has_type(session.world, entity.type_id, expected) for expected in OPENABLE):
        return Transition(session, Event("not_openable", (entity.id,)))
    state = _state(session, entity.id)
    if intent.verb == "close":
        if state != "aperto":
            return Transition(session, Event("already_closed", (entity.id,)))
        return _changed(_set_state(session, entity.id, "chiuso"), "closed", entity.id)
    if intent.verb == "lock":
        if state == "aperto":
            return Transition(session, Event("must_close", (entity.id,)))
        if state == "bloccato":
            return Transition(session, Event("already_locked", (entity.id,)))
    elif state == "aperto":
        return Transition(session, Event("already_open", (entity.id,)))
    if intent.indirect:
        error = _key_error(session, entity.id, intent.indirect, intent.indirect_id)
        if error:
            return Transition(session, error)
    elif state == "bloccato" or intent.verb == "lock":
        return Transition(session, Event("locked", (entity.id,)))
    value = "bloccato" if intent.verb == "lock" else "aperto"
    kind: EventKind = "lock_success" if intent.verb == "lock" else "opened"
    return _changed(_set_state(session, entity.id, value), kind, entity.id)


def _board(session: Session, name: str | None, selected_id: str | None = None) -> Transition:
    if name is None:
        return Transition(session, Event("missing_noun"))
    entity = _resolve(session, name, selected_id)
    if isinstance(entity, Event):
        return Transition(session, entity)
    if not has_type(session.world, entity.type_id, VEHICLE):
        return Transition(session, Event("not_vehicle", (entity.id,)))
    if session.vehicle_id == entity.id:
        return Transition(session, Event("already_aboard", (entity.id,)))
    if session.vehicle_id is not None:
        return Transition(session, Event("already_in_vehicle", (session.vehicle_id,)))
    return _changed(replace(session, vehicle_id=entity.id), "boarded", entity.id)


def _disembark(session: Session, name: str | None, selected_id: str | None = None) -> Transition:
    if session.vehicle_id is None:
        return Transition(session, Event("not_in_vehicle"))
    if name is not None:
        entity = _resolve(session, name, selected_id)
        if isinstance(entity, Event):
            return Transition(session, entity)
        if not has_type(session.world, entity.type_id, VEHICLE):
            return Transition(session, Event("not_vehicle", (entity.id,)))
        if entity.id != session.vehicle_id:
            return Transition(session, Event("wrong_vehicle", (entity.id,)))
    vehicle_id = session.vehicle_id
    return _changed(replace(session, vehicle_id=None), "disembarked", vehicle_id)


def _currency(session: Session) -> Entity | None:
    return next(
        (
            entity
            for entity in session.world.entities
            if has_type(session.world, entity.type_id, CURRENCY)
        ),
        None,
    )


def _merchant_for_item(session: Session, item_id: str) -> Entity | None:
    merchant_id = next(
        (
            edge.target_id
            for edge in session.world.relations
            if edge.source_id == item_id and edge.predicate_id == OFFERS
        ),
        None,
    )
    return (
        next(entity for entity in session.world.entities if entity.id == merchant_id)
        if merchant_id is not None
        else None
    )


def _without_offer(session: Session, item_id: str) -> Session:
    relations = tuple(
        edge
        for edge in session.world.relations
        if not (edge.source_id == item_id and edge.predicate_id == OFFERS)
    )
    return replace(session, world=replace(session.world, relations=relations))


def _with_offer(session: Session, item_id: str, merchant_id: str) -> Session:
    relations = (*session.world.relations, RelationIR(item_id, OFFERS, merchant_id))
    return replace(session, world=replace(session.world, relations=relations))


def _resolve_merchant(
    session: Session, name: str | None, selected_id: str | None = None
) -> Entity | Event:
    if selected_id is not None:
        merchant = _resolve(session, name or "", selected_id)
        if isinstance(merchant, Event):
            return merchant
        if not has_type(session.world, merchant.type_id, MERCHANT):
            return Event("not_merchant", (merchant.id,))
        return merchant
    if name is not None:
        merchant = _resolve(session, name)
        if isinstance(merchant, Event):
            return merchant
        if not has_type(session.world, merchant.type_id, MERCHANT):
            return Event("not_merchant", (merchant.id,))
        return merchant
    merchants = tuple(
        entity
        for entity in session.world.entities
        if has_type(session.world, entity.type_id, MERCHANT) and reachable(session, entity.id)
    )
    if not merchants:
        return Event("no_merchant")
    if len(merchants) > 1:
        return Event("ambiguous", tuple(entity.id for entity in merchants))
    return merchants[0]


def _purchase(session: Session, intent: Intent) -> Transition:
    name = intent.noun
    merchant_name = intent.indirect
    if name is None:
        return Transition(session, Event("missing_noun"))
    entity = _resolve(session, name, intent.noun_id)
    if isinstance(entity, Event):
        return Transition(session, entity)
    if not has_type(session.world, entity.type_id, MERCHANDISE):
        return Transition(session, Event("not_for_sale", (entity.id,)))
    if entity.id in session.inventory:
        return Transition(session, Event("already_carried", (entity.id,)))
    if entity.id in session.owned_ids:
        return Transition(session, Event("already_owned", (entity.id,)))
    merchants_exist = any(
        has_type(session.world, candidate.type_id, MERCHANT) for candidate in session.world.entities
    )
    merchant = _merchant_for_item(session, entity.id)
    if merchants_exist:
        if merchant is None:
            return Transition(session, Event("not_for_sale", (entity.id,)))
        if not reachable(session, merchant.id):
            return Transition(session, Event("no_merchant"))
        if merchant_name is not None:
            selected = _resolve_merchant(session, merchant_name, intent.indirect_id)
            if isinstance(selected, Event):
                return Transition(session, selected)
            if selected.id != merchant.id:
                return Transition(session, Event("wrong_merchant", (selected.id, entity.id)))
    currency = _currency(session)
    if currency is None:
        return Transition(session, Event("no_currency"))
    price = integer_property_value(session.world, entity.id, PRICE)
    balance = integer_property_value(session.world, currency.id, BALANCE)
    if balance < price:
        return Transition(session, Event("insufficient_funds", (entity.id, currency.id)))
    moved = _move(session, entity.id, None)
    if merchant is not None:
        moved = _without_offer(moved, entity.id)
        cash = integer_property_value(moved.world, merchant.id, MERCHANT_CASH, code="E125")
        moved = _set_property(moved, merchant.id, MERCHANT_CASH, cash + price)
    owned = (*session.owned_ids, entity.id)
    changed = replace(moved, owned_ids=owned)
    changed = _set_property(changed, currency.id, BALANCE, balance - price)
    entities = (
        (entity.id, currency.id, merchant.id) if merchant is not None else (entity.id, currency.id)
    )
    return _changed(changed, "purchased", *entities)


def _sell(session: Session, intent: Intent) -> Transition:
    name = intent.noun
    merchant_name = intent.indirect
    if name is None:
        return Transition(session, Event("missing_noun"))
    entity = _resolve(session, name, intent.noun_id)
    if isinstance(entity, Event):
        return Transition(session, entity)
    if not has_type(session.world, entity.type_id, MERCHANDISE):
        return Transition(session, Event("not_sellable", (entity.id,)))
    if not carried(session, entity.id) or entity.id not in session.owned_ids:
        return Transition(session, Event("not_carried", (entity.id,)))
    merchant = _resolve_merchant(session, merchant_name, intent.indirect_id)
    if isinstance(merchant, Event):
        return Transition(session, merchant)
    resale = integer_property_value(session.world, entity.id, RESALE_PRICE, code="E125")
    if resale <= 0:
        return Transition(session, Event("merchant_refuses", (merchant.id, entity.id)))
    cash = integer_property_value(session.world, merchant.id, MERCHANT_CASH, code="E125")
    if cash < resale:
        return Transition(session, Event("merchant_no_funds", (merchant.id, entity.id)))
    currency = _currency(session)
    if currency is None:
        return Transition(session, Event("no_currency"))
    balance = integer_property_value(session.world, currency.id, BALANCE)
    moved = _move(session, entity.id, session.room_id)
    moved = _with_offer(moved, entity.id, merchant.id)
    moved = replace(
        moved, owned_ids=tuple(ident for ident in moved.owned_ids if ident != entity.id)
    )
    moved = _set_property(moved, merchant.id, MERCHANT_CASH, cash - resale)
    moved = _set_property(moved, currency.id, BALANCE, balance + resale)
    return _changed(moved, "sold", entity.id, currency.id, merchant.id)


def _authored_action(session: Session, action_id: str) -> ActionIR | None:
    return next((action for action in session.world.actions if action.id == action_id), None)


def _authored_arguments(
    session: Session, intent: Intent, action: ActionIR
) -> tuple[Entity, ...] | Event:
    expected = (action.target_type_id, action.indirect_type_id)
    names = (intent.noun, intent.indirect)
    selected_ids = (intent.noun_id, intent.indirect_id)
    resolved: list[Entity] = []
    for name, selected_id, type_id in zip(names, selected_ids, expected, strict=True):
        if type_id is None:
            if name is not None:
                return Event("unknown")
            continue
        if name is None:
            return Event("missing_noun")
        entity = _resolve(session, name, selected_id)
        if isinstance(entity, Event):
            return entity
        if not has_type(session.world, entity.type_id, type_id):
            return Event("wrong_kind", (entity.id,))
        resolved.append(entity)
    return tuple(resolved)


def _perform_authored(session: Session, intent: Intent, action: ActionIR) -> Transition:
    arguments = _authored_arguments(session, intent, action)
    if isinstance(arguments, Event):
        return Transition(session, arguments)
    return Transition(session, Event("custom", tuple(entity.id for entity in arguments)))


def _dialogue_node(dialogue: DialogueIR, node_id: str) -> DialogueNodeIR:
    return next(node for node in dialogue.nodes if node.id == node_id)


def _dialogue_text(node: DialogueNodeIR) -> str:
    if not node.choices:
        return node.text
    choices = "\n".join(f"{index}. {choice.label}" for index, choice in enumerate(node.choices, 1))
    return f"{node.text}\n{choices}"


def _enter_dialogue(
    session: Session,
    dialogue: DialogueIR,
    node_id: str,
    *,
    choice_id: str | None = None,
    choice_label: str | None = None,
) -> Transition:
    node = _dialogue_node(dialogue, node_id)
    visited = session.visited_dialogue_nodes
    if node.id not in visited:
        visited = (*visited, node.id)
    ended = not node.choices
    updated = replace(
        session,
        dialogue_id=None if ended else dialogue.id,
        dialogue_node_id=None if ended else node.id,
        visited_dialogue_nodes=visited,
    )
    dialogue_step = DialogueStep(
        dialogue.id,
        dialogue.label,
        dialogue.speaker_id,
        node.id,
        node.label,
        choice_id,
        choice_label,
        ended,
    )
    return Transition(
        updated,
        Event("dialogue", (dialogue.speaker_id,)),
        (_dialogue_text(node),),
        dialogue=(dialogue_step,),
    )


def _talk(session: Session, name: str, selected_id: str | None = None) -> Transition:
    speaker = _resolve(session, name, selected_id)
    if isinstance(speaker, Event):
        return Transition(session, speaker)
    if not has_type(session.world, speaker.type_id, PERSON):
        return Transition(session, Event("wrong_kind", (speaker.id,)))
    dialogue = next(
        (item for item in session.world.dialogues if item.speaker_id == speaker.id),
        None,
    )
    if dialogue is None:
        return Transition(session, Event("no_dialogue", (speaker.id,)))
    return _enter_dialogue(session, dialogue, dialogue.start_node_id)


def _choose_dialogue(session: Session, selection: str) -> Transition:
    dialogue = next(
        (item for item in session.world.dialogues if item.id == session.dialogue_id),
        None,
    )
    if dialogue is None or session.dialogue_node_id is None:
        return Transition(session, Event("no_active_dialogue"))
    node = _dialogue_node(dialogue, session.dialogue_node_id)
    choice = None
    if selection.isdecimal():
        index = int(selection) - 1
        if 0 <= index < len(node.choices):
            choice = node.choices[index]
    else:
        normalized = canonical(selection)
        exact = [item for item in node.choices if canonical(item.label) == normalized]
        if len(exact) == 1:
            choice = exact[0]
        elif not exact:
            words = set(normalized.split())
            partial = [
                item
                for item in node.choices
                if words and words.issubset(set(canonical(item.label).split()))
            ]
            if len(partial) == 1:
                choice = partial[0]
    if choice is None:
        return Transition(session, Event("invalid_choice", (dialogue.speaker_id,)))
    if choice.target_node_id is None:
        updated = replace(session, dialogue_id=None, dialogue_node_id=None)
        dialogue_step = DialogueStep(
            dialogue.id,
            dialogue.label,
            dialogue.speaker_id,
            node.id,
            node.label,
            choice.id,
            choice.label,
            True,
        )
        return Transition(
            updated,
            Event("dialogue_end", (dialogue.speaker_id,)),
            dialogue=(dialogue_step,),
        )
    return _enter_dialogue(
        session,
        dialogue,
        choice.target_node_id,
        choice_id=choice.id,
        choice_label=choice.label,
    )


def _back_direction(session: Session) -> Intent | Event:
    if session.previous_room_id is None:
        return Event("no_previous_room")
    back_verb = next(
        (
            verb
            for verb, predicate in DIRECTION_PREDICATES.items()
            if any(
                edge.source_id == session.room_id
                and edge.predicate_id == predicate
                and edge.target_id == session.previous_room_id
                for edge in session.world.relations
            )
        ),
        None,
    )
    return Intent(back_verb) if back_verb is not None else Event("cannot_return")


def _perform(session: Session, intent: Intent) -> Transition:
    if intent.verb == "missing_direction":
        return Transition(session, Event("missing_direction"))
    if intent.verb == "invalid_direction":
        return Transition(session, Event("invalid_direction"))
    if intent.verb == "no_referent":
        return Transition(session, Event("no_referent"))
    if intent.verb == "no_indirect_referent":
        return Transition(session, Event("no_indirect_referent"))
    if intent.verb == "score":
        return Transition(session, Event("score"))
    if intent.verb == "time":
        return Transition(session, Event("time"))
    if intent.verb == "money":
        currency = _currency(session)
        return Transition(
            session,
            Event("money", (currency.id,)) if currency is not None else Event("no_currency"),
        )
    if intent.verb == "buy":
        return _purchase(session, intent)
    if intent.verb == "sell":
        return _sell(session, intent)
    if intent.verb == "board":
        return _board(session, intent.noun, intent.noun_id)
    if intent.verb == "exit_vehicle":
        return _disembark(session, intent.noun, intent.noun_id)
    if intent.verb == "look":
        return Transition(session, Event("look", (session.room_id, *visible(session))))
    if intent.verb == "inventory":
        return Transition(
            session,
            Event(
                "inventory",
                tuple(ident for ident in session.inventory if reachable(session, ident)),
            ),
        )
    if intent.verb in DIRECTION_PREDICATES:
        predicate = DIRECTION_PREDICATES[intent.verb]
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
        for door in session.world.entities:
            if has_type(session.world, door.type_id, DOOR) and _sides(session, door.id) == {
                session.room_id,
                target,
            }:
                if _state(session, door.id) != "aperto":
                    return Transition(session, Event("door_closed", (door.id,)))
        moved = session
        if session.vehicle_id is not None:
            moved = _move(session, session.vehicle_id, target)
        moved = replace(moved, room_id=target, previous_room_id=session.room_id)
        validate_session(
            moved.world, moved.inventory, moved.room_id, moved.vehicle_id, moved.owned_ids
        )
        return _perform(moved, Intent("look"))
    if intent.verb == "quit":
        return Transition(session, Event("quit"))
    if intent.verb == "unknown":
        return Transition(session, Event("unknown"))
    if intent.verb == "end_dialogue":
        if session.dialogue_id is None:
            return Transition(session, Event("no_active_dialogue"))
        dialogue = next(item for item in session.world.dialogues if item.id == session.dialogue_id)
        return Transition(
            replace(session, dialogue_id=None, dialogue_node_id=None),
            Event("dialogue_end", (dialogue.speaker_id,)),
        )
    if intent.verb == "dialogue_choice":
        return (
            _choose_dialogue(session, intent.noun)
            if intent.noun is not None
            else Transition(session, Event("invalid_choice"))
        )
    if intent.verb == "talk":
        return (
            _talk(session, intent.noun, intent.noun_id)
            if intent.noun is not None
            else Transition(session, Event("missing_noun"))
        )
    authored = _authored_action(session, intent.verb)
    if authored is not None:
        return _perform_authored(session, intent, authored)
    if not intent.noun:
        return Transition(session, Event("missing_noun"))
    entity = _resolve(session, intent.noun, intent.noun_id)
    if isinstance(entity, Event):
        return Transition(session, entity)
    if intent.verb == "examine":
        children = tuple(
            edge.source_id
            for edge in session.world.relations
            if edge.predicate_id == INSIDE
            and edge.target_id == entity.id
            and reachable(session, edge.source_id)
        )
        return Transition(session, Event("examined", (entity.id, *children)))
    if intent.verb in {"open", "close", "lock"}:
        return _opening(session, intent, entity)
    if intent.verb not in {"take", "put", "drop"}:
        return Transition(session, Event("unknown"))
    if has_type(session.world, entity.type_id, PERSON) or not any(
        has_type(session.world, entity.type_id, expected) for expected in PORTABLE
    ):
        return Transition(session, Event("not_portable", (entity.id,)))
    if intent.verb == "take":
        if entity.id in session.inventory:
            return Transition(session, Event("already_carried", (entity.id,)))
        if (
            has_type(session.world, entity.type_id, MERCHANDISE)
            and entity.id not in session.owned_ids
        ):
            return Transition(session, Event("must_buy", (entity.id,)))
        return _changed(_move(session, entity.id, None), "taken", entity.id)
    if not carried(session, entity.id):
        return Transition(session, Event("not_carried", (entity.id,)))
    if intent.verb == "drop":
        return _changed(_move(session, entity.id, session.room_id), "dropped", entity.id)
    if not intent.indirect:
        return Transition(session, Event("unknown"))
    target_entity = _resolve(session, intent.indirect, intent.indirect_id)
    if isinstance(target_entity, Event):
        return Transition(session, target_entity)
    if not has_type(session.world, target_entity.type_id, CONTAINER):
        return Transition(session, Event("not_container", (target_entity.id,)))
    if _state(session, target_entity.id) != "aperto":
        return Transition(session, Event("container_closed", (target_entity.id,)))
    parents = _parents(session)
    current = target_entity.id
    while True:
        if current == entity.id:
            return Transition(session, Event("cycle", (entity.id,)))
        if current not in parents:
            break
        current = parents[current]
    return _changed(_move(session, entity.id, target_entity.id), "put", entity.id, target_entity.id)


class _RuleHost:
    def read(self, state: Session, address: Address) -> Value:
        for prop in state.world.properties:
            if (prop.entity_id, prop.property_id) == (address.entity_id, address.property_id):
                return prop.value
        raise RuleError("Proprietà runtime assente.")

    def write(self, state: Session, address: Address, value: Value) -> Session:
        spec = next((p for p in state.world.property_specs if p.id == address.property_id), None)
        entity = next((e for e in state.world.entities if e.id == address.entity_id), None)
        if (
            spec is None
            or entity is None
            or not any(
                has_type(state.world, entity.type_id, expected) for expected in spec.owner_types
            )
            or not spec.accepts(value)
        ):
            raise RuleError("Valore non valido per la proprietà.")
        props = tuple(
            p
            for p in state.world.properties
            if (p.entity_id, p.property_id) != (address.entity_id, address.property_id)
        )
        updated = replace(
            state,
            world=replace(
                state.world,
                properties=(*props, PropertyIR(address.entity_id, address.property_id, value)),
            ),
        )
        try:
            validate_session(
                updated.world,
                updated.inventory,
                updated.room_id,
                updated.vehicle_id,
                updated.owned_ids,
            )
        except ValueError as error:
            raise RuleError(str(error)) from error
        return updated

    def relate(self, state: Session, change: RelationChange, present: bool) -> Session:
        requested = {(edge.source_id, edge.predicate_id, edge.target_id) for edge in change.edges}
        existing = {
            (edge.source_id, edge.predicate_id, edge.target_id) for edge in state.world.relations
        }
        if present:
            keys = {(source, predicate) for source, predicate, _target in requested}
            conflict = next(
                (
                    (source, predicate, target)
                    for source, predicate, target in existing
                    if (source, predicate) in keys and (source, predicate, target) not in requested
                ),
                None,
            )
            if conflict is not None:
                raise RuleError("Esiste già una destinazione diversa per questa relazione.")
            additions = tuple(
                RelationIR(edge.source_id, edge.predicate_id, edge.target_id)
                for edge in change.edges
                if (edge.source_id, edge.predicate_id, edge.target_id) not in existing
            )
            merged = (*state.world.relations, *additions)
        else:
            merged = tuple(
                edge
                for edge in state.world.relations
                if (edge.source_id, edge.predicate_id, edge.target_id) not in requested
            )
        updated = replace(state, world=replace(state.world, relations=tuple(merged)))
        try:
            validate_session(
                updated.world,
                updated.inventory,
                updated.room_id,
                updated.vehicle_id,
                updated.owned_ids,
            )
        except ValueError as error:
            raise RuleError(str(error)) from error
        return updated

    def rows(self, state: Session, table_id: str) -> tuple[tuple[Scalar, ...], ...]:
        table = next((item for item in state.world.tables if item.id == table_id), None)
        if table is None:
            raise RuleError("Tabella runtime assente.")
        return table.rows

    def change_table(self, state: Session, change: TableChange, present: bool) -> Session:
        table = next((item for item in state.world.tables if item.id == change.table_id), None)
        if (
            table is None
            or len(change.row) != len(table.columns)
            or any(
                not valid_value(column.value_kind, value)
                for column, value in zip(table.columns, change.row, strict=False)
            )
        ):
            raise RuleError("Riga non valida per la tabella.")
        if present:
            rows = (*table.rows, change.row)
        else:
            mutable = list(table.rows)
            try:
                mutable.remove(change.row)
            except ValueError:
                pass
            rows = tuple(mutable)
        changed = TableIR(table.id, table.label, table.columns, rows)
        tables = tuple(changed if item.id == table.id else item for item in state.world.tables)
        return replace(state, world=replace(state.world, tables=tables))

    def perform(self, state: Session, action: ActionCall) -> ActionResult[Session, Event]:
        labels = {e.id: e.label for e in state.world.entities}
        transition = _perform(
            state,
            Intent(
                action.action_id,
                labels.get(action.target_id) if action.target_id else None,
                labels.get(action.indirect_id) if action.indirect_id else None,
            ),
        )
        success = transition.event.kind in {
            "look",
            "inventory",
            "taken",
            "opened",
            "closed",
            "lock_success",
            "put",
            "dropped",
            "examined",
            "custom",
            "boarded",
            "disembarked",
            "purchased",
            "sold",
        }
        return ActionResult(transition.session, success, (transition.event,))


def _step(session: Session, intent: Intent) -> Transition:
    if intent.verb in {"dialogue_choice", "end_dialogue", "talk"}:
        if session.dialogue_id is not None and intent.verb == "talk":
            dialogue = next(
                item for item in session.world.dialogues if item.id == session.dialogue_id
            )
            return Transition(session, Event("dialogue_active", (dialogue.speaker_id,)))
        return _perform(session, intent)
    if session.dialogue_id is not None and intent.verb != "quit":
        dialogue = next(item for item in session.world.dialogues if item.id == session.dialogue_id)
        return Transition(session, Event("dialogue_active", (dialogue.speaker_id,)))
    if intent.verb == "back":
        backward = _back_direction(session)
        if isinstance(backward, Event):
            return Transition(session, backward)
        intent = backward
    authored = _authored_action(session, intent.verb)
    if (
        not session.world.rules
        or intent.verb in {"quit", "unknown"}
        or (
            authored is None
            and intent.verb
            not in {
                "look",
                "inventory",
                "north",
                "south",
                "east",
                "west",
                "northeast",
                "southeast",
                "southwest",
                "northwest",
                "up",
                "down",
                "inward",
                "outward",
                "exit_vehicle",
            }
            and not intent.noun
        )
    ):
        return _perform(session, intent)
    refs: list[str | None] = []
    if authored is not None:
        arguments = _authored_arguments(session, intent, authored)
        if isinstance(arguments, Event):
            return Transition(session, arguments)
        refs.extend(entity.id for entity in arguments)
        refs.extend([None] * (2 - len(refs)))
    else:
        for name, selected_id in zip(
            (intent.noun, intent.indirect),
            (intent.noun_id, intent.indirect_id),
            strict=True,
        ):
            if name is None:
                refs.append(None)
            else:
                resolved = _resolve(session, name, selected_id)
                if isinstance(resolved, Event):
                    return Transition(session, resolved)
                refs.append(resolved.id)
    execution = execute(session, ActionCall(intent.verb, *refs), session.world.rules, _RuleHost())
    outputs = execution.outputs
    if execution.value is not None:
        value = execution.value
        outputs = (*outputs, "vero" if value is True else "falso" if value is False else str(value))
    event = next((item for item in reversed(outputs) if isinstance(item, Event)), Event("rule"))
    return Transition(execution.state, event, outputs, execution.trace, execution.value)


def _ambiguity_argument(
    session: Session, intent: Intent, candidates: tuple[str, ...]
) -> Literal["noun", "indirect"]:
    for argument, name, selected_id in (
        ("noun", intent.noun, intent.noun_id),
        ("indirect", intent.indirect, intent.indirect_id),
    ):
        if name is None or selected_id is not None:
            continue
        resolved = _resolve(session, name)
        if isinstance(resolved, Event) and resolved.kind == "ambiguous":
            if resolved.entities == candidates:
                return "noun" if argument == "noun" else "indirect"
    return "indirect" if intent.verb == "sell" else "noun"


def _remember_ambiguity(session: Session, intent: Intent, transition: Transition) -> Transition:
    if transition.event.kind != "ambiguous" or not transition.event.entities:
        return transition
    clarification = Clarification(
        intent,
        _ambiguity_argument(session, intent, transition.event.entities),
        transition.event.entities,
    )
    return replace(transition, session=replace(transition.session, clarification=clarification))


def _clarification_choice(session: Session, selection: str) -> str | None:
    clarification = session.clarification
    assert clarification is not None
    if selection.isdecimal():
        index = int(selection) - 1
        return (
            clarification.candidates[index] if 0 <= index < len(clarification.candidates) else None
        )
    normalized = canonical(selection)
    entities = {
        entity.id: entity
        for entity in session.world.entities
        if entity.id in clarification.candidates
    }
    exact = {entity.id for entity in entities.values() if canonical(entity.label) == normalized}
    exact.update(
        synonym.target_id
        for synonym in session.world.synonyms
        if synonym.target_id in entities and canonical(synonym.alias) == normalized
    )
    if len(exact) == 1:
        return next(iter(exact))
    if exact:
        return None
    words = set(normalized.split())
    partial = {
        entity.id
        for entity in entities.values()
        if words and words.issubset(set(canonical(entity.label).split()))
    }
    partial.update(
        synonym.target_id
        for synonym in session.world.synonyms
        if synonym.target_id in entities
        and words
        and words.issubset(set(canonical(synonym.alias).split()))
    )
    return next(iter(partial)) if len(partial) == 1 else None


def _resume_clarification(session: Session, selection: str | None) -> Transition:
    clarification = session.clarification
    assert clarification is not None
    if not selection:
        return Transition(session, Event("invalid_clarification", clarification.candidates))
    selected_id = _clarification_choice(session, selection)
    if selected_id is None:
        return Transition(session, Event("invalid_clarification", clarification.candidates))
    intent = (
        replace(clarification.intent, noun_id=selected_id)
        if clarification.argument == "noun"
        else replace(clarification.intent, indirect_id=selected_id)
    )
    cleared = replace(session, clarification=None)
    transition = _remember_ambiguity(cleared, intent, _step(cleared, intent))
    return _remember_reference(cleared, intent, transition)


_PRONOUNS = frozenset({"esso", "essa", "questo", "questa", "quello", "quella", "it"})
_INDIRECT_PRONOUNS = frozenset({"ci"})


def _with_pronoun(session: Session, intent: Intent) -> Intent:
    for argument in ("noun", "indirect"):
        name = intent.noun if argument == "noun" else intent.indirect
        if name is None:
            continue
        normalized = canonical(name)
        if normalized in _PRONOUNS:
            referent_id = (
                session.indirect_pronoun_id
                if argument == "indirect" and session.indirect_pronoun_id is not None
                else session.pronoun_id
            )
            missing = "no_referent"
        elif argument == "indirect" and normalized in _INDIRECT_PRONOUNS:
            referent_id = session.indirect_pronoun_id
            missing = "no_indirect_referent"
        else:
            continue
        if referent_id is None:
            return Intent(missing)
        entity = next(
            (candidate for candidate in session.world.entities if candidate.id == referent_id),
            None,
        )
        if entity is None:
            return Intent(missing)
        intent = (
            replace(intent, noun=entity.label, noun_id=entity.id)
            if argument == "noun"
            else replace(intent, indirect=entity.label, indirect_id=entity.id)
        )
    return intent


def _remember_reference(session: Session, intent: Intent, transition: Transition) -> Transition:
    if intent.noun is None or transition.event.kind not in {
        "taken",
        "opened",
        "closed",
        "lock_success",
        "put",
        "dropped",
        "examined",
        "custom",
        "dialogue",
        "boarded",
        "disembarked",
        "purchased",
        "sold",
    }:
        return transition
    if intent.noun_id is not None:
        entity_id = intent.noun_id
    else:
        resolved = _resolve(session, intent.noun)
        if isinstance(resolved, Event):
            return transition
        entity_id = resolved.id
    indirect_id = transition.session.indirect_pronoun_id
    if intent.indirect is not None:
        if intent.indirect_id is not None:
            indirect_id = intent.indirect_id
        else:
            resolved_indirect = _resolve(session, intent.indirect)
            if not isinstance(resolved_indirect, Event):
                indirect_id = resolved_indirect.id
    return replace(
        transition,
        session=replace(
            transition.session,
            pronoun_id=entity_id,
            indirect_pronoun_id=indirect_id,
        ),
    )


def parse_session_command(session: Session, text: str) -> Intent:
    normalized = canonical(text)
    if session.clarification is not None:
        if normalized in {"annulla", "annulla chiarimento", "cancel"}:
            return Intent("cancel_clarification")
        if normalized.isdecimal():
            return Intent("clarify", normalized)
    intent = parse_command(
        text,
        session.world.actions,
        dialogue_enabled=bool(session.world.dialogues),
        scene_enabled=bool(session.world.scenes),
        vehicle_enabled=any(
            has_type(session.world, entity.type_id, VEHICLE) for entity in session.world.entities
        ),
        commerce_enabled=any(
            has_type(session.world, entity.type_id, CURRENCY) for entity in session.world.entities
        ),
    )
    if session.clarification is not None and intent.verb == "unknown":
        return Intent("clarify", normalized or None)
    return _with_pronoun(session, intent)


_TURNLESS_EVENTS = {
    "unknown",
    "missing_noun",
    "ambiguous",
    "invalid_clarification",
    "clarification_cancelled",
    "no_referent",
    "no_indirect_referent",
    "missing_direction",
    "invalid_direction",
    "quit",
    "score",
    "time",
    "money",
    "invalid_choice",
    "dialogue_active",
    "no_active_dialogue",
}


def _advance_scenes(transition: Transition) -> Transition:
    session = transition.session
    turn = session.turn + 1
    active = list(session.active_scene_ids)
    completed = list(session.completed_scene_ids)
    score = session.score
    score_log = list(session.score_log)
    scene_steps: list[SceneStep] = []
    texts: list[str] = []

    for scene in session.world.scenes:
        if scene.start_turn == turn and scene.id not in active and scene.id not in completed:
            active.append(scene.id)
            texts.append(scene.start_text)
            scene_steps.append(SceneStep(scene.id, scene.label, "iniziata", turn))
    for scene in session.world.scenes:
        if scene.end_turn == turn and scene.id in active:
            active.remove(scene.id)
            completed.append(scene.id)
            texts.append(scene.end_text)
            score += scene.points
            if scene.points:
                score_log.append(ScoreEntry(scene.id, scene.label, scene.points, turn))
            scene_steps.append(SceneStep(scene.id, scene.label, "terminata", turn, scene.points))

    updated = replace(
        session,
        turn=turn,
        score=score,
        active_scene_ids=tuple(active),
        completed_scene_ids=tuple(completed),
        score_log=tuple(score_log),
    )
    if not texts:
        return replace(transition, session=updated)
    outputs = transition.outputs or (transition.event,)
    return replace(
        transition,
        session=updated,
        outputs=(*outputs, *texts),
        scenes=tuple(scene_steps),
    )


def step(session: Session, intent: Intent, *, advance_time: bool = True) -> Transition:
    if session.clarification is not None and intent.verb == "clarify":
        transition = _resume_clarification(session, intent.noun)
    elif session.clarification is not None and intent.verb == "cancel_clarification":
        transition = Transition(
            replace(session, clarification=None),
            Event("clarification_cancelled"),
        )
    else:
        base = (
            replace(session, clarification=None) if session.clarification is not None else session
        )
        transition = _remember_ambiguity(base, intent, _step(base, intent))
        transition = _remember_reference(base, intent, transition)
    if (
        not advance_time
        or not transition.session.world.scenes
        or transition.event.kind in _TURNLESS_EVENTS
    ):
        return transition
    return _advance_scenes(transition)
