"""Posizioni e diagnostica condivise dal frontend."""

import unicodedata
from dataclasses import dataclass


def canonical(text: str) -> str:
    """Normalizza per confronto, senza alterare il sorgente originale."""
    return " ".join(unicodedata.normalize("NFC", text).casefold().replace("’", "'").split())


@dataclass(frozen=True, slots=True)
class Span:
    source: str
    start: int
    end: int
    line: int
    column: int


class CompileError(Exception):
    def __init__(self, code: str, message: str, span: Span) -> None:
        self.code = code
        self.message = message
        self.span = span
        super().__init__(f"{span.source}:{span.line}:{span.column}: {code}: {message}")
