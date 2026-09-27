"""Analisi a due passaggi e lowering di relazioni descritte da schemi esterni."""

from collections.abc import Collection, Mapping

from locus.ast import Program, Relation
from locus.diagnostics import CompileError, canonical
from locus.graph import cycle_node
from locus.ir import (
    IR_VERSION,
    ActionIR,
    EntityIR,
    ProgramIR,
    PropertyIR,
    RelationIR,
    SynonymIR,
    TypeIR,
)
from locus.parser import parse
from locus.rule_compiler import lower_rules
from locus.schema import (
    ActionSpec,
    PropertySpec,
    RelationSpec,
    Value,
    command_forms_conflict,
    is_subtype,
    type_ids,
    valid_command_form,
)


def _validate_catalog(
    kinds: Mapping[str, str],
    relations: Mapping[str, RelationSpec],
    kind_parents: Mapping[str, str | None] | None,
) -> dict[str, str | None]:
    if any(
        not name or canonical(name) != name or not ident.strip() for name, ident in kinds.items()
    ):
        raise ValueError("Il catalogo richiede nomi canonici e identificatori non vuoti.")
    if len(set(kinds.values())) != len(kinds):
        raise ValueError("Gli identificatori dei tipi devono essere univoci.")
    identifiers = set(kinds.values())
    parents: dict[str, str | None] = {ident: None for ident in kinds.values()}
    for child, parent in (kind_parents or {}).items():
        if child not in identifiers or (parent is not None and parent not in identifiers):
            raise ValueError("La gerarchia dei tipi usa identificatori non dichiarati.")
        parents[child] = parent
    hierarchy = {child: parent for child, parent in parents.items() if parent is not None}
    if cycle_node(hierarchy) is not None:
        raise ValueError("La gerarchia dei tipi contiene un ciclo.")
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
    return parents


