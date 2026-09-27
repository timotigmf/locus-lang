"""AST del sottoinsieme S0; nessun oggetto runtime."""

from dataclasses import dataclass

from locus.diagnostics import Span
from locus.rule_model import Condition, EffectKind, Phase
from locus.schema import Value, ValueKind


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
class Relation:
    subject: str
    predicate: str
    target: str
    span: Span


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
class PropertyReference:
    entity_name: str
    property_name: str


@dataclass(frozen=True, slots=True)
class ActionSyntax:
    name: str
    target: str | None = None
    indirect: str | None = None


@dataclass(frozen=True, slots=True)
class EffectSyntax:
    kind: EffectKind
    value: Value | None
    reference: PropertyReference | None
    action: ActionSyntax | None
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
