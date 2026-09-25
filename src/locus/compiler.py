"""Analisi a due passaggi e lowering di relazioni descritte da schemi esterni."""

from collections.abc import Mapping

from locus.ast import Program, Relation
from locus.diagnostics import CompileError, canonical
from locus.ir import IR_VERSION, EntityIR, ProgramIR, RelationIR
from locus.parser import parse
from locus.schema import RelationSpec


def _validate_catalog(kinds: Mapping[str, str], relations: Mapping[str, RelationSpec]) -> None:
    if any(
        not name or canonical(name) != name or not ident.strip() for name, ident in kinds.items()
    ):
        raise ValueError("Il catalogo richiede nomi canonici e identificatori non vuoti.")
    if len(set(kinds.values())) != len(kinds):
        raise ValueError("Gli identificatori dei tipi devono essere univoci.")
    by_id = {spec.id: spec for spec in relations.values()}
    if len(by_id) != len(relations):
        raise ValueError("Gli identificatori delle relazioni devono essere univoci.")
    for name, spec in relations.items():
        if not name or name != canonical(name) or not spec.id.strip():
            raise ValueError("Il catalogo relazioni richiede nomi canonici e ID non vuoti.")
        if spec.source_type not in kinds.values() or spec.target_type not in kinds.values():
            raise ValueError("Il catalogo relazioni usa tipi non dichiarati.")
        if spec.inverse_id is not None:
            inverse = by_id.get(spec.inverse_id)
            if inverse is None or (
                inverse.inverse_id,
                inverse.source_type,
                inverse.target_type,
            ) != (spec.id, spec.target_type, spec.source_type):
                raise ValueError("Le relazioni inverse devono essere reciproche e compatibili.")


def analyze(
    program: Program,
    kinds: Mapping[str, str],
    *,
    relations: Mapping[str, RelationSpec] | None = None,
) -> ProgramIR:
    catalog = relations if relations is not None else {}
    _validate_catalog(kinds, catalog)
    symbols: dict[str, EntityIR] = {}
    for declaration in program.declarations:
        name = canonical(declaration.name)
        if name in symbols:
            raise CompileError(
                "E101", f"Nome già dichiarato: {declaration.name}.", declaration.span
            )
        kind = canonical(declaration.kind)
        if kind not in kinds:
            raise CompileError("E102", f"Tipo sconosciuto: {declaration.kind}.", declaration.span)
        symbols[name] = EntityIR(f"e{len(symbols) + 1}", declaration.name, kinds[kind])

    facts = list(program.relations)
    facts.extend(
        Relation(d.name, "nella", d.location, d.span)
        for d in program.declarations
        if d.location is not None
    )
    facts.sort(key=lambda fact: fact.span.start)
    edges: dict[tuple[str, str], RelationIR] = {}
    for fact in facts:
        operands: list[EntityIR] = []
        for name in (fact.subject, fact.target):
            if canonical(name) not in symbols:
                raise CompileError("E103", f"Entità non dichiarata: {name}.", fact.span)
            operands.append(symbols[canonical(name)])
        predicate = canonical(fact.predicate)
        if predicate not in catalog:
            raise CompileError("E104", f"Relazione sconosciuta: {fact.predicate}.", fact.span)
        spec = catalog[predicate]
        source, target = reversed(operands) if spec.reverse_operands else operands
        if source.type_id != spec.source_type or target.type_id != spec.target_type:
            raise CompileError(
                "E105", f"Tipi incompatibili per la relazione {predicate}.", fact.span
            )
        if source.id == target.id:
            raise CompileError(
                "E107", "Una relazione non può collegare un'entità a sé stessa.", fact.span
            )
        candidates = [RelationIR(source.id, spec.id, target.id)]
        if spec.inverse_id is not None:
            candidates.append(RelationIR(target.id, spec.inverse_id, source.id))
        for edge in candidates:
            key = (edge.source_id, edge.predicate_id)
            if key in edges and edges[key] != edge:
                raise CompileError("E106", f"Destinazioni in conflitto per {predicate}.", fact.span)
            edges[key] = edge
    return ProgramIR(IR_VERSION, tuple(symbols.values()), tuple(edges.values()))


def compile_source(
    text: str,
    kinds: Mapping[str, str],
    source: str = "<memoria>",
    *,
    relations: Mapping[str, RelationSpec] | None = None,
) -> ProgramIR:
    return analyze(parse(text, source), kinds, relations=relations)
