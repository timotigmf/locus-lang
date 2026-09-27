"""Istanziazione minima: il runtime non conosce il linguaggio sorgente."""

from dataclasses import dataclass

from locus.diagnostics import canonical
from locus.graph import cycle_node
from locus.ir import IR_VERSION, ActionIR, ProgramIR, PropertyIR, RelationIR, SynonymIR, TypeIR
from locus.rule_model import RuleIR
from locus.schema import PropertySpec, command_forms_conflict, is_subtype, valid_command_form


@dataclass(frozen=True, slots=True)
class Entity:
    id: str
    label: str
    type_id: str


@dataclass(frozen=True, slots=True)
class World:
    entities: tuple[Entity, ...]
    relations: tuple[RelationIR, ...] = ()
    property_specs: tuple[PropertySpec, ...] = ()
    properties: tuple[PropertyIR, ...] = ()
    rules: tuple[RuleIR, ...] = ()
    entry_id: str | None = None
    synonyms: tuple[SynonymIR, ...] = ()
    title: str | None = None
    author: str | None = None
    types: tuple[TypeIR, ...] = ()
    actions: tuple[ActionIR, ...] = ()


def has_type(world: World, actual: str, expected: str) -> bool:
    return is_subtype(actual, expected, {item.id: item.parent_id for item in world.types})


def instantiate(program: ProgramIR) -> World:
    if program.version != IR_VERSION:
        raise ValueError(f"Versione IR non supportata: {program.version}.")
    if len({entity.id for entity in program.entities}) != len(program.entities):
        raise ValueError("Identificatori di entità duplicati nell'IR.")
    identifiers = {entity.id for entity in program.entities}
    inferred_type_ids = dict.fromkeys(
        (
            *(entity.type_id for entity in program.entities),
            *(owner for spec in program.property_specs for owner in spec.owner_types),
            *(
                type_id
                for action in program.actions
                for type_id in (action.target_type_id, action.indirect_type_id)
                if type_id is not None
            ),
        )
    )
    types = program.types or tuple(TypeIR(ident, ident) for ident in inferred_type_ids)
    type_ids = {item.id for item in types}
    if len(type_ids) != len(types):
        raise ValueError("Identificatori di tipo duplicati nell'IR.")
    parents = {item.id: item.parent_id for item in types}
    type_labels = [canonical(item.label) for item in types]
    if (
        any(
            not item.id.strip() or not label for item, label in zip(types, type_labels, strict=True)
        )
        or len(set(type_labels)) != len(type_labels)
        or any(parent is not None and parent not in type_ids for parent in parents.values())
    ):
        raise ValueError("Gerarchia dei tipi non valida nell'IR.")
    hierarchy = {child: parent for child, parent in parents.items() if parent is not None}
    if cycle_node(hierarchy) is not None:
        raise ValueError("La gerarchia dei tipi contiene un ciclo nell'IR.")
    if any(entity.type_id not in type_ids for entity in program.entities):
        raise ValueError("Tipo di entità assente nell'IR.")
    if any(owner not in type_ids for spec in program.property_specs for owner in spec.owner_types):
        raise ValueError("Tipo proprietario assente nell'IR.")
    action_ids = {action.id for action in program.actions}
    action_labels = [canonical(action.label) for action in program.actions]
    commands = [command for action in program.actions for command in action.commands]
    if (
        len(action_ids) != len(program.actions)
        or len(set(action_labels)) != len(action_labels)
        or command_forms_conflict(tuple(commands))
        or any(
            not action.id.strip()
            or not canonical(action.label)
            or not action.commands
            or any(
                command != canonical(command) or not valid_command_form(command)
                for command in action.commands
            )
            or (action.target_type_id is None and action.indirect_type_id is not None)
            or (action.indirect_type_id is None and bool(action.separators))
            or (action.indirect_type_id is not None and not action.separators)
            or len(set(action.separators)) != len(action.separators)
            or any(
                separator != canonical(separator)
                or len(separator.split()) != 1
                or not separator.isalpha()
                or separator in action.commands
                for separator in action.separators
            )
            or any(
                type_id is not None and type_id not in type_ids
                for type_id in (action.target_type_id, action.indirect_type_id)
            )
            for action in program.actions
        )
    ):
        raise ValueError("Catalogo delle azioni non valido nell'IR.")
    if any(
        edge.source_id not in identifiers or edge.target_id not in identifiers
        for edge in program.relations
    ):
        raise ValueError("Riferimento a entità assente nell'IR.")
    if program.entry_id is not None and program.entry_id not in identifiers:
        raise ValueError("Entità iniziale assente nell’IR.")
    aliases = [canonical(item.alias) for item in program.synonyms]
    labels = {canonical(entity.label) for entity in program.entities}
    if (
        any(not alias for alias in aliases)
        or len(set(aliases)) != len(aliases)
        or any(alias in labels for alias in aliases)
        or any(item.target_id not in identifiers for item in program.synonyms)
    ):
        raise ValueError("Vocabolario non valido nell'IR.")
    keys = {(edge.source_id, edge.predicate_id) for edge in program.relations}
    if len(keys) != len(program.relations):
        raise ValueError("Relazioni duplicate o in conflitto nell'IR.")
    specs = {spec.id: spec for spec in program.property_specs}
    if len(specs) != len(program.property_specs):
        raise ValueError("Schemi di proprietà duplicati nell'IR.")
    entities = {entity.id: entity for entity in program.entities}
    seen: set[tuple[str, str]] = set()
    for prop in program.properties:
        key = (prop.entity_id, prop.property_id)
        if key in seen or prop.entity_id not in entities or prop.property_id not in specs:
            raise ValueError("Proprietà duplicata o riferimento assente nell'IR.")
        spec = specs[prop.property_id]
        if not any(
            is_subtype(entities[prop.entity_id].type_id, owner, parents)
            for owner in spec.owner_types
        ) or not spec.accepts(prop.value):
            raise ValueError("Valore di proprietà non valido nell'IR.")
        seen.add(key)
    return World(
        entities=tuple(Entity(item.id, item.label, item.type_id) for item in program.entities),
        relations=program.relations,
        property_specs=program.property_specs,
        properties=program.properties,
        rules=program.rules,
        entry_id=program.entry_id,
        synonyms=program.synonyms,
        title=program.title,
        author=program.author,
        types=types,
        actions=program.actions,
    )
