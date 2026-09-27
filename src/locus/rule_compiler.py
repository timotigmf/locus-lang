"""Risoluzione e controllo statico delle regole, senza dipendenze narrative."""

from collections.abc import Mapping

from locus.ast import ActionSyntax, PropertyReference, Rule
from locus.diagnostics import CompileError, Span, canonical
from locus.ir import EntityIR
from locus.rule_model import (
    ActionCall,
    Address,
    Condition,
    Effect,
    Origin,
    RelationChange,
    RelationEdge,
    RuleIR,
)
from locus.schema import ActionSpec, PropertySpec, RelationSpec, is_subtype, type_ids


def lower_rules(
    rules: tuple[Rule, ...],
    entities: Mapping[str, EntityIR],
    properties: Mapping[str, PropertySpec],
    actions: Mapping[str, ActionSpec],
    relations: Mapping[str, RelationSpec],
    type_parents: Mapping[str, str | None],
) -> tuple[RuleIR, ...]:
    if len({spec.id for spec in actions.values()}) != len(actions):
        raise ValueError("Identificatori di azione duplicati.")
    for name, spec in actions.items():
        if (
            not name
            or name != canonical(name)
            or not spec.id.strip()
            or not 0 <= spec.min_args <= spec.max_args <= 2
            or (spec.target_types and spec.max_args < 1)
            or (spec.indirect_types and spec.max_args < 2)
            or any(
                type_id not in type_parents
                for type_id in (*spec.target_types, *spec.indirect_types)
            )
        ):
            raise ValueError("Catalogo azioni non valido.")

    def entity(name: str, span: Span) -> EntityIR:
        found = entities.get(canonical(name))
        if found is None:
            raise CompileError("E103", f"Entità non dichiarata: {name}.", span)
        return found

    def address(ref: PropertyReference, span: Span) -> tuple[Address, PropertySpec]:
        owner = entity(ref.entity_name, span)
        prop = properties.get(canonical(ref.property_name))
        if prop is None:
            raise CompileError("E304", f"Proprietà sconosciuta: {ref.property_name}.", span)
        if not any(
            is_subtype(owner.type_id, expected, type_parents) for expected in prop.owner_types
        ):
            raise CompileError("E305", "Proprietà non applicabile a questa entità.", span)
        return Address(owner.id, prop.id), prop

    def action(syntax: ActionSyntax, span: Span, *, selector: bool) -> ActionCall:
        spec = actions.get(canonical(syntax.name))
        if spec is None:
            raise CompileError("E303", f"Azione sconosciuta: {syntax.name}.", span)
        count = int(syntax.target is not None) + int(syntax.indirect is not None)
        if (
            count > spec.max_args
            or (not selector and count < spec.min_args)
            or (syntax.indirect is not None and syntax.target is None)
        ):
            raise CompileError("E306", "Numero di oggetti non valido per l'azione.", span)
        target = entity(syntax.target, span) if syntax.target is not None else None
        indirect = entity(syntax.indirect, span) if syntax.indirect is not None else None
        if (
            target is not None
            and spec.target_types
            and not any(
                is_subtype(target.type_id, expected, type_parents) for expected in spec.target_types
            )
        ):
            raise CompileError("E305", "Tipo del primo oggetto non compatibile.", span)
        if (
            indirect is not None
            and spec.indirect_types
            and not any(
                is_subtype(indirect.type_id, expected, type_parents)
                for expected in spec.indirect_types
            )
        ):
            raise CompileError("E305", "Tipo del secondo oggetto non compatibile.", span)
        return ActionCall(
            spec.id,
            target.id if target is not None else None,
            indirect.id if indirect is not None else None,
        )

    def condition(node: Condition[PropertyReference], span: Span) -> Condition[Address]:
        if node.reference is not None:
            resolved, prop = address(node.reference, span)
            if node.value is None or not prop.accepts(node.value):
                raise CompileError("E305", "Confronto con valore incompatibile.", span)
            if node.operator not in {"uguale", "diverso"} and prop.value_kind != "numero":
                raise CompileError(
                    "E305", "Il confronto ordinato richiede una proprietà numerica.", span
                )
            return Condition(node.operator, resolved, node.value)
        return Condition(
            node.operator, operands=tuple(condition(child, span) for child in node.operands)
        )

    def relation_change(
        name: str, source_name: str, target_name: str, span: Span
    ) -> RelationChange:
        spec = relations.get(canonical(name))
        if spec is None:
            raise CompileError("E312", f"Relazione sconosciuta: {name}.", span)
        if not spec.mutable:
            raise CompileError(
                "E312", f"La relazione {name} non può cambiare durante la storia.", span
            )
        source = entity(source_name, span)
        target = entity(target_name, span)
        if source.id == target.id:
            raise CompileError(
                "E312", "Una relazione non può collegare un'entità a sé stessa.", span
            )
        if not any(
            is_subtype(source.type_id, expected, type_parents)
            for expected in type_ids(spec.source_type)
        ) or not any(
            is_subtype(target.type_id, expected, type_parents)
            for expected in type_ids(spec.target_type)
        ):
            raise CompileError("E305", f"Tipi incompatibili per la relazione {name}.", span)
        edges = [RelationEdge(source.id, spec.id, target.id)]
        if spec.inverse_id is not None:
            edges.append(RelationEdge(target.id, spec.inverse_id, source.id))
        return RelationChange(tuple(edges))

    result: list[RuleIR] = []
    names: set[str] = set()
    for order, rule in enumerate(rules):
        name = canonical(rule.name)
        if name in names:
            raise CompileError("E301", f"Regola già dichiarata: {rule.name}.", rule.span)
        names.add(name)
        if abs(rule.priority) > 1_000_000:
            raise CompileError(
                "E309", "Priorità fuori intervallo: da -1000000 a 1000000.", rule.span
            )
        effects: list[Effect] = []
        terminal = False
        for syntax in rule.effects:
            if terminal:
                raise CompileError(
                    "E308", "Istruzione irraggiungibile dopo un esito terminale.", syntax.span
                )
            if rule.phase == "verifica" and syntax.kind in {
                "imposta",
                "aumenta",
                "sostituisci",
                "crea_relazione",
                "rimuovi_relazione",
            }:
                raise CompileError(
                    "E307",
                    "La fase verifica non può modificare lo stato o sostituire azioni.",
                    syntax.span,
                )
            resolved = None
            if syntax.reference is not None:
                resolved, prop = address(syntax.reference, syntax.span)
                if syntax.kind == "aumenta":
                    if prop.value_kind != "numero" or type(syntax.value) is not int:
                        raise CompileError(
                            "E305",
                            "Aumenta/diminuisci richiede una proprietà numerica.",
                            syntax.span,
                        )
                elif syntax.value is None or not prop.accepts(syntax.value):
                    raise CompileError(
                        "E305", "Assegnazione con valore incompatibile.", syntax.span
                    )
            replacement = (
                action(syntax.action, syntax.span, selector=False) if syntax.action else None
            )
            changed_relation = (
                relation_change(
                    syntax.relation.name,
                    syntax.relation.source,
                    syntax.relation.target,
                    syntax.span,
                )
                if syntax.relation is not None
                else None
            )
            effects.append(
                Effect(
                    syntax.kind,
                    syntax.value,
                    resolved,
                    replacement,
                    changed_relation,
                )
            )
            terminal = syntax.kind in {
                "continua",
                "interrompi",
                "fallisci",
                "sostituisci",
                "restituisci",
            }
        result.append(
            RuleIR(
                f"r{order + 1}",
                rule.name,
                rule.phase,
                action(rule.action, rule.span, selector=True),
                rule.priority,
                order,
                condition(rule.condition, rule.span),
                tuple(effects),
                Origin(rule.span.source, rule.span.line, rule.span.column),
            )
        )
    return tuple(result)
