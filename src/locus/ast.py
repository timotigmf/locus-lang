"""AST del sottoinsieme S0; nessun oggetto runtime."""

from dataclasses import dataclass

from locus.diagnostics import Span
from locus.rule_model import Condition, EffectKind, Phase
from locus.schema import Scalar, Value, ValueKind


@dataclass(frozen=True, slots=True)
class Declaration:
    name: str
    kind: str
    span: Span
    location: str | None = None


@dataclass(frozen=True, slots=True)
class KindDeclaration:
    name: str
    parent: str
    span: Span


@dataclass(frozen=True, slots=True)
class ActionDeclaration:
    name: str
    commands: tuple[str, ...]
    target_kind: str | None
    indirect_kind: str | None
    separators: tuple[str, ...]
    span: Span


@dataclass(frozen=True, slots=True)
class Relation:
    subject: str
    predicate: str
    target: str
    span: Span
    one_way: bool = False


@dataclass(frozen=True, slots=True)
class PropertyDeclaration:
    name: str
    value_kind: ValueKind
    span: Span


@dataclass(frozen=True, slots=True)
class Assignment:
    subject: str
    property_name: str
    value: Value
    span: Span


@dataclass(frozen=True, slots=True)
class TableColumnDeclaration:
    name: str
    value_kind: ValueKind
    span: Span


@dataclass(frozen=True, slots=True)
class TableRowDeclaration:
    values: tuple[Scalar, ...]
    span: Span


@dataclass(frozen=True, slots=True)
class TableDeclaration:
    name: str
    columns: tuple[TableColumnDeclaration, ...]
    rows: tuple[TableRowDeclaration, ...]
    span: Span


@dataclass(frozen=True, slots=True)
class DialogueChoiceDeclaration:
    label: str
    target: str | None
    span: Span


@dataclass(frozen=True, slots=True)
class DialogueNodeDeclaration:
    name: str
    text: str
    choices: tuple[DialogueChoiceDeclaration, ...]
    span: Span


@dataclass(frozen=True, slots=True)
class DialogueDeclaration:
    name: str
    speaker: str
    nodes: tuple[DialogueNodeDeclaration, ...]
    span: Span


@dataclass(frozen=True, slots=True)
class SceneDeclaration:
    name: str
    start_turn: int
    end_turn: int
    start_text: str
    end_text: str
    points: int
    span: Span


@dataclass(frozen=True, slots=True)
class PropertyReference:
    entity_name: str
    property_name: str


@dataclass(frozen=True, slots=True)
class ActionSyntax:
    name: str
    target: str | None = None
    indirect: str | None = None


@dataclass(frozen=True, slots=True)
class RelationSyntax:
    name: str
    source: str
    target: str
    one_way: bool = False


@dataclass(frozen=True, slots=True)
class TableRowSyntax:
    table_name: str
    values: tuple[Scalar, ...]


@dataclass(frozen=True, slots=True)
class EffectSyntax:
    kind: EffectKind
    value: Value | None
    reference: PropertyReference | None
    action: ActionSyntax | None
    relation: RelationSyntax | None
    table_row: TableRowSyntax | None
    span: Span


@dataclass(frozen=True, slots=True)
class Rule:
    name: str
    phase: Phase
    action: ActionSyntax
    priority: int
    condition: Condition[PropertyReference]
    effects: tuple[EffectSyntax, ...]
    span: Span


@dataclass(frozen=True, slots=True)
class Inclusion:
    path: str
    span: Span


@dataclass(frozen=True, slots=True)
class EntryPoint:
    name: str
    span: Span


@dataclass(frozen=True, slots=True)
class Metadata:
    name: str
    value: str
    span: Span


@dataclass(frozen=True, slots=True)
class Vocabulary:
    alias: str
    target: str
    span: Span


@dataclass(frozen=True, slots=True)
class Program:
    declarations: tuple[Declaration, ...]
    relations: tuple[Relation, ...] = ()
    properties: tuple[PropertyDeclaration, ...] = ()
    assignments: tuple[Assignment, ...] = ()
    rules: tuple[Rule, ...] = ()
    inclusions: tuple[Inclusion, ...] = ()
    entries: tuple[EntryPoint, ...] = ()
    source_order: tuple[str, ...] = ()
    metadata: tuple[Metadata, ...] = ()
    vocabulary: tuple[Vocabulary, ...] = ()
    kinds: tuple[KindDeclaration, ...] = ()
    actions: tuple[ActionDeclaration, ...] = ()
    tables: tuple[TableDeclaration, ...] = ()
    dialogues: tuple[DialogueDeclaration, ...] = ()
    scenes: tuple[SceneDeclaration, ...] = ()
