import json
from dataclasses import replace
from pathlib import Path

import pytest

from locus.cli import main
from locus.compiler import analyze, compile_source
from locus.diagnostics import CompileError
from locus.parser import parse
from locus.player import parse_command
from locus.project import load_project
from locus.runtime import instantiate
from locus.stdlib.authoring import compile_story, compile_story_file
from locus.stdlib.game import start, step
from locus.stdlib.render import render


def write(root: Path, name: str, source: str) -> Path:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")
    return path


def test_project_forward_references_and_explicit_start(tmp_path: Path) -> None:
    write(tmp_path, "parti/oggetti.locus", "La chiave è una cosa nella Sala.")
    write(tmp_path, "parti/mondo.locus", 'Includi "oggetti.locus". La Cantina è una stanza.')
    path = write(
        tmp_path,
        "storia.locus",
        'Includi "parti/mondo.locus". Inizia nella "Sala". La Sala è una stanza.',
    )
    ir = compile_story_file(path)
    session = start(instantiate(ir))
    assert render(step(session, parse_command("guarda"))) == "Sala\nVedi: chiave."
    assert len(ir.entities) == 3
    assert ir == compile_story_file(path)


def test_author_type_can_be_declared_in_an_included_file(tmp_path: Path) -> None:
    write(tmp_path, "tipi.locus", "Una reliquia è un tipo di cosa.")
    path = write(
        tmp_path,
        "storia.locus",
        'Includi "tipi.locus". La Sala è una stanza. Il rubino è una reliquia nella Sala.',
    )
    program = compile_story_file(path)
    custom = next(item for item in program.types if item.label == "reliquia")
    assert program.entities[1].type_id == custom.id


def test_author_action_can_be_declared_in_an_included_file(tmp_path: Path) -> None:
    write(
        tmp_path,
        "azioni.locus",
        'Azione "meditare" senza oggetti con comando "medita" e sinonimo "rifletti". '
        'Regola "meditazione" per meditare nella fase invece: dì "Silenzio."; Fine regola.',
    )
    path = write(
        tmp_path,
        "storia.locus",
        'Includi "azioni.locus". La Sala è una stanza.',
    )
    current = start(instantiate(compile_story_file(path)))
    transition = step(current, parse_command("medita", current.world.actions))
    assert render(transition) == "Silenzio."
    transition = step(current, parse_command("rifletti", current.world.actions))
    assert render(transition) == "Silenzio."


def test_diamond_includes_once_and_rule_order(tmp_path: Path) -> None:
    write(
        tmp_path,
        "base.locus",
        "La Sala è una stanza. "
        'Regola "base" per guardare nella fase prima: dì "base"; Fine regola.',
    )
    for name in ["sinistra", "destra"]:
        write(
            tmp_path,
            f"{name}.locus",
            'Includi "base.locus". '
            f'Regola "{name}" per guardare nella fase prima: dì "{name}"; Fine regola.',
        )
    path = write(
        tmp_path,
        "storia.locus",
        'Includi "sinistra.locus". Includi "destra.locus". Includi "./base.locus".',
    )
    ast = load_project(path)
    assert len(ast.source_order) == 4
    assert not ast.inclusions
    result = step(start(instantiate(compile_story_file(path))), parse_command("guarda"))
    assert [t.name for t in result.trace] == ["base", "sinistra", "destra"]
    assert result.trace[0].origin.source == str(tmp_path / "base.locus")


def test_relative_to_including_file_not_working_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write(tmp_path, "mondo.locus", "La Sala è una stanza.")
    path = write(tmp_path, "parti/storia.locus", 'Includi "../mondo.locus".')
    monkeypatch.chdir(tmp_path.parent)
    assert len(compile_story_file(path).entities) == 1


@pytest.mark.parametrize("source", ['Includi "storia.locus".', 'Includi "parte.locus".'])
def test_cycles(tmp_path: Path, source: str) -> None:
    path = write(tmp_path, "storia.locus", source)
    write(tmp_path, "parte.locus", 'Includi "storia.locus".')
    with pytest.raises(CompileError, match="E403") as caught:
        load_project(path)
    assert "storia.locus" in caught.value.message
    assert caught.value.span.line == 1


@pytest.mark.parametrize(
    "name",
    ["/assoluto.locus", "C:/mondo.locus", "https://host/mondo.locus", r"cartella\\mondo.locus"],
)
def test_nonportable_paths(tmp_path: Path, name: str) -> None:
    path = write(tmp_path, "storia.locus", f'Includi "{name}".')
    with pytest.raises(CompileError, match="E404"):
        load_project(path)


@pytest.mark.parametrize("content", [None, b"\xff"])
def test_missing_or_invalid_utf8(tmp_path: Path, content: bytes | None) -> None:
    path = write(tmp_path, "storia.locus", '\nIncludi "parte.locus".')
    if content is not None:
        (tmp_path / "parte.locus").write_bytes(content)
    with pytest.raises(CompileError, match="E402") as caught:
        load_project(path)
    assert caught.value.span.source == str(path)
    assert caught.value.span.line == 2


def test_directory_is_not_source(tmp_path: Path) -> None:
    path = write(tmp_path, "storia.locus", 'Includi ".".')
    with pytest.raises(CompileError, match="E402"):
        load_project(path)


