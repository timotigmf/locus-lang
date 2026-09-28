"""Composizione del frontend con schemi e vincoli della libreria narrativa."""

from dataclasses import replace
from pathlib import Path

from locus.ast import Program
from locus.compiler import analyze, relation_verbs
from locus.diagnostics import CompileError, canonical
from locus.ir import ProgramIR
from locus.parser import parse
from locus.player import standard_commands
from locus.project import load_project
from locus.runtime import instantiate
from locus.stdlib import (
    PERSON,
    default_actions,
    default_kind_parents,
    default_kinds,
    default_properties,
    default_relations,
)
from locus.stdlib.validation import WorldError, validate_world


def compile_story(text: str, source: str = "<memoria>") -> ProgramIR:
    relations = default_relations()
    ast = parse(text, source, verbs=relation_verbs(relations))
    return _compile(ast)


def compile_story_file(path: Path, *, allowed_root: Path | None = None) -> ProgramIR:
    return _compile(
        load_project(path, verbs=relation_verbs(default_relations()), allowed_root=allowed_root)
    )


def _compile(ast: Program) -> ProgramIR:
    has_dialogues = bool(ast.dialogues)
    has_scenes = bool(ast.scenes)
    kind_parents = {
        canonical(declaration.name): canonical(declaration.parent) for declaration in ast.kinds
    }
    vehicle_kinds = {"veicolo"}
    commerce_kinds = {"valuta", "prodotto", "mercante"}
    changed = True
    while changed:
        changed = False
        for name, parent in kind_parents.items():
            if parent in vehicle_kinds and name not in vehicle_kinds:
                vehicle_kinds.add(name)
                changed = True
            if parent in commerce_kinds and name not in commerce_kinds:
                commerce_kinds.add(name)
                changed = True
    has_vehicles = any(
        canonical(declaration.kind) in vehicle_kinds for declaration in ast.declarations
    )
    has_commerce = any(
        canonical(declaration.kind) in commerce_kinds for declaration in ast.declarations
    )
    # Compatibilità con esempi anteriori ai tipi standard persona e veicolo.
    ast = replace(
        ast,
        kinds=tuple(
            declaration
            for declaration in ast.kinds
            if not (
                (
                    canonical(declaration.name) in {"persona", "veicolo", "valuta"}
                    and canonical(declaration.parent) == "cosa"
                )
                or (
                    canonical(declaration.name) == "mercante"
                    and canonical(declaration.parent) == "persona"
                )
            )
        ),
    )
    relations = default_relations()
    program = analyze(
        ast,
        default_kinds(),
        relations=relations,
        properties=default_properties(),
        actions=default_actions(),
        kind_parents=default_kind_parents(),
        reserved_commands=standard_commands(
            include_dialogue=has_dialogues,
            include_scenes=has_scenes,
            include_vehicles=has_vehicles,
            include_commerce=has_commerce,
        ),
        dialogue_actor_types=(PERSON,),
    )
    try:
        validate_world(instantiate(program))
    except WorldError as error:
        if ast.entries and program.entry_id == error.entity_id:
            raise CompileError("E407", str(error), ast.entries[0].span) from error
        index = next(i for i, entity in enumerate(program.entities) if entity.id == error.entity_id)
        raise CompileError(error.code, str(error), ast.declarations[index].span) from error
    return program
