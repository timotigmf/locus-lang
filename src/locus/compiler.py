"""Analisi a due passaggi e lowering di relazioni descritte da schemi esterni."""

from collections.abc import Mapping

from locus.ast import Program, Relation
from locus.diagnostics import CompileError, canonical
from locus.graph import cycle_node
from locus.ir import IR_VERSION, EntityIR, ProgramIR, PropertyIR, RelationIR, SynonymIR
from locus.parser import parse
from locus.rule_compiler import lower_rules
from locus.schema import ActionSpec, PropertySpec, RelationSpec, Value, type_ids


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
        if (
            not type_ids(spec.source_type)
            or not type_ids(spec.target_type)
            or any(
                ident not in kinds.values()
                for ident in (*type_ids(spec.source_type), *type_ids(spec.target_type))
            )
        ):
            raise ValueError("Il catalogo relazioni usa tipi non dichiarati.")
        if spec.inverse_id is not None:
            inverse = by_id.get(spec.inverse_id)
            if inverse is None or (
                inverse.inverse_id,
                set(type_ids(inverse.source_type)),
                set(type_ids(inverse.target_type)),
            ) != (spec.id, set(type_ids(spec.target_type)), set(type_ids(spec.source_type))):
                raise ValueError("Le relazioni inverse devono essere reciproche e compatibili.")


def analyze(
    program: Program,
    kinds: Mapping[str, str],
    *,
    relations: Mapping[str, RelationSpec] | None = None,
    properties: Mapping[str, PropertySpec] | None = None,
    actions: Mapping[str, ActionSpec] | None = None,
) -> ProgramIR:
    if program.inclusions:
        raise CompileError(
            "E401",
            "Le inclusioni richiedono il caricamento del progetto da file.",
            program.inclusions[0].span,
        )
    if len(program.entries) > 1:
        raise CompileError(
            "E406", "Il progetto può dichiarare un solo punto iniziale.", program.entries[1].span
        )
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

    metadata: dict[str, str] = {}
    for metadata_item in program.metadata:
        if metadata_item.name in metadata:
            raise CompileError(
                "E408", f"Metadato ripetuto: {metadata_item.name}.", metadata_item.span
            )
        metadata[metadata_item.name] = metadata_item.value

    synonyms: dict[str, SynonymIR] = {}
    for vocabulary_item in program.vocabulary:
        alias = canonical(vocabulary_item.alias)
        target = symbols.get(canonical(vocabulary_item.target))
        if target is None:
            raise CompileError(
                "E103",
                f"Entità non dichiarata: {vocabulary_item.target}.",
                vocabulary_item.span,
            )
        if not alias or alias in symbols or alias in synonyms:
            raise CompileError(
                "E409",
                f"Sinonimo già usato come nome o sinonimo: {vocabulary_item.alias}.",
                vocabulary_item.span,
            )
        synonyms[alias] = SynonymIR(vocabulary_item.alias, target.id)

    entry_id = None
    if program.entries:
        entry = program.entries[0]
        target = symbols.get(canonical(entry.name))
        if target is None:
            raise CompileError("E103", f"Entità iniziale non dichiarata: {entry.name}.", entry.span)
        entry_id = target.id
    facts = list(program.relations)
    facts.extend(
        Relation(d.name, "nella", d.location, d.span)
        for d in program.declarations
        if d.location is not None
    )
    source_order = {source: index for index, source in enumerate(program.source_order)}
    facts.sort(key=lambda fact: (source_order.get(fact.span.source, 0), fact.span.start))
    edges: dict[tuple[str, str], RelationIR] = {}
    edge_facts: dict[tuple[str, str], Relation] = {}
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
        if source.type_id not in type_ids(spec.source_type) or target.type_id not in type_ids(
            spec.target_type
        ):
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
            edge_facts[key] = fact
    for spec in catalog.values():
        if spec.acyclic:
            parents = {
                edge.source_id: edge.target_id
                for edge in edges.values()
                if edge.predicate_id == spec.id
            }
            cyclic = cycle_node(parents)
            if cyclic is not None:
                raise CompileError(
                    "E108", "La relazione contiene un ciclo.", edge_facts[(cyclic, spec.id)].span
                )

    property_catalog = dict(properties or {})
    for property_declaration in program.properties:
        name = canonical(property_declaration.name)
        if name in property_catalog:
            raise CompileError(
                "E109",
                f"Proprietà già dichiarata: {property_declaration.name}.",
                property_declaration.span,
            )
        defaults: dict[str, Value] = {"numero": 0, "testo": "", "logico": False}
        property_catalog[name] = PropertySpec(
            "autore." + name,
            tuple(kinds.values()),
            property_declaration.value_kind,
            defaults[property_declaration.value_kind],
        )
    _validate_properties(property_catalog, kinds)
    values = {
        (entity.id, spec.id): PropertyIR(entity.id, spec.id, spec.default)
        for entity in symbols.values()
        for spec in property_catalog.values()
        if entity.type_id in spec.owner_types
    }
    assigned: set[tuple[str, str]] = set()
    for assignment in program.assignments:
        entity = symbols.get(canonical(assignment.subject))
        if entity is None:
            raise CompileError(
                "E103", f"Entità non dichiarata: {assignment.subject}.", assignment.span
            )
        prop = property_catalog.get(canonical(assignment.property_name))
        if prop is None:
            raise CompileError(
                "E110", f"Proprietà sconosciuta: {assignment.property_name}.", assignment.span
            )
        if entity.type_id not in prop.owner_types or not prop.accepts(assignment.value):
            raise CompileError(
                "E111",
                f"Valore o destinatario incompatibile per {assignment.property_name}.",
                assignment.span,
            )
        key = (entity.id, prop.id)
        if key in assigned:
            raise CompileError(
                "E112",
                f"Proprietà assegnata più volte: {assignment.property_name}.",
                assignment.span,
            )
        assigned.add(key)
        values[key] = PropertyIR(entity.id, prop.id, assignment.value)
    return ProgramIR(
        version=IR_VERSION,
        entities=tuple(symbols.values()),
        relations=tuple(edges.values()),
        property_specs=tuple(property_catalog.values()),
        properties=tuple(values.values()),
        rules=lower_rules(program.rules, symbols, property_catalog, actions or {}),
        entry_id=entry_id,
        synonyms=tuple(synonyms.values()),
        title=metadata.get("titolo"),
        author=metadata.get("autore"),
    )