@pytest.mark.parametrize(
    "source,code",
    [
        ("La Sala è una stanza. La Sala è una stanza.", "E101"),
        ("La cosa è un tipo ignoto.", "E102"),
        ('Regola "x" per volare nella fase prima: continua; Fine regola.', "E303"),
        ("La Sala è una stanza", "E002"),
    ],
)
def test_diagnostics_preserve_module_source(tmp_path: Path, source: str, code: str) -> None:
    module = write(tmp_path, "parte.locus", "\n" + source)
    path = write(tmp_path, "storia.locus", 'Includi "parte.locus".')
    with pytest.raises(CompileError) as caught:
        compile_story_file(path)
    assert caught.value.code == code
    assert caught.value.span.source == str(module)
    assert caught.value.span.line == 2


def test_text_compilation_never_reads_includes() -> None:
    with pytest.raises(CompileError, match="E401"):
        compile_story('Includi "non_leggere.locus".')
    with pytest.raises(CompileError, match="E401"):
        analyze(parse('Includi "non_leggere.locus".'), {})


@pytest.mark.parametrize(
    "source,code",
    [
        ('Inizia nella "Assente".', "E103"),
        ('La leva è una cosa. Inizia nella "leva".', "E407"),
        ('La Sala è una stanza. Inizia nella "Sala". Inizia nella "Sala".', "E406"),
    ],
)
def test_invalid_entry(source: str, code: str) -> None:
    with pytest.raises(CompileError, match=code):
        compile_story(source)


def test_entry_collision_across_files(tmp_path: Path) -> None:
    write(tmp_path, "parte.locus", 'La Sala è una stanza. Inizia nella "Sala".')
    path = write(tmp_path, "storia.locus", 'Includi "parte.locus". Inizia nella "Sala".')
    with pytest.raises(CompileError, match="E406") as caught:
        compile_story_file(path)
    assert caught.value.span.source == str(path)


def test_entry_runtime_and_generic_domain() -> None:
    ir = compile_source('Il nodo è un elemento. Inizia nella "nodo".', {"elemento": "grafo.nodo"})
    assert instantiate(ir).entry_id == ir.entities[0].id
    with pytest.raises(ValueError, match="iniziale"):
        instantiate(replace(ir, entry_id="inesistente"))
    world = instantiate(compile_story("La Sala è una stanza. La leva è una cosa."))
    with pytest.raises(ValueError, match="stanza"):
        start(replace(world, entry_id=world.entities[1].id))


def test_limits(tmp_path: Path) -> None:
    path = write(tmp_path, "a.locus", 'Includi "b.locus".')
    write(tmp_path, "b.locus", 'Includi "c.locus".')
    write(tmp_path, "c.locus", "")
    assert len(load_project(path, max_files=3, max_depth=3).source_order) == 3
    for files, depth in [(2, 64), (256, 2)]:
        with pytest.raises(CompileError, match="E405"):
            load_project(path, max_files=files, max_depth=depth)
    with pytest.raises(ValueError, match="positivi"):
        load_project(path, max_files=0)


def test_symlink_identity(tmp_path: Path) -> None:
    original = write(tmp_path, "parte.locus", "La Sala è una stanza.")
    try:
        (tmp_path / "alias.locus").symlink_to(original)
    except (OSError, NotImplementedError):
        pytest.skip("Creazione symlink non disponibile su questa piattaforma")
    path = write(tmp_path, "storia.locus", 'Includi "parte.locus". Includi "alias.locus".')
    assert len(compile_story_file(path).entities) == 1


def test_cli_expanded_ast(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write(tmp_path, "parte.locus", "La Sala è una stanza.")
    path = write(tmp_path, "storia.locus", 'Includi "parte.locus". Inizia nella "Sala".')
    assert main(["ast", str(path)]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["declarations"][0]["name"] == "Sala"
    assert len(data["source_order"]) == 2
    assert main(["controlla", str(path)]) == 0
    assert "1 entità" in capsys.readouterr().out


def test_relation_order_uses_modules_not_local_offsets(tmp_path: Path) -> None:
    write(
        tmp_path,
        "parte.locus",
        "La A è una stanza. La B è una stanza. La C è una stanza. La B è a nord della A.",
    )
    path = write(tmp_path, "storia.locus", 'Includi "parte.locus". La C è a nord della A.')
    with pytest.raises(CompileError) as caught:
        compile_story_file(path)
    assert caught.value.span.source == str(path)


def test_optional_project_boundary(tmp_path: Path) -> None:
    outside = write(tmp_path, "outside.locus", "La Sala è una stanza.")
    entry = write(tmp_path, "project/main.locus", 'Includi "../outside.locus".')
    with pytest.raises(CompileError, match="E404"):
        load_project(entry, allowed_root=entry.parent)
    assert outside.exists()
    assert len(load_project(entry).declarations) == 1


@pytest.mark.parametrize("preposition", ["nella", "nel", "nello", "nell'", "nell’"])
def test_entry_accepts_articulated_location_forms(preposition: str) -> None:
    source = f'La Sala è una stanza. Il Mercato è una stanza. Inizia {preposition} "Mercato".'
    session = start(instantiate(compile_story(source)))
    assert "Mercato" in render(step(session, parse_command("guarda")))
    with pytest.raises(CompileError, match="E406"):
        compile_story(source + ' Inizia nella "Sala".')


@pytest.mark.parametrize("preposition", ["in", "al", "nell"])
def test_entry_rejects_incomplete_or_wrong_prepositions(preposition: str) -> None:
    with pytest.raises(CompileError) as error:
        compile_story(f'La Sala è una stanza. Inizia {preposition} "Sala".')
    assert error.value.code == "E002"
    assert error.value.span.line == 1
