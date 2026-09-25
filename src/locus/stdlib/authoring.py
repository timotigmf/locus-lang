"""Composizione del frontend con schemi e vincoli della libreria narrativa."""

from locus.compiler import analyze, relation_verbs
from locus.diagnostics import CompileError
from locus.ir import ProgramIR
from locus.parser import parse
from locus.runtime import instantiate
from locus.stdlib import default_actions, default_kinds, default_properties, default_relations
from locus.stdlib.validation import WorldError, validate_world


def compile_story(text: str, source: str = "<memoria>") -> ProgramIR:
    relations = default_relations()
    ast = parse(text, source, verbs=relation_verbs(relations))
    program = analyze(
        ast,
        default_kinds(),
        relations=relations,
        properties=default_properties(),
        actions=default_actions(),
    )
    try:
        validate_world(instantiate(program))
    except WorldError as error:
        index = next(i for i, entity in enumerate(program.entities) if entity.id == error.entity_id)
        raise CompileError("E201", str(error), ast.declarations[index].span) from error
    return program
