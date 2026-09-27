from dataclasses import FrozenInstanceError

import pytest

from locus.compiler import compile_source
from locus.diagnostics import CompileError
from locus.ir import IR_VERSION, ActionIR, EntityIR, ProgramIR, SynonymIR, TypeIR
from locus.parser import parse
from locus.runtime import instantiate
from locus.schema import RelationSpec
from locus.stdlib import THING, default_kinds
from locus.stdlib.authoring import compile_story


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


def test_author_types_allow_forward_parents_and_inheritance() -> None:
    source = (
        "Una reliquia è un tipo di gioiello. "
        "Un gioiello è un tipo di cosa. "
        "Il rubino è una reliquia."
    )
    syntax = parse(source)
    assert [(item.name, item.parent) for item in syntax.kinds] == [
        ("reliquia", "gioiello"),
        ("gioiello", "cosa"),
    ]
    program = compile_story(source)
    types = {item.label: item for item in program.types}
    assert types["reliquia"].parent_id == types["gioiello"].id
    assert types["gioiello"].parent_id == THING
    assert program.entities[0].type_id == types["reliquia"].id
    world = instantiate(program)
    assert next(item.label for item in world.types if item.id == THING) == "cosa"


def test_author_subtype_works_in_a_non_narrative_catalog() -> None:
    program = compile_source(
        "Un sensore è un tipo di dispositivo. "
        "Il radar è un sensore nella Zona. La Zona è una area.",
        {"dispositivo": "lab.device", "area": "lab.area"},
        relations={"nella": RelationSpec("lab.inside", "lab.device", "lab.area")},
    )
    assert program.relations[0].predicate_id == "lab.inside"
    assert program.types[-1].parent_id == "lab.device"


def test_author_type_ids_do_not_collide_with_host_ids() -> None:
    program = compile_source(
        "Un derivato è un tipo di base. Il valore è un derivato.",
        {"base": "autore.t1"},
    )
    assert [item.id for item in program.types] == ["autore.t1", "autore.t2"]


def test_apostrophe_article_in_author_type() -> None:
    program = compile_story("Un'arma è un tipo di cosa. La sciabola è un'arma.")
    assert program.entities[0].type_id == program.types[-1].id


@pytest.mark.parametrize(
    ("source", "code"),
    [
        ("Una cosa è un tipo di cosa.", "E113"),
        ("Un gioiello è un tipo di cosa. Un GIOIELLO è un tipo di cosa.", "E113"),
        ("Una reliquia è un tipo di tipo assente.", "E102"),
        ("Un alfa è un tipo di beta. Un beta è un tipo di alfa.", "E114"),
    ],
)
def test_invalid_author_type_hierarchy(source: str, code: str) -> None:
    with pytest.raises(CompileError) as caught:
        compile_story(source)
    assert caught.value.code == code


def test_runtime_rejects_invalid_type_hierarchy() -> None:
    entity = EntityIR("e1", "A", "a")
    with pytest.raises(ValueError, match="Gerarchia"):
        instantiate(ProgramIR(IR_VERSION, (entity,), types=(TypeIR("a", "A", "b"),)))
    with pytest.raises(ValueError, match="ciclo"):
        instantiate(
            ProgramIR(
                IR_VERSION,
                (entity,),
                types=(TypeIR("a", "A", "b"), TypeIR("b", "B", "a")),
            )
        )


def test_author_action_is_compiled_by_the_generic_core() -> None:
    source = 'Azione "calcolare" senza oggetti con comando "calcola".'
    syntax = parse(source)
    assert syntax.actions[0].name == "calcolare"
    program = compile_source(source, {})
    assert program.actions == (ActionIR("autore.a1", "calcolare", ("calcola",)),)


def test_runtime_rejects_invalid_author_action_catalog() -> None:
    entity = EntityIR("e1", "A", "a")
    types = (TypeIR("a", "A"),)
    with pytest.raises(ValueError, match="azioni"):
        instantiate(
            ProgramIR(
                IR_VERSION,
                (entity,),
                types=types,
                actions=(ActionIR("x", "prova", ("prova",), "assente"),),
            )
        )
    with pytest.raises(ValueError, match="azioni"):
        instantiate(
            ProgramIR(
                IR_VERSION,
                (entity,),
                types=types,
                actions=(
                    ActionIR("x", "prima", ("prova",)),
                    ActionIR("y", "seconda", ("prova",)),
                ),
            )
        )


def test_runtime_rejects_invalid_action_forms_and_separators() -> None:
    entity = EntityIR("e1", "A", "a")
    types = (TypeIR("a", "A"),)
    invalid_actions = (
        ActionIR("x", "vuota", ()),
        ActionIR("x", "duplicata", ("prova", "prova")),
        ActionIR("x", "senza secondo oggetto", ("prova",), separators=("a",)),
        ActionIR("x", "senza separatore", ("prova",), "a", "a"),
        ActionIR("x", "separatore duplicato", ("prova",), "a", "a", ("a", "a")),
    )
    for action in invalid_actions:
        with pytest.raises(ValueError, match="azioni"):
            instantiate(ProgramIR(IR_VERSION, (entity,), types=types, actions=(action,)))


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
