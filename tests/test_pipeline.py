from dataclasses import FrozenInstanceError

import pytest

from locus.compiler import compile_source
from locus.diagnostics import CompileError
from locus.ir import IR_VERSION, EntityIR, ProgramIR, SynonymIR
from locus.runtime import instantiate
from locus.stdlib import default_kinds


def test_pipeline_and_determinism() -> None:
    source = "La Cucina è una stanza. La chiave è una cosa."
    program = compile_source(source, default_kinds())
    assert program == compile_source(source, default_kinds())
    assert program.entities == (
        EntityIR("e1", "Cucina", "mondo.stanza"),
        EntityIR("e2", "chiave", "mondo.cosa"),
    )
    world = instantiate(program)
    other = instantiate(program)
    assert world == other and world is not other
    assert world.entities[0] is not other.entities[0]
    with pytest.raises(FrozenInstanceError):
        world.entities[0].label = "mutato"  # type: ignore[misc]


def test_non_narrative_catalog() -> None:
    program = compile_source("Il sensore è un dispositivo.", {"dispositivo": "lab.device"})
    assert instantiate(program).entities[0].type_id == "lab.device"


@pytest.mark.parametrize(
    "source",
    [
        "La chiave è una cosa. IL CHIAVE è una cosa.",
        "La chiave di ottone è una cosa. La chiave  di ottone è una cosa.",
        "Il Caffè è una cosa. Il Caffe\u0300 è una cosa.",
    ],
)
def test_duplicate_canonical_names(source: str) -> None:
    with pytest.raises(CompileError, match="E101"):
        compile_source(source, default_kinds())


def test_unknown_type_and_error_location() -> None:
    with pytest.raises(CompileError) as result:
        compile_source("La Cucina è una stanza.\nIl cane è un animale.", default_kinds(), "a.locus")
    assert result.value.code == "E102"
    assert result.value.span.line == 2
    assert "Tipo sconosciuto: animale" in str(result.value)


@pytest.mark.parametrize("catalog", [{"Cosa": "x"}, {"": "x"}, {"cosa": " "}, {"a": "x", "b": "x"}])
def test_invalid_catalog(catalog: dict[str, str]) -> None:
    with pytest.raises(ValueError):
        compile_source("", catalog)


def test_catalogs_are_independent() -> None:
    changed = default_kinds()
    changed.clear()
    assert "stanza" in default_kinds()


def test_empty_world() -> None:
    assert instantiate(compile_source("", {})).entities == ()


def test_runtime_rejects_unknown_version_and_duplicate_ids() -> None:
    with pytest.raises(ValueError, match="Versione IR"):
        instantiate(ProgramIR(999, ()))
    duplicate = EntityIR("e1", "A", "x")
    with pytest.raises(ValueError, match="duplicati"):
        instantiate(ProgramIR(IR_VERSION, (duplicate, duplicate)))
    with pytest.raises(ValueError, match="Vocabolario"):
        instantiate(ProgramIR(IR_VERSION, (duplicate,), synonyms=(SynonymIR("A", "e1"),)))


def test_compound_type_name() -> None:
    program = compile_source("Il sensore è un dispositivo digitale.", {"dispositivo digitale": "x"})
    assert program.entities[0].type_id == "x"


def test_story_metadata_and_vocabulary_are_compiled() -> None:
    program = compile_source(
        'Titolo: "La torre". Autore: "Ada". La custodia è una cosa. '
        'Comprendi "cassa" come "custodia".',
        default_kinds(),
    )
    assert program.title == "La torre"
    assert program.author == "Ada"
    assert program.synonyms[0].alias == "cassa"
    assert program.synonyms[0].target_id == "e1"
    world = instantiate(program)
    assert world.title == "La torre" and world.author == "Ada"


@pytest.mark.parametrize(
    ("source", "code"),
    [
        ('Titolo: "A". Titolo: "B".', "E408"),
        ('La cassa è una cosa. Comprendi "cassa" come "cassa".', "E409"),
        ('La custodia è una cosa. Comprendi "" come "custodia".', "E002"),
        (
            'La custodia è una cosa. Comprendi "cassa" come "custodia". '
            'Comprendi "CASSA" come "custodia".',
            "E409",
        ),
        ('Comprendi "cassa" come "assente".', "E103"),
    ],
)
def test_invalid_metadata_and_vocabulary(source: str, code: str) -> None:
    with pytest.raises(CompileError) as caught:
        compile_source(source, default_kinds())
    assert caught.value.code == code
