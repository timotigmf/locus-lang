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
    # Compatibilità con gli esempi anteriori all'IR 16, dove persona era un tipo autore.
    ast = replace(
        ast,
        kinds=tuple(
            declaration
            for declaration in ast.kinds
            if not (
                canonical(declaration.name) == "persona" and canonical(declaration.parent) == "cosa"
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
        ),
        dialogue_actor_types=(PERSON,),
    )
    try:
        validate_world(instantiate(program))
    except WorldError as error:
        if ast.entries and program.entry_id == error.entity_id:
            raise CompileError("E407", str(error), ast.entries[0].span) from error
        index = next(i for i, entity in enumerate(program.entities) if entity.id == error.entity_id)
        raise CompileError("E201", str(error), ast.declarations[index].span) from error
    return program
