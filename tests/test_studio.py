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


def test_bridge_exposes_current_list_values() -> None:
    studio = Studio()
    source = (
        "La Sala è una stanza. Il taccuino è una cosa nella Sala. "
        "La indizi è una proprietà elenco di testi. "
        'Azione "annotare" senza oggetti con comando "annota". '
        'Regola "annota" per annotare nella fase invece: '
        'aggiungi "orma" a "indizi" di "taccuino"; Fine regola.'
    )
    compiled = studio.compile(project(source))
    assert compiled["ok"]
    notebook_id = next(
        item["id"] for item in compiled["ir"]["entities"] if item["label"] == "taccuino"
    )
    restarted = studio.restart()
    assert (
        next(
            item
            for item in restarted["properties"]
            if item["entity_id"] == notebook_id and item["property_id"].endswith("indizi")
        )["value"]
        == ()
    )
    changed = studio.command("annota")
    assert next(
        item
        for item in changed["properties"]
        if item["entity_id"] == notebook_id and item["property_id"].endswith("indizi")
    )["value"] == ("orma",)


def test_bridge_exposes_current_table_rows() -> None:
    studio = Studio()
    source = """
La Sala è una stanza.
Azione "trasferire" senza oggetti con comando "trasferisci".
Tabella "deposito":
    Colonna "nome" testuale.
    Colonna "valore" numerica.
    Riga "astrolabio" 40.
Fine tabella.
Regola "trasferimento" per trasferire nella fase invece:
    rimuovi riga "astrolabio" 40 da tabella "deposito";
    aggiungi riga "maschera" 25 a tabella "deposito";
Fine regola.
"""
    compiled = studio.compile(project(source))
    assert compiled["ok"] and compiled["ir"]["tables"][0]["rows"] == (("astrolabio", 40),)
    assert studio.restart()["tables"][0]["rows"] == (("astrolabio", 40),)
    assert studio.command("trasferisci")["tables"][0]["rows"] == (("maschera", 25),)


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


def test_map_updates_when_a_secret_passage_is_revealed() -> None:
    studio = Studio()
    result = studio.compile(
        project(
            "La Sala è una stanza. La Cripta è una stanza. "
            "La leva è una cosa nella Sala. "
            'Regola "rivela" per esaminare "leva" nella fase dopo: '
            'crea relazione "nord" da "Sala" a "Cripta"; Fine regola.'
        )
    )
    assert result["map"]["links"] == []
    assert studio.restart()["map"]["links"] == []
    revealed = studio.command("esamina leva")
    assert revealed["map"]["links"] == [{"from": "e1", "to": "e2", "direction": "nord"}]
    assert studio.command("nord")["room"] == "e2"


def test_dynamic_relation_diagnostic_links_the_reference() -> None:
    studio = Studio()
    result = studio.compile(
        project(
            "La Sala è una stanza. La leva è una cosa nella Sala. "
            'Regola "errata" per esaminare "leva" nella fase dopo: '
            'crea relazione "nella" da "leva" a "Sala"; Fine regola.'
        )
    )
    diagnostic = result["diagnostics"][0]
    assert diagnostic["code"] == "E312"
    assert diagnostic["title"] == "Relazione dinamica non valida"
    assert diagnostic["manual"] == "docs/linguaggio/relazioni-dinamiche.md"
    assert Path(diagnostic["manual"]).is_file()


def test_list_diagnostic_links_the_specific_reference() -> None:
    studio = Studio()
    result = studio.compile(
        project(
            "La Sala è una stanza. Il taccuino è una cosa nella Sala. "
            "La indizi è una proprietà elenco di testi. "
            'Regola "errata" per guardare nella fase dopo: '
            'aggiungi 1 a "indizi" di "taccuino"; Fine regola.'
        )
    )
    diagnostic = result["diagnostics"][0]
    assert diagnostic["code"] == "E313"
    assert diagnostic["title"] == "Elemento di elenco non valido"
    assert diagnostic["manual"] == "docs/linguaggio/liste-tipate.md"
    assert Path(diagnostic["manual"]).is_file()


def test_table_diagnostic_links_the_specific_reference() -> None:
    studio = Studio()
    result = studio.compile(
        project('Tabella "prezzi": Colonna "valore" numerica. Riga "dieci". Fine tabella.')
    )
    diagnostic = result["diagnostics"][0]
    assert diagnostic["code"] == "E117"
    assert diagnostic["title"] == "Riga di tabella non valida"
    assert diagnostic["manual"] == "docs/linguaggio/tabelle-tipate.md"
    assert Path(diagnostic["manual"]).is_file()