def compile_source(
    text: str,
    kinds: Mapping[str, str],
    source: str = "<memoria>",
    *,
    relations: Mapping[str, RelationSpec] | None = None,
    properties: Mapping[str, PropertySpec] | None = None,
    actions: Mapping[str, ActionSpec] | None = None,
) -> ProgramIR:
    catalog = relations or {}
    _validate_catalog(kinds, catalog)
    return analyze(
        parse(text, source, verbs=relation_verbs(catalog)),
        kinds,
        relations=relations,
        properties=properties,
        actions=actions,
    )


def relation_verbs(relations: Mapping[str, RelationSpec]) -> dict[str, str]:
    result: dict[str, str] = {}
    for name, spec in relations.items():
        if spec.verb is not None:
            if spec.verb in result or not spec.verb.isalpha() or canonical(spec.verb) != spec.verb:
                raise ValueError("Verbi di relazione non canonici o duplicati.")
            result[spec.verb] = name
    return result


def _validate_properties(properties: Mapping[str, PropertySpec], kinds: Mapping[str, str]) -> None:
    if len({spec.id for spec in properties.values()}) != len(properties):
        raise ValueError("Identificatori di proprietà duplicati.")
    for name, spec in properties.items():
        if not name or canonical(name) != name or not spec.id.strip():
            raise ValueError("Proprietà con nome non canonico o ID vuoto.")
        if any(owner not in kinds.values() for owner in spec.owner_types):
            raise ValueError("Proprietà con tipo destinatario sconosciuto.")
        if not spec.accepts(spec.default) or any(
            not spec.accepts(choice) for choice in spec.choices
        ):
            raise ValueError("Proprietà con default o alternative non validi.")
