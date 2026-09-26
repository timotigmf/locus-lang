import json
from pathlib import Path

import pytest

from locus.studio import Studio, validate_project


def project(source: str) -> dict[str, object]:
    return {"format": "locus-project-1", "entry": "storia.locus", "files": {"storia.locus": source}}


def test_bridge_matches_story_and_tests_do_not_mutate_session() -> None:
    studio = Studio()
    result = studio.compile(project("La Sala è una stanza. La chiave è una cosa nella Sala."))
    assert result["ok"] and result["entities"] == 2
    assert studio.restart()["text"] == "Sala\nVedi: chiave."
    original = studio.session
    result = studio.test(["prendi chiave"], "Sala\nVedi: chiave.\nHai preso: chiave.\n")
    assert result["passed"] is True
    assert studio.session is original
    assert studio.command("prendi chiave")["text"] == "Hai preso: chiave."


def test_bridge_exposes_story_metadata_and_uses_vocabulary() -> None:
    studio = Studio()
    result = studio.compile(
        project(
            'Titolo: "Il laboratorio". Autore: "Ada". La Sala è una stanza. '
            'La custodia è una cosa nella Sala. Comprendi "cassa" come "custodia".'
        )
    )
    assert result["title"] == "Il laboratorio" and result["author"] == "Ada"
    studio.restart()
    assert studio.command("x cassa")["text"].startswith("custodia\n")


def test_failed_compile_invalidates_previous_program() -> None:
    studio = Studio()
    studio.compile(project("La Sala è una stanza."))
    result = studio.compile(project("La Sala è un tipoignoto."))
    assert not result["ok"]
    diag = result["diagnostics"][0]
    assert diag["code"] == "E102"
    assert diag["file"] == "storia.locus"
    assert diag["line"] == 1 and diag["column"] == 1
    assert Path(diag["manual"]).is_file()
    assert studio.program is None
    with pytest.raises(ValueError):
        studio.restart()


@pytest.mark.parametrize(
    "name", ["../x.locus", "/x.locus", "C:/x.locus", "a//x.locus", "a/./x.locus", "x.py"]
)
def test_project_paths(name: str) -> None:
    with pytest.raises(ValueError):
        validate_project({"format": "locus-project-1", "entry": name, "files": {name: ""}})


def test_no_access_outside_virtual_project(tmp_path: Path) -> None:
    path = tmp_path / "privato.locus"
    path.write_text("La Segreta è una stanza.", encoding="utf-8")
    # Il riferimento assoluto è rifiutato anche se il file esiste.
    studio = Studio()
    result = studio.compile(project(f'Includi "{path.as_posix()}".'))
    assert result["diagnostics"][0]["code"] == "E404"


def test_virtual_submodules_and_trace_sources() -> None:
    studio = Studio()
    p = {
        "format": "locus-project-1",
        "entry": "storia.locus",
        "files": {
            "storia.locus": 'Includi "parti/mondo.locus". Inizia nella "Sala".',
            "parti/mondo.locus": "La Sala è una stanza. "
            'Regola "saluto" per guardare nella fase prima: dì "Ciao"; Fine regola.',
        },
    }
    assert studio.compile(p)["ok"]
    result = studio.restart()
    assert result["trace"][0]["origin"]["source"] == "parti/mondo.locus"
    assert result["text"].startswith("Ciao\n")


def test_exploratory_test_is_not_a_pass() -> None:
    studio = Studio()
    studio.compile(project("La Sala è una stanza."))
    assert studio.test(["guarda"])["passed"] is None
    assert studio.test(["guarda"], "altro")["passed"] is False
    result = studio.test(["esci", "guarda"])
    assert result["executed"] == 1
    assert result["requested"] == 2


def test_map_and_session_end() -> None:
    studio = Studio()
    source = Path("examples/porte_e_contenitori.locus").read_text(encoding="utf-8")
    result = studio.compile(project(source))
    assert len(result["map"]["rooms"]) == 2
    assert len(result["map"]["links"]) == 1
    assert result["map"]["doors"][0]["label"] == "porta rossa"
    studio.restart()
    assert studio.command("esci")["ended"]
    with pytest.raises(ValueError):
        studio.command("guarda")


def test_map_contains_north_and_east_links_once() -> None:
    studio = Studio()
    result = studio.compile(
        project(
            "La Sala è una stanza. La Torre è una stanza. La Serra è una stanza. "
            "La Torre è a nord della Sala. La Serra è a est della Sala."
        )
    )
    assert result["map"]["links"] == [
        {"from": "e1", "to": "e2", "direction": "nord"},
        {"from": "e1", "to": "e3", "direction": "est"},
    ]


def test_dispatch_errors_and_size_limit() -> None:
    studio = Studio()
    assert not json.loads(studio.dispatch("{"))["ok"]
    assert not json.loads(studio.dispatch('{"operation":"ignota"}'))["ok"]
    with pytest.raises(ValueError, match="grande"):
        validate_project(project("a" * 2_000_001))
