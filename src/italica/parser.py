"""Parser autore sostituibile dietro il contratto Program."""

from italica.ast import Declaration, Program
from italica.diagnostics import CompileError, Span
from italica.lexer import Token, tokenize


class _Parser:
    def __init__(self, tokens: tuple[Token, ...]) -> None:
        self.tokens = tokens
        self.index = 0

    @property
    def current(self) -> Token:
        return self.tokens[self.index]

    def fail(self, expected: str) -> None:
        actual = repr(self.current.text) if self.current.kind != "EOF" else "fine del file"
        raise CompileError("E002", f"Atteso {expected}; trovato {actual}.", self.current.span)

    def article(self, definite: bool) -> None:
        allowed = {"il", "lo", "la", "l"} if definite else {"un", "uno", "una"}
        token = self.current
        if token.kind != "WORD" or token.normalized not in allowed:
            self.fail("un articolo determinativo" if definite else "un articolo indeterminativo")
        self.index += 1
        if token.normalized == "l":
            if self.current.kind != "APOSTROPHE":
                self.fail("l'apostrofo dopo l")
            self.index += 1
        elif not definite and token.normalized == "un" and self.current.kind == "APOSTROPHE":
            self.index += 1

    def words(self, stop_at_copula: bool) -> str:
        words: list[str] = []
        while self.current.kind == "WORD":
            if self.current.normalized == "è":
                break
            words.append(self.current.text)
            self.index += 1
        if not words:
            self.fail("un nome" if stop_at_copula else "un nome di tipo")
        return " ".join(words)

    def program(self) -> Program:
        declarations: list[Declaration] = []
        while self.current.kind != "EOF":
            start = self.current.span
            self.article(definite=True)
            name = self.words(stop_at_copula=True)
            if self.current.kind != "WORD" or self.current.normalized != "è":
                self.fail("'è'")
            self.index += 1
            self.article(definite=False)
            kind = self.words(stop_at_copula=False)
            if self.current.kind != "DOT":
                self.fail("'.'")
            end = self.current.span.end
            self.index += 1
            declarations.append(
                Declaration(
                    name, kind, Span(start.source, start.start, end, start.line, start.column)
                )
            )
        return Program(tuple(declarations))


def parse(text: str, source: str = "<memoria>") -> Program:
    return _Parser(tokenize(text, source)).program()
