import base64
from dataclasses import replace
from pathlib import Path

import pytest

from locus.diagnostics import CompileError
from locus.ir import IR_VERSION, ResourceIR
from locus.runtime import instantiate
from locus.stdlib.authoring import compile_story, compile_story_file
from locus.studio import Studio, validate_project

SOURCE = """
Titolo: "Il molo illustrato".
La Sala è una stanza.
La Sala ha descrizione "Le onde urtano il pontile.".
La Sala ha immagine "media/molo.png".
La Sala ha suono "media/onde.ogg".
La Sala ha testo alternativo "Il molo al tramonto.".
"""


def project(source: str, assets: dict[str, str] | None = None) -> dict[str, object]:
    return {
        "format": "locus-project-1",
        "entry": "storia.locus",
        "files": {"storia.locus": source},
        "assets": assets or {},
    }


PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)
OGG = b"OggS" + b"\x00" * 20


def encoded(content: bytes) -> str:
    return base64.b64encode(content).decode("ascii")


def test_media_properties_build_a_typed_ir21_manifest() -> None:
    program = compile_story(SOURCE)
    assert IR_VERSION == 21
    assert program.resources == (
        ResourceIR("e1", "immagine", "media/molo.png", "image/png", "Il molo al tramonto."),
        ResourceIR("e1", "suono", "media/onde.ogg", "audio/ogg", "Il molo al tramonto."),
    )
    assert instantiate(program).resources == program.resources


@pytest.mark.parametrize(
    "line",
    [
        'La Sala ha immagine "../molo.png".',
        'La Sala ha immagine "media/molo.mp3".',
        'La Sala ha suono "https://example.test/onde.ogg".',
    ],
)
def test_unsafe_or_incoherent_media_is_rejected(line: str) -> None:
    with pytest.raises(CompileError, match="E126"):
        compile_story(f"La Sala è una stanza. {line}")


def test_file_compilation_requires_and_accepts_local_resources(tmp_path: Path) -> None:
    story = tmp_path / "storia.locus"
    story.write_text(
        'La Sala è una stanza. La Sala ha immagine "media/molo.png".', encoding="utf-8"
    )
    with pytest.raises(CompileError, match="E126"):
        compile_story_file(story)
    media = tmp_path / "media"
    media.mkdir()
    (media / "molo.png").write_bytes(PNG)
    assert compile_story_file(story).resources[0].path == "media/molo.png"


def test_studio_validates_assets_and_exposes_media_for_look() -> None:
    studio = Studio()
    result = studio.compile(
        project(
            SOURCE,
            {
                "media/molo.png": encoded(PNG),
                "media/onde.ogg": encoded(OGG),
            },
        )
    )
    assert result["ok"] and result["resources"] == 2
    started = studio.restart()
    assert [item["kind"] for item in started["media"]] == ["immagine", "suono"]
    assert started["media"][0]["alternative_text"] == "Il molo al tramonto."


def test_studio_reports_missing_resource_at_the_assignment() -> None:
    result = Studio().compile(project('La Sala è una stanza. La Sala ha immagine "media/x.png".'))
    assert not result["ok"]
    assert result["diagnostics"][0]["code"] == "E126"
    assert result["diagnostics"][0]["manual"] == "docs/linguaggio/risorse-multimediali.md"


def test_project_rejects_invalid_base64_and_runtime_rejects_bad_manifest() -> None:
    with pytest.raises(ValueError, match="Base64"):
        validate_project(project("La Sala è una stanza.", {"media/x.png": "%%%"}))
    with pytest.raises(ValueError, match="contenuto"):
        validate_project(project("La Sala è una stanza.", {"media/x.png": encoded(b"not a PNG")}))
    program = compile_story("La Sala è una stanza.")
    invalid = ResourceIR("e1", "video", "media/x.png", "image/png", "Sala")
    with pytest.raises(ValueError, match="Manifest"):
        instantiate(replace(program, resources=(invalid,)))
