"""Parser autore controllato: costrutti generici, verbi forniti dal chiamante."""

from collections.abc import Mapping
from typing import cast

from locus.ast import (
    ActionDeclaration,
    Assignment,
    Declaration,
    DialogueChoiceDeclaration,
    DialogueDeclaration,
    DialogueNodeDeclaration,
    EntryPoint,
    Inclusion,
    KindDeclaration,
    Metadata,
    Program,
    PropertyDeclaration,
    Relation,
    Rule,
    TableColumnDeclaration,
    TableDeclaration,
    TableRowDeclaration,
    Vocabulary,
)
from locus.diagnostics import CompileError, Span
from locus.lexer import Token, tokenize
from locus.rule_parser import RuleParser
from locus.schema import Scalar, Value, ValueKind

_LOCATIONS = {"nella", "nel", "nello", "nell"}
_GENITIVES = {"della", "del", "dello", "dell"}
_TARGETS = {"alla", "al", "allo", "all", "a"}
_RESERVED = {
    "è",
    "ha",
    "collega",
    "titolo",
    "autore",
    "comprendi",
    "come",
    *_LOCATIONS,
    *_GENITIVES,
}


def decode_string(text: str) -> str:
    result: list[str] = []
    index = 1
    while index < len(text) - 1:
        if text[index] == "\\":
            index += 1
            result.append("\n" if text[index] == "n" else text[index])
        else:
            result.append(text[index])
        index += 1
    return "".join(result)