def analyze(
    program: Program,
    kinds: Mapping[str, str],
    *,
    relations: Mapping[str, RelationSpec] | None = None,
    properties: Mapping[str, PropertySpec] | None = None,
    actions: Mapping[str, ActionSpec] | None = None,
    kind_parents: Mapping[str, str | None] | None = None,
    reserved_commands: Collection[str] = (),
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
    type_parents = _validate_catalog(kinds, catalog, kind_parents)
    kind_symbols = dict(kinds)
    kind_spans = {}
    next_author_id = 1
    for kind_declaration in program.kinds:
        name = canonical(kind_declaration.name)
        if name in kind_symbols:
            raise CompileError(
                "E113", f"Tipo già dichiarato: {kind_declaration.name}.", kind_declaration.span
            )
        ident = f"autore.t{next_author_id}"
        while ident in type_parents:
            next_author_id += 1
            ident = f"autore.t{next_author_id}"
        next_author_id += 1
        kind_symbols[name] = ident
        kind_spans[ident] = kind_declaration.span
    author_parents: dict[str, str] = {}
    for kind_declaration in program.kinds:
        ident = kind_symbols[canonical(kind_declaration.name)]
        parent = kind_symbols.get(canonical(kind_declaration.parent))
        if parent is None:
            raise CompileError(
                "E102",
                f"Tipo sconosciuto: {kind_declaration.parent}.",
                kind_declaration.span,
            )
        author_parents[ident] = parent
    type_parents.update(author_parents)
    cyclic_kind = cycle_node({child: parent for child, parent in type_parents.items() if parent})
    if cyclic_kind is not None:
        raise CompileError(
            "E114", "La gerarchia dei tipi contiene un ciclo.", kind_spans[cyclic_kind]
        )
    labels_by_id = {ident: name for name, ident in kinds.items()}
    labels_by_id.update(
        {
            kind_symbols[canonical(kind_declaration.name)]: kind_declaration.name
            for kind_declaration in program.kinds
        }
    )
    type_records = tuple(
        TypeIR(ident, labels_by_id[ident], type_parents[ident]) for ident in type_parents
    )
    command_names = {canonical(command) for command in reserved_commands}
    if any(
        command != canonical(command) or not valid_command_form(command)
        for command in reserved_commands
    ) or command_forms_conflict(tuple(command_names)):
        raise ValueError("I comandi riservati devono essere canonici e privi di conflitti.")
    action_catalog = dict(actions or {})
    used_action_ids = {spec.id for spec in action_catalog.values()}
    action_records: list[ActionIR] = []
    next_action_id = 1
    for declaration in program.actions:
        name = canonical(declaration.name)
        name_words = name.split()
        if (
            name in action_catalog
            or not name_words
            or any(not word.isalpha() or word in {"con", "nella"} for word in name_words)
        ):
            raise CompileError(
                "E310",
                f"Nome di azione non valido o già dichiarato: {declaration.name}.",
                declaration.span,
            )
        commands = tuple(canonical(command) for command in declaration.commands)
        if (
            not commands
            or any(not valid_command_form(command) for command in commands)
            or command_forms_conflict(tuple(command_names) + commands)
        ):
            raise CompileError(
                "E311",
                "Comando o sinonimo non valido, duplicato o in conflitto di prefisso.",
                declaration.span,
            )
        command_names.update(commands)
        target_type = (
            kind_symbols.get(canonical(declaration.target_kind))
            if declaration.target_kind is not None
            else None
        )
        indirect_type = (
            kind_symbols.get(canonical(declaration.indirect_kind))
            if declaration.indirect_kind is not None
            else None
        )
        missing_kind = (
            declaration.target_kind
            if declaration.target_kind is not None and target_type is None
            else declaration.indirect_kind
            if declaration.indirect_kind is not None and indirect_type is None
            else None
        )
        if missing_kind is not None:
            raise CompileError("E102", f"Tipo sconosciuto: {missing_kind}.", declaration.span)
        separators = tuple(canonical(separator) for separator in declaration.separators)
        invalid_separators = (
            (indirect_type is None and bool(separators))
            or (indirect_type is not None and not separators)
            or len(set(separators)) != len(separators)
            or any(
                len(separator.split()) != 1 or not separator.isalpha() or separator in commands
                for separator in separators
            )
        )
        if invalid_separators:
            raise CompileError(
                "E311",
                "I separatori devono essere parole distinte dai comandi e non duplicate.",
                declaration.span,
            )
        ident = f"autore.a{next_action_id}"
        while ident in used_action_ids:
            next_action_id += 1
            ident = f"autore.a{next_action_id}"
        next_action_id += 1
        used_action_ids.add(ident)
        arity = int(target_type is not None) + int(indirect_type is not None)
        action_catalog[name] = ActionSpec(
            ident,
            arity,
            arity,
            (target_type,) if target_type is not None else (),
            (indirect_type,) if indirect_type is not None else (),
        )
        action_records.append(
            ActionIR(
                ident,
                declaration.name,
                commands,
                target_type,
                indirect_type,
                separators,
            )
        )
    symbols: dict[str, EntityIR] = {}
    for entity_declaration in program.declarations:
        name = canonical(entity_declaration.name)
        if name in symbols:
            raise CompileError(
                "E101", f"Nome già dichiarato: {entity_declaration.name}.", entity_declaration.span
            )
        kind = canonical(entity_declaration.kind)
        if kind not in kind_symbols:
            raise CompileError(
                "E102",
                f"Tipo sconosciuto: {entity_declaration.kind}.",
                entity_declaration.span,
            )
        symbols[name] = EntityIR(
            f"e{len(symbols) + 1}", entity_declaration.name, kind_symbols[kind]
        )

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
        if not any(
            is_subtype(source.type_id, expected, type_parents)
            for expected in type_ids(spec.source_type)
        ) or not any(
            is_subtype(target.type_id, expected, type_parents)
            for expected in type_ids(spec.target_type)
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
            tuple(kind_symbols.values()),
            property_declaration.value_kind,
            defaults[property_declaration.value_kind],
        )
    _validate_properties(property_catalog, set(type_parents))
    values = {
        (entity.id, spec.id): PropertyIR(entity.id, spec.id, spec.default)
        for entity in symbols.values()
        for spec in property_catalog.values()
        if any(is_subtype(entity.type_id, owner, type_parents) for owner in spec.owner_types)
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
        if not any(
            is_subtype(entity.type_id, owner, type_parents) for owner in prop.owner_types
        ) or not prop.accepts(assignment.value):
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
        rules=lower_rules(program.rules, symbols, property_catalog, action_catalog, type_parents),
        entry_id=entry_id,
        synonyms=tuple(synonyms.values()),
        title=metadata.get("titolo"),
        author=metadata.get("autore"),
        types=type_records,
        actions=tuple(action_records),
    )


def compile_source(
    text: str,
    kinds: Mapping[str, str],
    source: str = "<memoria>",
    *,
    relations: Mapping[str, RelationSpec] | None = None,
    properties: Mapping[str, PropertySpec] | None = None,
    actions: Mapping[str, ActionSpec] | None = None,
    kind_parents: Mapping[str, str | None] | None = None,
    reserved_commands: Collection[str] = (),
) -> ProgramIR:
    catalog = relations or {}
    return analyze(
        parse(text, source, verbs=relation_verbs(catalog)),
        kinds,
        relations=relations,
        properties=properties,
        actions=actions,
        kind_parents=kind_parents,
        reserved_commands=reserved_commands,
    )


def relation_verbs(relations: Mapping[str, RelationSpec]) -> dict[str, str]:
    result: dict[str, str] = {}
    for name, spec in relations.items():
        if spec.verb is not None:
            if spec.verb in result or not spec.verb.isalpha() or canonical(spec.verb) != spec.verb:
                raise ValueError("Verbi di relazione non canonici o duplicati.")
            result[spec.verb] = name
    return result


def _validate_properties(
    properties: Mapping[str, PropertySpec], type_identifiers: set[str]
) -> None:
    if len({spec.id for spec in properties.values()}) != len(properties):
        raise ValueError("Identificatori di proprietà duplicati.")
    for name, spec in properties.items():
        if not name or canonical(name) != name or not spec.id.strip():
            raise ValueError("Proprietà con nome non canonico o ID vuoto.")
        if any(owner not in type_identifiers for owner in spec.owner_types):
            raise ValueError("Proprietà con tipo destinatario sconosciuto.")
        if not spec.accepts(spec.default) or any(
            not spec.accepts(choice) for choice in spec.choices
        ):
            raise ValueError("Proprietà con default o alternative non validi.")
