"""Contratto interno indipendente dalla grammatica italiana."""

from dataclasses import dataclass

from locus.rule_model import RuleIR
from locus.schema import PropertySpec, Scalar, Value, ValueKind

IR_VERSION = 16


@dataclass(frozen=True, slots=True)
class TypeIR:
    id: str
    label: str
    parent_id: str | None = None


@dataclass(frozen=True, slots=True)
class ActionIR:
    id: str
    label: str
    commands: tuple[str, ...]
    target_type_id: str | None = None
    indirect_type_id: str | None = None
    separators: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class EntityIR:
    id: str
    label: str
    type_id: str


@dataclass(frozen=True, slots=True)
class RelationIR:
    source_id: str
    predicate_id: str
    target_id: str


@dataclass(frozen=True, slots=True)
class PropertyIR:
    entity_id: str
    property_id: str
    value: Value


@dataclass(frozen=True, slots=True)
class SynonymIR:
    alias: str
    target_id: str


@dataclass(frozen=True, slots=True)
class TableColumnIR:
    id: str
    label: str
    value_kind: ValueKind


@dataclass(frozen=True, slots=True)
class TableIR:
    id: str
    label: str
    columns: tuple[TableColumnIR, ...]
    rows: tuple[tuple[Scalar, ...], ...] = ()


@dataclass(frozen=True, slots=True)
class DialogueChoiceIR:
    id: str
    label: str
    target_node_id: str | None


@dataclass(frozen=True, slots=True)
class DialogueNodeIR:
    id: str
    label: str
    text: str
    choices: tuple[DialogueChoiceIR, ...] = ()


@dataclass(frozen=True, slots=True)
class DialogueIR:
    id: str
    label: str
    speaker_id: str
    start_node_id: str
    nodes: tuple[DialogueNodeIR, ...]


@dataclass(frozen=True, slots=True)
class ProgramIR:
    version: int
    entities: tuple[EntityIR, ...]
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
    dialogues: tuple[DialogueIR, ...] = ()