class _Parser:
    def __init__(self, tokens: tuple[Token, ...], verbs: Mapping[str, str]) -> None:
        self.tokens = tokens
        self.index = 0
        self.verbs = verbs
        self.reserved = _RESERVED | set(verbs)

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
            self.apostrophe()
        elif not definite and token.normalized == "un" and self.current.kind == "APOSTROPHE":
            self.index += 1

    def apostrophe(self) -> None:
        if self.current.kind != "APOSTROPHE":
            self.fail("un apostrofo")
        self.index += 1

    def preposition(self, allowed: set[str]) -> None:
        word = self.current.normalized
        if self.current.kind != "WORD" or word not in allowed:
            self.fail("una preposizione: " + ", ".join(sorted(allowed)))
        self.index += 1
        if word in {"nell", "dell", "all"}:
            self.apostrophe()
        if word == "a":
            self.article(True)

    def words(self, *, value_follows: bool = False, stop: set[str] | None = None) -> str:
        if self.current.kind == "STRING":
            name = decode_string(self.current.text)
            if not name.strip() or "\n" in name:
                self.fail("un nome non vuoto su una riga")
            self.index += 1
            return name
        words: list[str] = []
        while self.current.kind == "WORD" and self.current.normalized not in self.reserved:
            if stop and words and self.current.normalized in stop:
                break
            if value_follows and self.current.normalized in {"vero", "falso"}:
                break
            words.append(self.current.text)
            self.index += 1
        if not words:
            self.fail("un nome senza parole riservate, oppure un nome tra virgolette")
        return " ".join(words)

    def value(self) -> Value:
        token = self.current
        if token.kind == "NUMBER":
            if len(token.text.lstrip("-")) > 1000:
                raise CompileError("E004", "Intero troppo lungo: massimo 1000 cifre.", token.span)
            value: Value = int(token.text)
        elif token.kind == "STRING":
            value = decode_string(token.text)
        elif token.kind == "WORD" and token.normalized in {"vero", "falso"}:
            value = token.normalized == "vero"
        else:
            self.fail("un intero, una stringa, vero o falso")
            raise AssertionError("irraggiungibile")
        self.index += 1
        return value

    def finish(self, start: Span) -> Span:
        if self.current.kind != "DOT":
            self.fail("'.'")
        span = Span(start.source, start.start, self.current.span.end, start.line, start.column)
        self.index += 1
        return span

    def program(self) -> Program:
        declarations: list[Declaration] = []
        kinds: list[KindDeclaration] = []
        actions: list[ActionDeclaration] = []
        tables: list[TableDeclaration] = []
        dialogues: list[DialogueDeclaration] = []
        relations: list[Relation] = []
        properties: list[PropertyDeclaration] = []
        assignments: list[Assignment] = []
        rules: list[Rule] = []
        inclusions: list[Inclusion] = []
        entries: list[EntryPoint] = []
        metadata: list[Metadata] = []
        vocabulary: list[Vocabulary] = []
        while self.current.kind != "EOF":
            if self.current.normalized == "dialogo":
                start = self.current.span
                self.keyword("dialogo")
                name = RuleParser(self).quoted()
                self.keyword("con")
                speaker = RuleParser(self).quoted()
                if self.current.kind != "COLON":
                    self.fail("':'")
                self.index += 1
                nodes: list[DialogueNodeDeclaration] = []
                while self.current.normalized != "fine":
                    node_start = self.current.span
                    self.keyword("nodo")
                    node_name = RuleParser(self).quoted()
                    self.keyword("dice")
                    text = RuleParser(self).quoted(name=False)
                    if self.current.kind != "COLON":
                        self.fail("':'")
                    self.index += 1
                    choices: list[DialogueChoiceDeclaration] = []
                    while self.current.normalized != "fine":
                        choice_start = self.current.span
                        self.keyword("scelta")
                        label = RuleParser(self).quoted()
                        target = None
                        if self.current.normalized == "porta":
                            self.keyword("porta")
                            self.keyword("a")
                            target = RuleParser(self).quoted()
                        elif self.current.normalized == "termina":
                            self.keyword("termina")
                        else:
                            self.fail("'porta a' o 'termina'")
                        choices.append(
                            DialogueChoiceDeclaration(label, target, self.finish(choice_start))
                        )
                    self.keyword("fine")
                    self.keyword("nodo")
                    nodes.append(
                        DialogueNodeDeclaration(
                            node_name,
                            text,
                            tuple(choices),
                            self.finish(node_start),
                        )
                    )
                self.keyword("fine")
                self.keyword("dialogo")
                dialogues.append(
                    DialogueDeclaration(name, speaker, tuple(nodes), self.finish(start))
                )
                continue
            if self.current.normalized == "tabella":
                start = self.current.span
                self.keyword("tabella")
                name = RuleParser(self).quoted()
                if self.current.kind != "COLON":
                    self.fail("':'")
                self.index += 1
                columns: list[TableColumnDeclaration] = []
                rows: list[TableRowDeclaration] = []
                while self.current.normalized != "fine":
                    item_start = self.current.span
                    if self.current.normalized == "colonna":
                        self.keyword("colonna")
                        column_name = RuleParser(self).quoted()
                        table_value_kinds: dict[str, ValueKind] = {
                            "numerica": "numero",
                            "testuale": "testo",
                            "logica": "logico",
                        }
                        adjective = self.current.normalized
                        if adjective not in table_value_kinds:
                            self.fail("numerica, testuale o logica")
                        self.index += 1
                        columns.append(
                            TableColumnDeclaration(
                                column_name,
                                table_value_kinds[adjective],
                                self.finish(item_start),
                            )
                        )
                    elif self.current.normalized == "riga":
                        self.keyword("riga")
                        values: list[Scalar] = []
                        while self.current.kind != "DOT":
                            value = self.value()
                            assert type(value) in {str, int, bool}
                            values.append(cast(Scalar, value))
                        rows.append(TableRowDeclaration(tuple(values), self.finish(item_start)))
                    else:
                        self.fail("'Colonna', 'Riga' o 'Fine tabella'")
                self.keyword("fine")
                self.keyword("tabella")
                tables.append(
                    TableDeclaration(name, tuple(columns), tuple(rows), self.finish(start))
                )
                continue
            if self.current.normalized == "azione":
                start = self.current.span
                self.keyword("azione")
                name = RuleParser(self).quoted()
                target_kind = None
                indirect_kind = None
                if self.current.normalized == "senza":
                    self.keyword("senza")
                    self.keyword("oggetti")
                    self.keyword("con")
                else:
                    self.keyword("su")
                    self.article(False)
                    target_kind = self.words(stop={"con"})
                    self.keyword("con")
                    if self.current.normalized != "comando":
                        self.article(False)
                        indirect_kind = self.words(stop={"con"})
                        self.keyword("con")
                self.keyword("comando")
                commands = [RuleParser(self).quoted()]
                separators: list[str] = []
                while self.current.normalized == "e":
                    self.keyword("e")
                    clause = self.current.normalized
                    if clause == "sinonimo":
                        self.keyword("sinonimo")
                        commands.append(RuleParser(self).quoted())
                    elif clause == "separatore":
                        self.keyword("separatore")
                        separators.append(RuleParser(self).quoted())
                    else:
                        self.fail("'sinonimo' o 'separatore'")
                actions.append(
                    ActionDeclaration(
                        name,
                        tuple(commands),
                        target_kind,
                        indirect_kind,
                        tuple(separators),
                        self.finish(start),
                    )
                )
                continue
            if self.current.kind == "WORD" and self.current.normalized in {"un", "uno", "una"}:
                start = self.current.span
                self.article(False)
                name = self.words()
                self.keyword("è")
                self.article(False)
                self.keyword("tipo")
                self.keyword("di")
                parent = self.words()
                kinds.append(KindDeclaration(name, parent, self.finish(start)))
                continue
            if self.current.normalized in {"titolo", "autore"}:
                start = self.current.span
                name = self.current.normalized
                self.keyword(name)
                if self.current.kind != "COLON":
                    self.fail("':'")
                self.index += 1
                metadata_value = RuleParser(self).quoted()
                metadata.append(Metadata(name, metadata_value, self.finish(start)))
                continue
            if self.current.normalized == "comprendi":
                start = self.current.span
                self.keyword("comprendi")
                alias = RuleParser(self).quoted()
                self.keyword("come")
                target = RuleParser(self).quoted()
                vocabulary.append(Vocabulary(alias, target, self.finish(start)))
                continue
            if self.current.normalized in {"includi", "inizia"}:
                start = self.current.span
                directive = self.current.normalized
                self.keyword(directive)
                if directive == "inizia":
                    self.keyword("nella")
                name = RuleParser(self).quoted()
                span = self.finish(start)
                if directive == "includi":
                    inclusions.append(Inclusion(name, span))
                else:
                    entries.append(EntryPoint(name, span))
                continue
            if self.current.normalized == "regola":
                rules.append(RuleParser(self).rule())
                continue
            start = self.current.span
            self.article(True)
            name = self.words()
            operator = self.current.normalized
            if operator == "ha":
                self.keyword("ha")
                prop = self.words(value_follows=True)
                assigned_value = self.value()
                assignments.append(Assignment(name, prop, assigned_value, self.finish(start)))
            elif operator in self.verbs:
                self.keyword(operator)
                self.article(True)
                target = self.words()
                relations.append(Relation(name, self.verbs[operator], target, self.finish(start)))
            elif operator == "collega":
                self.keyword("collega")
                self.article(True)
                left = self.words(stop=_TARGETS)
                self.preposition(_TARGETS)
                right = self.words()
                span = self.finish(start)
                relations.extend(
                    (
                        Relation(name, "collega da", left, span),
                        Relation(name, "collega a", right, span),
                    )
                )
            else:
                self.keyword("è")
                if self.current.normalized == "a":
                    self.keyword("a")
                    predicate = self.words()
                    self.preposition(_GENITIVES)
                    target = self.words()
                    relations.append(Relation(name, predicate, target, self.finish(start)))
                elif self.current.normalized in _LOCATIONS:
                    self.preposition(_LOCATIONS)
                    target = self.words()
                    relations.append(Relation(name, "nella", target, self.finish(start)))
                else:
                    self.article(False)
                    if self.current.normalized == "proprietà":
                        self.keyword("proprietà")
                        if self.current.normalized == "elenco":
                            self.keyword("elenco")
                            self.keyword("di")
                            list_kinds: dict[str, ValueKind] = {
                                "testi": "elenco_testi",
                                "numeri": "elenco_numeri",
                                "logici": "elenco_logici",
                            }
                            item_kind = self.current.normalized
                            if item_kind not in list_kinds:
                                self.fail("testi, numeri o logici")
                            self.index += 1
                            value_kind = list_kinds[item_kind]
                        else:
                            value_kinds: dict[str, ValueKind] = {
                                "numerica": "numero",
                                "testuale": "testo",
                                "logica": "logico",
                            }
                            adjective = self.current.normalized
                            if adjective not in value_kinds:
                                self.fail("numerica, testuale, logica o elenco")
                            self.index += 1
                            value_kind = value_kinds[adjective]
                        properties.append(PropertyDeclaration(name, value_kind, self.finish(start)))
                    else:
                        kind = self.words()
                        location = None
                        if self.current.normalized in _LOCATIONS:
                            self.preposition(_LOCATIONS)
                            location = self.words()
                        declarations.append(Declaration(name, kind, self.finish(start), location))
        return Program(
            declarations=tuple(declarations),
            kinds=tuple(kinds),
            relations=tuple(relations),
            properties=tuple(properties),
            assignments=tuple(assignments),
            rules=tuple(rules),
            inclusions=tuple(inclusions),
            entries=tuple(entries),
            metadata=tuple(metadata),
            vocabulary=tuple(vocabulary),
            actions=tuple(actions),
            tables=tuple(tables),
            dialogues=tuple(dialogues),
        )


def parse(
    text: str, source: str = "<memoria>", *, verbs: Mapping[str, str] | None = None
) -> Program:
    if verbs and any(verb in _RESERVED or not verb.isalpha() for verb in verbs):
        raise ValueError("Un verbo registrato collide con una parola riservata.")
    return _Parser(tokenize(text, source), verbs or {}).program()
