import unicodedata

import pytest

from italica.diagnostics import CompileError
from italica.lexer import tokenize
from italica.parser import parse


def test_tokens_preserve_original_positions() -> None:
    text = "\r\n  La Caffe\u0300 è una cosa."
    tokens = tokenize(text, "storia.ita")
    assert [t.kind for t in tokens] == ["WORD"] * 5 + ["DOT", "EOF"]
    name = tokens[1]
    assert name.text == "Caffe\u0300"
    assert name.normalized == "caffè"
    assert text[name.span.start : name.span.end] == name.text
    assert (name.span.line, name.span.column) == (2, 6)
    assert tokens[-1].span.start == len(text)


@pytest.mark.parametrize("newline", ["\n", "\r\n", "\r"])
def test_newlines(newline: str) -> None:
    program = parse(f"La A è una cosa.{newline}Il B è una cosa.")
    assert program.declarations[1].span.line == 2
    assert program.declarations[1].span.column == 1


@pytest.mark.parametrize("article", ["La", "Il", "Lo", "L'", "L’"])
@pytest.mark.parametrize("indefinite", ["un", "uno", "una", "un'", "un’"])
def test_articles_are_syntactic_not_gender_inference(article: str, indefinite: str) -> None:
    result = parse(f"{article} oggetto è {indefinite} cosa.")
    assert result.declarations[0].name == "oggetto"
    assert result.declarations[0].kind == "cosa"


def test_compound_names_case_and_span() -> None:
    source = "LA chiave di ottone È UNA COSA."
    declaration = parse(source, "prova.ita").declarations[0]
    assert declaration.name == "chiave di ottone"
    assert declaration.kind == "COSA"
    assert declaration.span.start == 0
    assert declaration.span.end == len(source)
    assert declaration.span.source == "prova.ita"


def test_decomposed_copula() -> None:
    assert parse(unicodedata.normalize("NFD", "La chiave è una cosa.")).declarations


@pytest.mark.parametrize(
    ("source", "code"),
    [
        ("La chiave è una cosa", "E002"),
        ("La chiave e una cosa.", "E002"),
        ("La è una cosa.", "E002"),
        ("La chiave è una .", "E002"),
        ("chiave è una cosa.", "E002"),
        ("L oggetto è una cosa.", "E002"),
        ("La chiave è cosa.", "E002"),
        ("La chiave è una cosa..", "E002"),
        ("La chiave è una cosa. testo", "E002"),
        ("La chiave è una cosa!", "E001"),
        ("La chiave2 è una cosa.", "E001"),
        ("La sala d'armi è una stanza.", "E002"),
        ("\ufeffLa chiave è una cosa.", "E001"),
    ],
)
def test_rejected_syntax(source: str, code: str) -> None:
    with pytest.raises(CompileError) as result:
        parse(source, "errore.ita")
    assert result.value.code == code
    assert "errore.ita:1:" in str(result.value)


def test_empty_source() -> None:
    assert parse(" \t\n").declarations == ()