def test_dialogue_diagnostic_links_the_specific_reference() -> None:
    studio = Studio()
    result = studio.compile(
        project(
            "La Sala è una stanza. La guida è una persona nella Sala. "
            'Dialogo "incompleto" con "guida": Fine dialogo.'
        )
    )
    diagnostic = result["diagnostics"][0]
    assert diagnostic["code"] == "E119"
    assert diagnostic["title"] == "Grafo del dialogo non valido"
    assert diagnostic["manual"] == "docs/linguaggio/dialoghi-strutturati.md"
    assert Path(diagnostic["manual"]).is_file()


def test_scene_diagnostic_links_the_specific_reference() -> None:
    studio = Studio()
    result = studio.compile(
        project('Scena "contraddizione" dal turno 4 al turno 2: Inizio "x". Fine "y". Fine scena.')
    )
    diagnostic = result["diagnostics"][0]
    assert diagnostic["code"] == "E122"
    assert diagnostic["title"] == "Scena non valida"
    assert diagnostic["manual"] == "docs/linguaggio/scene-tempo-punteggio.md"
    assert Path(diagnostic["manual"]).is_file()


def test_studio_exposes_author_types_and_maps_room_subtypes() -> None:
    studio = Studio()
    result = studio.compile(
        project(
            "Un osservatorio è un tipo di stanza. "
            "Una reliquia è un tipo di cosa. "
            "La Torre è un osservatorio. Il disco è una reliquia nella Torre."
        )
    )
    assert result["ok"]
    assert [room["label"] for room in result["map"]["rooms"]] == ["Torre"]
    assert any(item["label"] == "osservatorio" for item in result["ir"]["types"])
    assert any(item["label"] == "reliquia" for item in result["ir"]["types"])


def test_studio_executes_and_exposes_author_actions() -> None:
    studio = Studio()
    result = studio.compile(
        project(
            "La Sala è una stanza. Il gong è una cosa nella Sala. "
            "Il martello è una cosa nella Sala. "
            'Azione "suonare" su una cosa con una cosa con comando "suona" '
            'e sinonimo "fai risuonare" e separatore "insieme a". '
            'Regola "gong" per suonare "gong" con "martello" nella fase invece: '
            'dì "Il gong risuona."; Fine regola.'
        )
    )
    assert result["ok"] and result["actions"] == 1
    assert result["ir"]["actions"][0]["commands"] == ("suona", "fai risuonare")
    assert result["ir"]["actions"][0]["separators"] == ("insieme a",)
    studio.restart()
    assert studio.command("suona gong insieme al martello")["text"] == "Il gong risuona."
    assert studio.command("fai risuonare gong insieme al martello")["text"] == ("Il gong risuona.")


def test_studio_exposes_and_executes_dialogue_graphs() -> None:
    studio = Studio()
    source = Path("examples/tutorial/16_dialogo_guardiana.locus").read_text(encoding="utf-8")
    compiled = studio.compile(project(source))
    assert compiled["ok"] and compiled["dialogues"] == 1
    dialogue = compiled["ir"]["dialogues"][0]
    assert dialogue["label"] == "memorie della guardiana"
    assert len(dialogue["nodes"]) == 3

    studio.restart()
    opened = studio.command("parla con guardiana")
    assert "1. Chiedi della tempesta" in opened["text"]
    assert opened["active_dialogue"] == dialogue["id"]
    assert opened["dialogue"][0]["node_label"] == "inizio"

    storm = studio.command("1")
    assert "spense la luce" in storm["text"]
    assert storm["dialogue"][0]["choice_label"] == "Chiedi della tempesta"
    assert len(storm["visited_dialogue_nodes"]) == 2

    ended = studio.command("basta")
    assert ended["active_dialogue"] is None
    assert "termina" in ended["text"]


def test_studio_exposes_scene_time_score_and_log() -> None:
    studio = Studio()
    source = Path("examples/tutorial/17_tempesta_e_punteggio.locus").read_text(encoding="utf-8")
    compiled = studio.compile(project(source))
    assert compiled["ok"] and compiled["scenes"] == 1
    assert compiled["ir"]["scenes"][0]["points"] == 10
    assert studio.restart()["turn"] == 0

    started = studio.command("guarda")
    assert started["turn"] == 1
    assert started["scenes"][0]["event"] == "iniziata"
    assert "tempesta è iniziata" in started["text"]
    studio.command("inventario")
    ended = studio.command("esamina orologio")
    assert ended["turn"] == 3 and ended["score"] == 10
    assert ended["scenes"][0]["score_delta"] == 10
    assert ended["score_log"][0]["scene_label"] == "la tempesta"
    score = studio.command("punteggio")
    assert score["text"] == "Punteggio: 10."
    assert score["turn"] == 3


def test_dispatch_errors_and_size_limit() -> None:
    studio = Studio()
    assert not json.loads(studio.dispatch("{"))["ok"]
    assert not json.loads(studio.dispatch('{"operation":"ignota"}'))["ok"]
    with pytest.raises(ValueError, match="grande"):
        validate_project(project("a" * 2_000_001))
