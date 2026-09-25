"""Contratto interno indipendente dalla grammatica italiana."""

from dataclasses import dataclass

from locus.rule_model import RuleIR
from locus.schema import PropertySpec, Value

IR_VERSION = 4


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
class ProgramIR:
    version: int
    entities: tuple[EntityIR, ...]
    relations: tuple[RelationIR, ...] = ()
    property_specs: tuple[PropertySpec, ...] = ()
    properties: tuple[PropertyIR, ...] = ()
    rules: tuple[RuleIR, ...] = ()
