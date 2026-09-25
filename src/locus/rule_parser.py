"""Grammatica controllata delle regole sul cursore del frontend autore."""

from typing import Protocol, cast

from locus.ast import ActionSyntax, EffectSyntax, PropertyReference, Rule
from locus.diagnostics import CompileError, Span
from locus.lexer import Token, TokenKind
from locus.rule_model import Condition, EffectKind, Operator, Phase
from locus.schema import Value

PHASES = {"prima", "invece", "verifica", "esegui", "dopo", "descrivi"}


class Cursor(Protocol):
    index: int

    @property
    def current(self) -> Token: ...
    def keyword(self, word: str) -> None: ...
    def value(self) -> Value: ...
    def fail(self, expected: str) -> None: ...
    def finish(self, start: Span) -> Span: ...


class RuleParser:
    def __init__(self, cursor: Cursor) -> None:
        self.cursor = cursor

    def punctuation(self, kind: TokenKind) -> None:
        if self.cursor.current.kind != kind:
            names = {"COLON": "':'", "SEMI": "';'", "RPAR": "')'"}
            self.cursor.fail(names.get(kind, kind))
        self.cursor.index += 1

    def quoted(self, *, name: bool = True) -> str:
        if self.cursor.current.kind != "STRING":
            self.cursor.fail("una stringa tra virgolette")
        text = self.cursor.value()
        assert isinstance(text, str)
        if name and (not text.strip() or "\n" in text):
            self.cursor.fail("un nome non vuoto su una riga")
        return text

    def action(self) -> ActionSyntax:
        words: list[str] = []
        while self.cursor.current.kind == "WORD" and self.cursor.current.normalized not in {
            "nella",
            "con",
        }:
            words.append(self.cursor.current.text)
            self.cursor.index += 1
        if not words:
            self.cursor.fail("un nome di azione")
        target = self.quoted() if self.cursor.current.kind == "STRING" else None
        indirect = None
        if self.cursor.current.normalized == "con":
            self.cursor.keyword("con")
            indirect = self.quoted()
        return ActionSyntax(" ".join(words), target, indirect)

    def reference(self) -> PropertyReference:
        property_name = self.quoted()
        self.cursor.keyword("di")
        return PropertyReference(self.quoted(), property_name)

    def expression(self, depth: int = 0) -> Condition[PropertyReference]:
        items = [self.conjunction(depth)]
        while self.cursor.current.normalized == "o":
            self.cursor.keyword("o")
            items.append(self.conjunction(depth))
        return items[0] if len(items) == 1 else Condition("o", operands=tuple(items))

    def conjunction(self, depth: int) -> Condition[PropertyReference]:
        items = [self.unary(depth)]
        while self.cursor.current.normalized == "e":
            self.cursor.keyword("e")
            items.append(self.unary(depth))
        return items[0] if len(items) == 1 else Condition("e", operands=tuple(items))

    def unary(self, depth: int) -> Condition[PropertyReference]:
        if depth > 64:
            raise CompileError(
                "E302", "Condizione troppo annidata (massimo 64 livelli).", self.cursor.current.span
            )
        if self.cursor.current.normalized == "non":
            self.cursor.keyword("non")
            return Condition("non", operands=(self.unary(depth + 1),))
        if self.cursor.current.kind == "LPAR":
            self.cursor.index += 1
            result = self.expression(depth + 1)
            self.punctuation("RPAR")
            return result
        if self.cursor.current.normalized in {"vero", "falso"}:
            boolean = cast(Operator, self.cursor.current.normalized)
            self.cursor.index += 1
            return Condition(boolean)
        reference = self.reference()
        self.cursor.keyword("è")
        operator = "uguale"
        if self.cursor.current.normalized in {"maggiore", "minore", "almeno", "al", "diverso"}:
            word = self.cursor.current.normalized
            self.cursor.index += 1
            if word in {"maggiore", "minore"}:
                self.cursor.keyword("di")
            elif word == "diverso":
                self.cursor.keyword("da")
            elif word == "al":
                self.cursor.keyword("massimo")
            operator = "massimo" if word == "al" else word
        return Condition(cast(Operator, operator), reference, self.cursor.value())

    def effect(self) -> EffectSyntax:
        start = self.cursor.current.span
        word = self.cursor.current.normalized
        self.cursor.index += 1
        value: Value | None = None
        reference = None
        action = None
        if word in {"dì", "fallisci"}:
            value = self.quoted(name=False)
        elif word in {"imposta", "aumenta", "diminuisci"}:
            reference = self.reference()
            self.cursor.keyword("a" if word == "imposta" else "di")
            if word != "imposta" and self.cursor.current.kind != "NUMBER":
                self.cursor.fail("un intero")
            value = self.cursor.value()
            if word == "diminuisci":
                assert type(value) is int
                value = -value
                word = "aumenta"
        elif word == "sostituisci":
            self.cursor.keyword("con")
            action = self.action()
        elif word == "restituisci":
            value = self.cursor.value()
        elif word not in {"continua", "interrompi"}:
            raise CompileError("E302", "Istruzione di regola non riconosciuta.", start)
        end = self.cursor.current.span.end
        self.punctuation("SEMI")
        return EffectSyntax(
            cast(EffectKind, word),
            value,
            reference,
            action,
            Span(start.source, start.start, end, start.line, start.column),
        )

    def rule(self) -> Rule:
        start = self.cursor.current.span
        self.cursor.keyword("regola")
        name = self.quoted()
        self.cursor.keyword("per")
        action = self.action()
        self.cursor.keyword("nella")
        self.cursor.keyword("fase")
        phase = self.cursor.current.normalized
        if phase not in PHASES:
            self.cursor.fail("prima, invece, verifica, esegui, dopo o descrivi")
        self.cursor.index += 1
        priority = 0
        if self.cursor.current.normalized == "priorità":
            self.cursor.keyword("priorità")
            if self.cursor.current.kind != "NUMBER":
                self.cursor.fail("una priorità intera")
            value = self.cursor.value()
            assert type(value) is int
            priority = value
        condition: Condition[PropertyReference] = Condition("vero")
        if self.cursor.current.normalized == "quando":
            self.cursor.keyword("quando")
            condition = self.expression()
        self.punctuation("COLON")
        effects: list[EffectSyntax] = []
        while self.cursor.current.normalized != "fine":
            if self.cursor.current.kind == "EOF":
                self.cursor.fail("'Fine regola.'")
            effects.append(self.effect())
        if not effects:
            self.cursor.fail("almeno un'istruzione")
        self.cursor.keyword("fine")
        self.cursor.keyword("regola")
        return Rule(
            name,
            cast(Phase, phase),
            action,
            priority,
            condition,
            tuple(effects),
            self.cursor.finish(start),
        )
