"""Analisi e lowering generici; catalogo fornito dal chiamante."""

from collections.abc import Mapping

from italica.ast import Program
from italica.diagnostics import CompileError, canonical
from italica.ir import IR_VERSION, EntityIR, ProgramIR
from italica.parser import parse


def analyze(program: Program, kinds: Mapping[str, str]) -> ProgramIR:
    if any(
        not name or canonical(name) != name or not ident.strip() for name, ident in kinds.items()
    ):
        raise ValueError("Il catalogo richiede nomi canonici e identificatori non vuoti.")
    if len(set(kinds.values())) != len(kinds):
        raise ValueError("Gli identificatori dei tipi devono essere univoci.")
    symbols: set[str] = set()
    entities: list[EntityIR] = []
    for declaration in program.declarations:
        name = canonical(declaration.name)
        if name in symbols:
            raise CompileError(
                "E101", f"Nome già dichiarato: {declaration.name}.", declaration.span
            )
        kind = canonical(declaration.kind)
        if kind not in kinds:
            raise CompileError("E102", f"Tipo sconosciuto: {declaration.kind}.", declaration.span)
        symbols.add(name)
        entities.append(EntityIR(f"e{len(entities) + 1}", declaration.name, kinds[kind]))
    return ProgramIR(IR_VERSION, tuple(entities))


def compile_source(text: str, kinds: Mapping[str, str], source: str = "<memoria>") -> ProgramIR:
    return analyze(parse(text, source), kinds)
