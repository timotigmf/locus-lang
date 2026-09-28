"""Analisi a due passaggi e lowering di relazioni descritte da schemi esterni."""

from collections.abc import Collection, Mapping

from locus.ast import Program, Relation
from locus.diagnostics import CompileError, canonical
from locus.graph import cycle_node
from locus.ir import (
    IR_VERSION,
    ActionIR,
    DialogueChoiceIR,
    DialogueIR,
    DialogueNodeIR,
    EntityIR,
    ProgramIR,
    PropertyIR,
    RelationIR,
    SynonymIR,
    TableColumnIR,
    TableIR,
    TypeIR,
)
from locus.parser import parse
from locus.rule_compiler import lower_rules
from locus.schema import (
    ActionSpec,
    PropertySpec,
    RelationSpec,
    Scalar,
    Value,
    command_forms_conflict,
    is_subtype,
    separator_forms_conflict,
    type_ids,
    valid_command_form,
    valid_separator_form,
    valid_value,
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
                inverse.mutable,
            ) != (
                spec.id,
                set(type_ids(spec.target_type)),
                set(type_ids(spec.source_type)),
                spec.mutable,
            ):
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
    dialogue_actor_types: Collection[str] = (),
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
    if any(type_id not in type_parents for type_id in dialogue_actor_types):
        raise ValueError("I tipi ammessi nei dialoghi devono essere dichiarati nel catalogo.")
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
            or separator_forms_conflict(separators)
            or any(
                not valid_separator_form(separator) or separator in commands
                for separator in separators
            )
        )
        if invalid_separators:
            raise CompileError(
                "E311",
                "I separatori non sono validi, sono duplicati o hanno prefissi ambigui.",
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
    if len(program.tables) > 64:
        raise CompileError(
            "E116", "Un progetto ammette al massimo 64 tabelle.", program.tables[64].span
        )
    table_catalog: dict[str, TableIR] = {}
    for index, table_declaration in enumerate(program.tables, 1):
        name = canonical(table_declaration.name)
        if name in table_catalog:
            raise CompileError(
                "E115",
                f"Tabella già dichiarata: {table_declaration.name}.",
                table_declaration.span,
            )
        if not 1 <= len(table_declaration.columns) <= 64:
            raise CompileError(
                "E116", "Una tabella richiede da 1 a 64 colonne.", table_declaration.span
            )
        column_names = [canonical(column.name) for column in table_declaration.columns]
        if any(not column_name for column_name in column_names) or len(set(column_names)) != len(
            column_names
        ):
            raise CompileError(
                "E116",
                "I nomi delle colonne devono essere univoci e non vuoti.",
                table_declaration.span,
            )
        if len(table_declaration.rows) > 10_000:
            raise CompileError(
                "E117",
                "Una tabella ammette al massimo 10000 righe.",
                table_declaration.rows[10_000].span,
            )
        columns = tuple(
            TableColumnIR(column_name, column.name, column.value_kind)
            for column_name, column in zip(column_names, table_declaration.columns, strict=True)
        )
        rows: list[tuple[Scalar, ...]] = []
        for row in table_declaration.rows:
            if len(row.values) != len(columns) or any(
                not valid_value(column.value_kind, value)
                for column, value in zip(columns, row.values, strict=False)
            ):
                raise CompileError(
                    "E117",
                    "La riga deve avere un valore compatibile per ogni colonna.",
                    row.span,
                )
            rows.append(row.values)
        table_catalog[name] = TableIR(
            f"autore.tabella.{index}", table_declaration.name, columns, tuple(rows)
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

    if len(program.dialogues) > 64:
        raise CompileError(
            "E118", "Un progetto ammette al massimo 64 dialoghi.", program.dialogues[64].span
        )
    dialogue_names: set[str] = set()
    dialogue_speakers: set[str] = set()
    dialogue_records: list[DialogueIR] = []
    for dialogue_index, dialogue_declaration in enumerate(program.dialogues, 1):
        dialogue_name = canonical(dialogue_declaration.name)
        if not dialogue_name or dialogue_name in dialogue_names:
            raise CompileError(
                "E118",
                f"Dialogo già dichiarato: {dialogue_declaration.name}.",
                dialogue_declaration.span,
            )
        speaker = symbols.get(canonical(dialogue_declaration.speaker))
        if speaker is None:
            raise CompileError(
                "E120",
                f"Persona non dichiarata: {dialogue_declaration.speaker}.",
                dialogue_declaration.span,
            )
        if not dialogue_actor_types or not any(
            is_subtype(speaker.type_id, expected, type_parents) for expected in dialogue_actor_types
        ):
            raise CompileError(
                "E120",
                f"Il partecipante del dialogo non è una persona: {dialogue_declaration.speaker}.",
                dialogue_declaration.span,
            )
        if speaker.id in dialogue_speakers:
            raise CompileError(
                "E118",
                f"Esiste già un dialogo per {dialogue_declaration.speaker}.",
                dialogue_declaration.span,
            )
        if not 1 <= len(dialogue_declaration.nodes) <= 128:
            raise CompileError(
                "E119", "Un dialogo richiede da 1 a 128 nodi.", dialogue_declaration.span
            )
        node_names = [canonical(node.name) for node in dialogue_declaration.nodes]
        if any(not name for name in node_names) or len(set(node_names)) != len(node_names):
            raise CompileError(
                "E119",
                "I nomi dei nodi devono essere univoci e non vuoti.",
                dialogue_declaration.span,
            )
        dialogue_id = f"autore.dialogo.{dialogue_index}"
        node_ids = {
            name: f"{dialogue_id}.nodo.{node_index}"
            for node_index, name in enumerate(node_names, 1)
        }
        nodes: list[DialogueNodeIR] = []
        for node, node_name in zip(dialogue_declaration.nodes, node_names, strict=True):
            if not node.text.strip() or len(node.choices) > 32:
                raise CompileError(
                    "E119",
                    "Ogni nodo richiede una battuta non vuota e al massimo 32 scelte.",
                    node.span,
                )
            choice_names = [canonical(choice.label) for choice in node.choices]
            if any(not name for name in choice_names) or len(set(choice_names)) != len(
                choice_names
            ):
                raise CompileError(
                    "E119", "Le scelte di un nodo devono essere univoche e non vuote.", node.span
                )
            choices: list[DialogueChoiceIR] = []
            for choice_index, choice in enumerate(node.choices, 1):
                target_id = (
                    node_ids.get(canonical(choice.target)) if choice.target is not None else None
                )
                if choice.target is not None and target_id is None:
                    raise CompileError(
                        "E119",
                        f"Nodo di destinazione sconosciuto: {choice.target}.",
                        choice.span,
                    )
                choices.append(
                    DialogueChoiceIR(
                        f"{node_ids[node_name]}.scelta.{choice_index}",
                        choice.label,
                        target_id,
                    )
                )
            nodes.append(DialogueNodeIR(node_ids[node_name], node.name, node.text, tuple(choices)))
        nodes_by_id = {node.id: node for node in nodes}
        reachable = {nodes[0].id}
        pending = [nodes[0].id]
        while pending:
            current = nodes_by_id[pending.pop()]
            for edge_choice in current.choices:
                if (
                    edge_choice.target_node_id is not None
                    and edge_choice.target_node_id not in reachable
                ):
                    reachable.add(edge_choice.target_node_id)
                    pending.append(edge_choice.target_node_id)
        if len(reachable) != len(nodes):
            unreachable = next(
                node
                for node in dialogue_declaration.nodes
                if node_ids[canonical(node.name)] not in reachable
            )
            raise CompileError(
                "E119", f"Nodo irraggiungibile: {unreachable.name}.", unreachable.span
            )
        dialogue_names.add(dialogue_name)
        dialogue_speakers.add(speaker.id)
        dialogue_records.append(
            DialogueIR(
                dialogue_id,
                dialogue_declaration.name,
                speaker.id,
                nodes[0].id,
                tuple(nodes),
            )
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
        defaults: dict[str, Value] = {
            "numero": 0,
            "testo": "",
            "logico": False,
            "elenco_testi": (),
            "elenco_numeri": (),
            "elenco_logici": (),
        }
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
        rules=lower_rules(
            program.rules,
            symbols,
            property_catalog,
            action_catalog,
            catalog,
            type_parents,
            table_catalog,
        ),
        entry_id=entry_id,
        synonyms=tuple(synonyms.values()),
        title=metadata.get("titolo"),
        author=metadata.get("autore"),
        types=type_records,
        actions=tuple(action_records),
        tables=tuple(table_catalog.values()),
        dialogues=tuple(dialogue_records),
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
    dialogue_actor_types: Collection[str] = (),
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
        dialogue_actor_types=dialogue_actor_types,
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
