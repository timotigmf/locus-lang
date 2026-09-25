"""Schemi di dominio iniettati nel compilatore, indipendenti dalla IF."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RelationSpec:
    id: str
    source_type: str
    target_type: str
    reverse_operands: bool = False
    inverse_id: str | None = None
