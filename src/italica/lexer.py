"""Lexer deterministico: nessuna conoscenza di tipi o mondo."""

import unicodedata
from dataclasses import dataclass
from typing import Literal

from italica.diagnostics import CompileError, Span, canonical

TokenKind = Literal["WORD", "APOSTROPHE", "DOT", "EOF"]


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
        elif char in "'’":
            kind = "APOSTROPHE"
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
