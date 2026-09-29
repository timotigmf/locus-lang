import pytest

from locus.compiler import compile_source
from locus.diagnostics import CompileError
from locus.ir import IR_VERSION, EntityIR, ProgramIR, RelationIR
from locus.parser import parse
from locus.runtime import instantiate
from locus.schema import RelationSpec
from locus.stdlib import default_kinds, default_relations

ROOMS = "La A è una stanza. La B è una stanza. La C è una stanza."


def test_forward_references_and_inverse() -> None:
    source = "Il Corridoio è a nord della Cucina. La chiave è una cosa nella Cucina. "
    source += "La Cucina è una stanza. Il Corridoio è una stanza."
    ast = parse(source)
    assert ast.declarations[0].location == "Cucina"
    assert ast.relations[0].subject == "Corridoio"
    assert ast.relations[0].span.start == 0
    program = compile_source(source, default_kinds(), relations=default_relations())
    assert set(program.relations) == {
        RelationIR("e2", "mondo.nord", "e3"),
        RelationIR("e3", "mondo.sud", "e2"),
        RelationIR("e1", "mondo.dentro", "e2"),
    }
    assert instantiate(program).relations == program.relations
    assert compile_source(source, default_kinds(), relations=default_relations()) == program


@pytest.mark.parametrize(
    ("statement", "code"),
    [
        ("La D è a nord della A.", "E103"),
        ("La A è a nord della D.", "E103"),
        ("La A è a nordnord della B.", "E104"),
        ("La chiave è una cosa. La chiave è a nord della A.", "E105"),
        ("La A è a nord della A.", "E107"),
        ("La B è a nord della A. La C è a nord della A.", "E106"),
        ("La B è a nord della A. La B è a nord della C.", "E106"),
        ("La chiave è una cosa nella D.", "E103"),
        ("La chiave è una cosa. La pietra è una cosa nella chiave.", "E105"),
        ("La D è una stanza nella A.", "E105"),
    ],
)
def test_invalid_relations(statement: str, code: str) -> None:
    with pytest.raises(CompileError) as error:
        compile_source(
            ROOMS + "\n" + statement, default_kinds(), "s.locus", relations=default_relations()
        )
    assert error.value.code == code
    assert error.value.span.line == 2


def test_repeated_equivalent_links_are_idempotent() -> None:
    source = ROOMS + "La B è a nord della A. La A è a sud della B. La B è a nord della A."
    assert (
        len(compile_source(source, default_kinds(), relations=default_relations()).relations) == 2
    )


def test_east_west_relations_are_inverse() -> None:
    program = compile_source(
        ROOMS + "La B è a est della A.", default_kinds(), relations=default_relations()
    )
    assert RelationIR("e1", "mondo.est", "e2") in program.relations
    assert RelationIR("e2", "mondo.ovest", "e1") in program.relations


@pytest.mark.parametrize(
    ("predicate", "relation", "inverse"),
    [
        ("nordest", "mondo.nordest", "mondo.sudovest"),
        ("sudest", "mondo.sudest", "mondo.nordovest"),
    ],
)
def test_diagonal_relations_are_inverse(predicate: str, relation: str, inverse: str) -> None:
    program = compile_source(
        ROOMS + f"La B è a {predicate} della A.",
        default_kinds(),
        relations=default_relations(),
    )
    assert RelationIR("e1", relation, "e2") in program.relations
    assert RelationIR("e2", inverse, "e1") in program.relations


def test_diagonal_destination_conflict_is_rejected() -> None:
    with pytest.raises(CompileError) as error:
        compile_source(
            ROOMS + "La B è a nordest della A. La C è a nordest della A.",
            default_kinds(),
            relations=default_relations(),
        )
    assert error.value.code == "E106"


def test_vertical_relation_uses_natural_italian_verb_and_inverse() -> None:
    program = compile_source(
        ROOMS + "La B sovrasta la A.",
        default_kinds(),
        relations=default_relations(),
    )
    assert RelationIR("e1", "mondo.sopra", "e2") in program.relations
    assert RelationIR("e2", "mondo.sotto", "e1") in program.relations


def test_vertical_destination_conflict_is_rejected() -> None:
    with pytest.raises(CompileError) as error:
        compile_source(
            ROOMS + "La B sovrasta la A. La C sovrasta la A.",
            default_kinds(),
            relations=default_relations(),
        )
    assert error.value.code == "E106"


def test_inward_relation_uses_natural_italian_verb_and_inverse() -> None:
    program = compile_source(
        ROOMS + "La A racchiude la B.",
        default_kinds(),
        relations=default_relations(),
    )
    assert RelationIR("e1", "mondo.interno", "e2") in program.relations
    assert RelationIR("e2", "mondo.esterno", "e1") in program.relations


def test_inward_destination_conflict_is_rejected() -> None:
    with pytest.raises(CompileError) as error:
        compile_source(
            ROOMS + "La A racchiude la B. La A racchiude la C.",
            default_kinds(),
            relations=default_relations(),
        )
    assert error.value.code == "E106"


def test_catalog_is_required_and_replaceable() -> None:
    with pytest.raises(CompileError, match="E104"):
        compile_source(ROOMS + "La B è a nord della A.", default_kinds())
    program = compile_source(
        "Il Sensore è a fianco della Centralina. Il Sensore è un dispositivo. "
        "La Centralina è un dispositivo.",
        {"dispositivo": "lab.device"},
        relations={"fianco": RelationSpec("lab.peer", "lab.device", "lab.device")},
    )
    assert program.relations == (RelationIR("e1", "lab.peer", "e2"),)


@pytest.mark.parametrize(
    "catalog",
    [
        {"nord": RelationSpec("n", "missing", "mondo.stanza")},
        {"Nord": RelationSpec("n", "mondo.stanza", "mondo.stanza")},
        {"nord": RelationSpec("", "mondo.stanza", "mondo.stanza")},
        {"nord": RelationSpec("n", "mondo.stanza", "mondo.stanza", inverse_id="missing")},
        {
            "nord": RelationSpec("n", "mondo.stanza", "mondo.stanza"),
            "sud": RelationSpec("n", "mondo.stanza", "mondo.stanza"),
        },
    ],
)
def test_invalid_relation_catalog(catalog: dict[str, RelationSpec]) -> None:
    with pytest.raises(ValueError):
        compile_source("", default_kinds(), relations=catalog)


@pytest.mark.parametrize(
    "source",
    [
        "La stanza della torre è una stanza.",
        "La cosa è una cosa nella .",
        "La A è a nord della .",
        "La A è a nord B.",
        "La A è a della B.",
    ],
)
def test_delimiters_and_missing_operands(source: str) -> None:
    with pytest.raises(CompileError, match="E002"):
        parse(source)


def test_world_rejects_invalid_internal_edges() -> None:
    entity = EntityIR("e1", "A", "x")
    with pytest.raises(ValueError, match="assente"):
        instantiate(ProgramIR(IR_VERSION, (entity,), (RelationIR("e1", "p", "missing"),)))
    edge = RelationIR("e1", "p", "e1")
    with pytest.raises(ValueError, match="duplicate"):
        instantiate(ProgramIR(IR_VERSION, (entity,), (edge, edge)))


def test_double_location_in_custom_schema_conflicts() -> None:
    with pytest.raises(CompileError, match="E106"):
        compile_source(
            "La X è un nodo. La A è un nodo. La B è un nodo. "
            "La X è a sede della A. La X è a sede della B.",
            {"nodo": "node"},
            relations={"sede": RelationSpec("location", "node", "node")},
        )
