"""AST del sottoinsieme S0; nessun oggetto runtime."""

from dataclasses import dataclass

from locus.diagnostics import Span


@dataclass(frozen=True, slots=True)
class Declaration:
    name: str
    kind: str
    span: Span


@dataclass(frozen=True, slots=True)
class Program:
    declarations: tuple[Declaration, ...]
