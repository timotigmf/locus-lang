"""Contratti del motore di regole, indipendenti da sintassi e dominio."""

from dataclasses import dataclass
from typing import Generic, Literal, TypeVar

from locus.schema import Value

Ref = TypeVar("Ref")
Phase = Literal["prima", "invece", "verifica", "esegui", "dopo", "descrivi"]
Operator = Literal[
    "vero", "falso", "uguale", "diverso", "maggiore", "minore", "almeno", "massimo", "e", "o", "non"
]
EffectKind = Literal[
    "dì",
    "imposta",
    "aumenta",
    "continua",
    "interrompi",
    "fallisci",
    "sostituisci",
    "restituisci",
    "crea_relazione",
    "rimuovi_relazione",
]


@dataclass(frozen=True, slots=True)
class Condition(Generic[Ref]):
    operator: Operator
    reference: Ref | None = None
    value: Value | None = None
    operands: tuple["Condition[Ref]", ...] = ()


@dataclass(frozen=True, slots=True)
class Address:
    entity_id: str
    property_id: str


@dataclass(frozen=True, slots=True)
class ActionCall:
    action_id: str
    target_id: str | None = None
    indirect_id: str | None = None


@dataclass(frozen=True, slots=True)
class RelationEdge:
    source_id: str
    predicate_id: str
    target_id: str


@dataclass(frozen=True, slots=True)
class RelationChange:
    edges: tuple[RelationEdge, ...]


@dataclass(frozen=True, slots=True)
class Origin:
    source: str
    line: int
    column: int


@dataclass(frozen=True, slots=True)
class Effect:
    kind: EffectKind
    value: Value | None = None
    address: Address | None = None
    action: ActionCall | None = None
    relation: RelationChange | None = None


@dataclass(frozen=True, slots=True)
class RuleIR:
    id: str
    name: str
    phase: Phase
    selector: ActionCall
    priority: int
    order: int
    condition: Condition[Address]
    effects: tuple[Effect, ...]
    origin: Origin


@dataclass(frozen=True, slots=True)
class Trace:
    rule_id: str
    name: str
    phase: Phase
    priority: int
    condition: bool
    outcome: str
    origin: Origin
