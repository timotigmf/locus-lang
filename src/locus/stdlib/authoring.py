"""Composizione del frontend con schemi e vincoli della libreria narrativa."""

from pathlib import Path

from locus.ast import Program
from locus.compiler import analyze, relation_verbs
from locus.diagnostics import CompileError
from locus.ir import ProgramIR
from locus.parser import parse
from locus.project import load_project
from locus.runtime import instantiate
from locus.stdlib import default_actions, default_kinds, default_properties, default_relations
from locus.stdlib.validation import WorldError, validate_world


def compile_story(text: str, source: str = "<memoria>") -> ProgramIR:
    relations = default_relations()
    ast = parse(text, source, verbs=relation_verbs(relations))
    return _compile(ast)


def compile_story_file(path: Path) -> ProgramIR:
    return _compile(load_project(path, verbs=relation_verbs(default_relations())))


def _compile(ast: Program) -> ProgramIR:
    program = analyze(
        ast,
        default_kinds(),
        relations=default_relations(),
        properties=default_properties(),
        actions=default_actions(),
    )
    try:
        validate_world(instantiate(program))
    except WorldError as error:
        if ast.entries and program.entry_id == error.entity_id:
            raise CompileError("E407", str(error), ast.entries[0].span) from error
        index = next(i for i, entity in enumerate(program.entities) if entity.id == error.entity_id)
        raise CompileError("E201", str(error), ast.declarations[index].span) from error
    return program
