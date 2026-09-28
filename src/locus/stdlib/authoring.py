"""Composizione del frontend con schemi e vincoli della libreria narrativa."""

from dataclasses import replace
from pathlib import Path

from locus.ast import Program
from locus.compiler import analyze, relation_verbs
from locus.diagnostics import CompileError, canonical
from locus.ir import ProgramIR, ResourceIR
from locus.media import MAX_RESOURCE_BYTES, resource_media_type, valid_media_content
from locus.parser import parse
from locus.player import standard_commands
from locus.project import load_project
from locus.runtime import instantiate
from locus.stdlib import (
    ALTERNATIVE_TEXT,
    IMAGE,
    PERSON,
    SOUND,
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
    root = (allowed_root or path.parent).resolve()
    return _compile(
        load_project(path, verbs=relation_verbs(default_relations()), allowed_root=allowed_root),
        resource_root=root,
    )


def _compile(ast: Program, *, resource_root: Path | None = None) -> ProgramIR:
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
    program = _add_resources(program, ast, resource_root)
    try:
        validate_world(instantiate(program))
    except WorldError as error:
        if ast.entries and program.entry_id == error.entity_id:
            raise CompileError("E407", str(error), ast.entries[0].span) from error
        index = next(i for i, entity in enumerate(program.entities) if entity.id == error.entity_id)
        raise CompileError(error.code, str(error), ast.declarations[index].span) from error
    return program


def _add_resources(program: ProgramIR, ast: Program, root: Path | None) -> ProgramIR:
    """Costruisce il manifest IR dalle proprietà della stdlib multimediale."""
    entities = {canonical(item.label): item for item in program.entities}
    spans = {
        (entities[canonical(item.subject)].id, canonical(item.property_name)): item.span
        for item in ast.assignments
        if canonical(item.subject) in entities
    }
    values = {(item.entity_id, item.property_id): item.value for item in program.properties}
    resources: list[ResourceIR] = []
    for entity in program.entities:
        alternative = values.get((entity.id, ALTERNATIVE_TEXT)) or entity.label
        for kind, property_id in (("immagine", IMAGE), ("suono", SOUND)):
            value = values.get((entity.id, property_id), "")
            if not isinstance(value, str) or not value:
                continue
            span = spans[(entity.id, kind)]
            try:
                media_type = resource_media_type(kind, value)
            except ValueError as error:
                raise CompileError("E126", str(error), span) from error
            if root is not None:
                try:
                    candidate = (root / value).resolve(strict=True)
                    if not candidate.is_relative_to(root) or not candidate.is_file():
                        raise OSError
                    if candidate.stat().st_size > MAX_RESOURCE_BYTES:
                        raise OSError("La risorsa supera 5 MB.")
                    if not valid_media_content(media_type, candidate.read_bytes()[:12]):
                        raise OSError("Il contenuto non corrisponde al formato dichiarato.")
                except (OSError, RuntimeError, ValueError) as error:
                    detail = str(error) or "file assente o non regolare"
                    raise CompileError(
                        "E126", f"Risorsa non leggibile: {value} ({detail}).", span
                    ) from error
            resources.append(ResourceIR(entity.id, kind, value, media_type, str(alternative)))
    return replace(program, resources=tuple(resources))
