import pytest

from locus.compiler import compile_source
from locus.diagnostics import CompileError
from locus.ir import IR_VERSION, EntityIR, ProgramIR, PropertyIR
from locus.lexer import tokenize
from locus.parser import parse
from locus.runtime import instantiate
from locus.schema import PropertySpec, RelationSpec
from locus.stdlib.authoring import compile_story


def test_user_properties_forward_assignment_defaults_and_types() -> None:
    program = compile_source(
        "Il sensore ha soglia -12. Il sensore ha attivo vero. "
        'Il sensore ha etichetta "Valore: \\"rosso\\".\\nSeconda riga". '
        "Il sensore è un dispositivo. Il ricambio è un dispositivo. "
        "La soglia è una proprietà numerica. La attivo è una proprietà logica. "
        "La etichetta è una proprietà testuale.",
        {"dispositivo": "lab.sensor"},
    )
    values = {(v.entity_id, v.property_id): v.value for v in program.properties}
    assert values["e1", "autore.soglia"] == -12
    assert values["e1", "autore.attivo"] is True
    assert values["e1", "autore.etichetta"] == 'Valore: "rosso".\nSeconda riga'
    assert values["e2", "autore.soglia"] == 0
    assert values["e2", "autore.attivo"] is False
    assert values["e2", "autore.etichetta"] == ""
    assert instantiate(program).properties == program.properties


def test_typed_list_properties_start_empty() -> None:
    program = compile_source(
        "La scheda è un documento. "
        "La parole è una proprietà elenco di testi. "
        "La misure è una proprietà elenco di numeri. "
        "La verifiche è una proprietà elenco di logici.",
        {"documento": "document"},
    )
    assert {item.value for item in program.properties} == {()}
    assert {spec.value_kind for spec in program.property_specs} == {
        "elenco_testi",
        "elenco_numeri",
        "elenco_logici",
    }


@pytest.mark.parametrize(
    ("source", "code"),
    [
        ("La massa è una proprietà numerica. La massa è una proprietà testuale.", "E109"),
        ("La X è una cosa. La X ha ignota 1.", "E110"),
        ("La massa è una proprietà numerica. La X è una cosa. La X ha massa vero.", "E111"),
        ("La attivo è una proprietà logica. La X è una cosa. La X ha attivo 1.", "E111"),
        ("La nota è una proprietà testuale. La X è una cosa. La X ha nota falso.", "E111"),
        ("La massa è una proprietà numerica. La X ha massa 1.", "E103"),
        (
            "La massa è una proprietà numerica. La X è una cosa. La X ha massa 1. La X ha massa 1.",
            "E112",
        ),
        ('La X è una cosa. La X ha stato "aperto".', "E111"),
        ('La X è un contenitore. La X ha stato "socchiuso".', "E111"),
        ("La stato è una proprietà testuale.", "E109"),
        ('La indizi è una proprietà elenco di testi. La X è una cosa. La X ha indizi "x".', "E111"),
    ],
)
def test_invalid_properties(source: str, code: str) -> None:
    with pytest.raises(CompileError) as error:
        compile_story(source)
    assert error.value.code == code


@pytest.mark.parametrize("text", ['"incompleta', '"una\nriga"', '"escape\\q"'])
def test_malformed_strings(text: str) -> None:
    with pytest.raises(CompileError, match="E003"):
        tokenize(text)


def test_quoted_names_preserve_reserved_words_and_numeric_names() -> None:
    source = (
        'La "sala della torre" è una stanza. La "chiave 2" è una cosa nella "sala della torre".'
    )
    result = compile_story(source)
    assert result.entities[0].label == "sala della torre"
    assert result.relations[0].target_id == result.entities[0].id
    assert parse(source).declarations[1].name == "chiave 2"


@pytest.mark.parametrize(
    "source",
    [
        'La "" è una cosa.',
        'La "a\\nb" è una cosa.',
        "La massa è una proprietà decimale.",
        "La X ha massa .",
    ],
)
def test_malformed_property_syntax(source: str) -> None:
    with pytest.raises(CompileError, match="E002"):
        parse(source)


def test_integer_size_limit_is_diagnostic_not_python_error() -> None:
    with pytest.raises(CompileError, match="E004"):
        parse("La X ha massa " + "1" * 1001 + ".")


@pytest.mark.parametrize(
    "spec",
    [
        PropertySpec("x", ("unknown",), "numero", 0),
        PropertySpec("x", ("object",), "numero", True),
        PropertySpec("x", ("object",), "testo", "missing", ("other",)),
        PropertySpec("x", ("object",), "numero", 0, (0, False)),
        PropertySpec("x", ("object",), "elenco_numeri", (1, True)),
    ],
)
def test_property_catalog_validation(spec: PropertySpec) -> None:
    with pytest.raises(ValueError):
        compile_source("", {"oggetto": "object"}, properties={"x": spec})


def test_runtime_checks_property_values_and_references() -> None:
    spec = PropertySpec("p", ("object",), "numero", 0)
    entity = EntityIR("e", "X", "object")
    for prop in [
        PropertyIR("e", "p", True),
        PropertyIR("missing", "p", 1),
        PropertyIR("e", "unknown", 2),
    ]:
        with pytest.raises(ValueError):
            instantiate(
                ProgramIR(IR_VERSION, (entity,), property_specs=(spec,), properties=(prop,))
            )


def test_registered_verb_is_generic() -> None:
    program = compile_source(
        "Il sensore abilita il motore. Il sensore è un dispositivo. Il motore è un dispositivo.",
        {"dispositivo": "d"},
        relations={"abilita": RelationSpec("enables", "d", "d", verb="abilita")},
    )
    assert program.relations[0].predicate_id == "enables"
    with pytest.raises(ValueError):
        compile_source("", {"d": "d"}, relations={"x": RelationSpec("x", "d", "d", verb="ha")})


def test_typographic_apostrophe_duplicates_are_rejected() -> None:
    with pytest.raises(CompileError, match="E101"):
        compile_story('La "moneta d’oro" è una cosa. La "moneta d\'oro" è una cosa.')


def test_large_acyclic_graph_uses_iterative_validation() -> None:
    from locus.graph import cycle_node

    parents = {str(i): str(i + 1) for i in range(2000)}
    assert cycle_node(parents) is None
    parents["2000"] = "1000"
    assert cycle_node(parents) is not None
