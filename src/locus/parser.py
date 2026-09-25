"""Parser autore sostituibile dietro il contratto Program."""

from locus.ast import Declaration, Program, Relation
from locus.diagnostics import CompileError, Span
from locus.lexer import Token, tokenize

_RESERVED = {"è", "nella", "della"}


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

    def keyword(self, word: str) -> None:
        if self.current.kind != "WORD" or self.current.normalized != word:
            self.fail(repr(word))
        self.index += 1

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

    def words(self) -> str:
        words: list[str] = []
        while self.current.kind == "WORD" and self.current.normalized not in _RESERVED:
            words.append(self.current.text)
            self.index += 1
        if not words:
            self.fail("un nome senza parole riservate")
        return " ".join(words)

    def finish(self, start: Span) -> Span:
        if self.current.kind != "DOT":
            self.fail("'.'")
        span = Span(start.source, start.start, self.current.span.end, start.line, start.column)
        self.index += 1
        return span

    def program(self) -> Program:
        declarations: list[Declaration] = []
        relations: list[Relation] = []
        while self.current.kind != "EOF":
            start = self.current.span
            self.article(definite=True)
            name = self.words()
            self.keyword("è")
            if self.current.normalized == "a":
                self.keyword("a")
                predicate = self.words()
                self.keyword("della")
                target = self.words()
                relations.append(Relation(name, predicate, target, self.finish(start)))
            else:
                self.article(definite=False)
                kind = self.words()
                location = None
                if self.current.normalized == "nella":
                    self.keyword("nella")
                    location = self.words()
                declarations.append(Declaration(name, kind, self.finish(start), location))
        return Program(tuple(declarations), tuple(relations))


def parse(text: str, source: str = "<memoria>") -> Program:
    return _Parser(tokenize(text, source)).program()
