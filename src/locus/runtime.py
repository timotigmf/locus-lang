"""Istanziazione minima: il runtime non conosce il linguaggio sorgente."""

from dataclasses import dataclass
from typing import Any

from locus.diagnostics import canonical
from locus.graph import cycle_node
from locus.ir import (
    IR_VERSION,
    ActionIR,
    ProgramIR,
    PropertyIR,
    RelationIR,
    SynonymIR,
    TableIR,
    TypeIR,
)
from locus.rule_model import Condition, RuleIR
from locus.schema import (
    PropertySpec,
    command_forms_conflict,
    is_subtype,
    separator_forms_conflict,
    valid_command_form,
    valid_separator_form,
    valid_value,
)


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
    tables: tuple[TableIR, ...] = ()


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
            or separator_forms_conflict(action.separators)
            or any(
                separator != canonical(separator)
                or not valid_separator_form(separator)
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
    tables_by_id = {table.id: table for table in program.tables}
    table_ids = set(tables_by_id)
    table_labels = [canonical(table.label) for table in program.tables]
    if (
        len(program.tables) > 64
        or len(table_ids) != len(program.tables)
        or len(set(table_labels)) != len(table_labels)
    ):
        raise ValueError("Identificatori o nomi di tabella duplicati nell'IR.")
    for table in program.tables:
        column_ids = [column.id for column in table.columns]
        column_labels = [canonical(column.label) for column in table.columns]
        if (
            not table.id.strip()
            or not canonical(table.label)
            or not 1 <= len(table.columns) <= 64
            or len(set(column_ids)) != len(column_ids)
            or len(set(column_labels)) != len(column_labels)
            or any(
                not column.id.strip()
                or not canonical(column.label)
                or column.value_kind not in {"numero", "testo", "logico"}
                for column in table.columns
            )
            or len(table.rows) > 10_000
            or any(
                len(row) != len(table.columns)
                or any(
                    not valid_value(column.value_kind, value)
                    for column, value in zip(table.columns, row, strict=False)
                )
                for row in table.rows
            )
        ):
            raise ValueError("Schema o righe di tabella non validi nell'IR.")

    def validate_table_condition(condition: Condition[Any]) -> None:
        if condition.operator == "contiene_riga":
            table = tables_by_id.get(condition.table_id or "")
            if (
                table is None
                or len(condition.row) != len(table.columns)
                or any(
                    not valid_value(column.value_kind, value)
                    for column, value in zip(table.columns, condition.row, strict=False)
                )
            ):
                raise ValueError("Condizione di tabella non valida nell'IR.")
        elif condition.table_id is not None or condition.row:
            raise ValueError("Condizione di tabella associata all'operatore errato nell'IR.")
        for child in condition.operands:
            validate_table_condition(child)

    for rule in program.rules:
        validate_table_condition(rule.condition)
        for effect in rule.effects:
            relation = effect.relation
            if effect.kind in {"crea_relazione", "rimuovi_relazione"}:
                if relation is None or not relation.edges:
                    raise ValueError("Mutazione di relazione incompleta nell'IR.")
                relation_keys = {(edge.source_id, edge.predicate_id) for edge in relation.edges}
                if len(relation_keys) != len(relation.edges) or any(
                    edge.source_id not in identifiers
                    or edge.target_id not in identifiers
                    or edge.source_id == edge.target_id
                    or not edge.predicate_id.strip()
                    for edge in relation.edges
                ):
                    raise ValueError("Mutazione di relazione non valida nell'IR.")
            elif relation is not None:
                raise ValueError("Mutazione di relazione associata all'effetto errato nell'IR.")
            table_change = effect.table
            if effect.kind in {"aggiungi_riga", "rimuovi_riga"}:
                changed_table = tables_by_id.get(table_change.table_id if table_change else "")
                if (
                    table_change is None
                    or changed_table is None
                    or len(table_change.row) != len(changed_table.columns)
                    or any(
                        not valid_value(column.value_kind, value)
                        for column, value in zip(
                            changed_table.columns, table_change.row, strict=False
                        )
                    )
                ):
                    raise ValueError("Mutazione di tabella incompleta nell'IR.")
            elif table_change is not None:
                raise ValueError("Mutazione di tabella associata all'effetto errato nell'IR.")
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
        tables=program.tables,
    )
