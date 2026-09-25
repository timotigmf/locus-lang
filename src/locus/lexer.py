"""Lexer deterministico: nessuna conoscenza di tipi o mondo."""

import unicodedata
from dataclasses import dataclass
from typing import Literal

from locus.diagnostics import CompileError, Span, canonical

TokenKind = Literal[
    "WORD", "APOSTROPHE", "DOT", "NUMBER", "STRING", "COLON", "SEMI", "LPAR", "RPAR", "EOF"
]


@dataclass(frozen=True, slots=True)
class Token:
    kind: TokenKind
    text: str
    span: Span

    @property
    def normalized(self) -> str:
        return canonical(self.text)


def tokenize(text: str, source: str = "<memoria>") -> tuple[Token, ...]:
    tokens: list[Token] = []
    offset, line, column = 0, 1, 1
    while offset < len(text):
        char = text[offset]
        if char in " \t\r\n":
            if char == "\n" or (char == "\r" and text[offset : offset + 2] != "\r\n"):
                line, column = line + 1, 1
            elif char != "\r":
                column += 1
            offset += 1
            continue
        start, start_column = offset, column
        kind: TokenKind
        if char.isalpha():
            kind = "WORD"
            offset += 1
            while offset < len(text) and (
                text[offset].isalpha() or unicodedata.category(text[offset]).startswith("M")
            ):
                offset += 1
        elif char == '"':
            kind = "STRING"
            offset += 1
            while offset < len(text) and text[offset] != '"':
                if text[offset] in "\r\n":
                    raise CompileError(
                        "E003",
                        "Una stringa deve terminare sulla stessa riga.",
                        Span(source, start, offset, line, start_column),
                    )
                if text[offset] == "\\":
                    offset += 1
                    if offset >= len(text) or text[offset] not in '\\"n':
                        raise CompileError(
                            "E003",
                            "Sequenza di escape non valida.",
                            Span(source, start, offset, line, start_column),
                        )
                offset += 1
            if offset >= len(text):
                raise CompileError(
                    "E003",
                    "Stringa senza virgolette finali.",
                    Span(source, start, offset, line, start_column),
                )
            offset += 1
        elif char in "0123456789" or (
            char == "-" and text[offset + 1 : offset + 2] in tuple("0123456789")
        ):
            if offset > 0 and (
                text[offset - 1].isalpha() or unicodedata.category(text[offset - 1]).startswith("M")
            ):
                raise CompileError(
                    "E001",
                    "Separare il numero dal nome con uno spazio.",
                    Span(source, offset, offset + 1, line, column),
                )
            kind = "NUMBER"
            offset += 1
            while offset < len(text) and text[offset] in "0123456789":
                offset += 1
        elif char in "'’":
            kind = "APOSTROPHE"
            offset += 1
        elif char in ":;()":
            punctuation: dict[str, TokenKind] = {
                ":": "COLON",
                ";": "SEMI",
                "(": "LPAR",
                ")": "RPAR",
            }
            kind = punctuation[char]
            offset += 1
        elif char == ".":
            kind = "DOT"
            offset += 1
        else:
            raise CompileError(
                "E001",
                f"Carattere non ammesso: {char!r}.",
                Span(source, offset, offset + 1, line, column),
            )
        column += offset - start
        tokens.append(
            Token(kind, text[start:offset], Span(source, start, offset, line, start_column))
        )
    tokens.append(Token("EOF", "", Span(source, offset, offset, line, column)))
    return tuple(tokens)
