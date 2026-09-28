"""Transizioni IF pure con contenimento, stati e intenti a due oggetti."""

from dataclasses import dataclass, replace
from typing import Literal

from locus.diagnostics import canonical
from locus.ir import ActionIR, DialogueIR, DialogueNodeIR, PropertyIR, RelationIR, TableIR
from locus.player import Intent
from locus.rule_model import ActionCall, Address, RelationChange, TableChange, Trace
from locus.rules import ActionResult, RuleError, execute
from locus.runtime import Entity, World, has_type
from locus.schema import Scalar, Value, valid_value
from locus.stdlib import (
    CONTAINER,
    DOOR,
    EAST,
    INSIDE,
    NORTH,
    OPENABLE,
    PERSON,
    PORTABLE,
    ROOM,
    SIDE_A,
    SIDE_B,
    SOUTH,
    STATE,
    UNLOCKS,
    VISIBLE,
    WEST,
)
from locus.stdlib.validation import property_value, validate_world

EventKind = Literal[
    "rule",
    "look",
    "inventory",
    "taken",
    "already_carried",
    "not_here",
    "not_portable",
    "ambiguous",
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
]


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
        and reachable(session, entity.id)
        and not carried(session, entity.id)
    )


def _resolve(session: Session, name: str) -> Entity | Event:
    in_scope = [entity for entity in session.world.entities if reachable(session, entity.id)]
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
    validate_world(session.world, session.inventory)
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


def _key_error(session: Session, target_id: str, name: str) -> Event | None:
    key = _resolve(session, name)
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
        error = _key_error(session, entity.id, intent.indirect)
        if error:
            return Transition(session, error)
    elif state == "bloccato" or intent.verb == "lock":
        return Transition(session, Event("locked", (entity.id,)))
    value = "bloccato" if intent.verb == "lock" else "aperto"
    kind: EventKind = "lock_success" if intent.verb == "lock" else "opened"
    return _changed(_set_state(session, entity.id, value), kind, entity.id)


def _authored_action(session: Session, action_id: str) -> ActionIR | None:
    return next((action for action in session.world.actions if action.id == action_id), None)


def _authored_arguments(
    session: Session, intent: Intent, action: ActionIR
) -> tuple[Entity, ...] | Event:
    expected = (action.target_type_id, action.indirect_type_id)
    names = (intent.noun, intent.indirect)
    resolved: list[Entity] = []
    for name, type_id in zip(names, expected, strict=True):
        if type_id is None:
            if name is not None:
                return Event("unknown")
            continue
        if name is None:
            return Event("missing_noun")
        entity = _resolve(session, name)
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


def _talk(session: Session, name: str) -> Transition:
    speaker = _resolve(session, name)
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


def _perform(session: Session, intent: Intent) -> Transition:
    if intent.verb == "score":
        return Transition(session, Event("score"))
    if intent.verb == "time":
        return Transition(session, Event("time"))
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
    directions = {"north": NORTH, "south": SOUTH, "east": EAST, "west": WEST}
    if intent.verb in directions:
        predicate = directions[intent.verb]
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
        moved = replace(session, room_id=target)
        validate_world(moved.world, moved.inventory)
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
            _talk(session, intent.noun)
            if intent.noun is not None
            else Transition(session, Event("missing_noun"))
        )
    authored = _authored_action(session, intent.verb)
    if authored is not None:
        return _perform_authored(session, intent, authored)
    if not intent.noun:
        return Transition(session, Event("missing_noun"))
    entity = _resolve(session, intent.noun)
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
        return _changed(_move(session, entity.id, None), "taken", entity.id)
    if not carried(session, entity.id):
        return Transition(session, Event("not_carried", (entity.id,)))
    if intent.verb == "drop":
        return _changed(_move(session, entity.id, session.room_id), "dropped", entity.id)
    if not intent.indirect:
        return Transition(session, Event("unknown"))
    target_entity = _resolve(session, intent.indirect)
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
            validate_world(updated.world, updated.inventory)
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
            validate_world(updated.world, updated.inventory)
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
    authored = _authored_action(session, intent.verb)
    if (
        not session.world.rules
        or intent.verb in {"quit", "unknown"}
        or (
            authored is None
            and intent.verb not in {"look", "inventory", "north", "south", "east", "west"}
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
        for name in (intent.noun, intent.indirect):
            if name is None:
                refs.append(None)
            else:
                resolved = _resolve(session, name)
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


_TURNLESS_EVENTS = {
    "unknown",
    "missing_noun",
    "ambiguous",
    "quit",
    "score",
    "time",
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
    transition = _step(session, intent)
    if (
        not advance_time
        or not transition.session.world.scenes
        or transition.event.kind in _TURNLESS_EVENTS
    ):
        return transition
    return _advance_scenes(transition)
