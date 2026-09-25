"""AST del sottoinsieme S0; nessun oggetto runtime."""

from dataclasses import dataclass

from locus.diagnostics import Span
from locus.schema import Value, ValueKind


@dataclass(frozen=True, slots=True)
class Declaration:
    name: str
    kind: str
    span: Span
    location: str | None = None


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
class Program:
    declarations: tuple[Declaration, ...]
    relations: tuple[Relation, ...] = ()
    properties: tuple[PropertyDeclaration, ...] = ()
    assignments: tuple[Assignment, ...] = ()
