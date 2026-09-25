"""Rulebook deterministici e transazionali; nessuna dipendenza da IF o sorgente."""

from dataclasses import dataclass, field
from typing import Generic, Literal, Protocol, TypeVar

from locus.rule_model import ActionCall, Address, Condition, Phase, RuleIR, Trace
from locus.schema import Value

S = TypeVar("S")
E = TypeVar("E")
Outcome = Literal["riuscita", "interrotta", "fallita", "risultato"]


class RuleError(Exception):
    """Errore previsto di esecuzione, con rollback della transazione."""


@dataclass(frozen=True, slots=True)
class ActionResult(Generic[S, E]):
    state: S
    success: bool
    outputs: tuple[E | str, ...] = ()


class Host(Protocol[S, E]):
    def read(self, state: S, address: Address) -> Value: ...
    def write(self, state: S, address: Address, value: Value) -> S: ...
    def perform(self, state: S, action: ActionCall) -> ActionResult[S, E]: ...


@dataclass(frozen=True, slots=True)
class Execution(Generic[S, E]):
    state: S
    outcome: Outcome
    outputs: tuple[E | str, ...]
    trace: tuple[Trace, ...]
    value: Value | None = None


@dataclass(frozen=True, slots=True)
class _Control:
    kind: str = "completata"
    value: Value | None = None
    replacement: ActionCall | None = None


def evaluate(condition: Condition[Address], read: "Reader") -> bool:
    op = condition.operator
    if op in {"vero", "falso"}:
        return op == "vero"
    if op == "e":
        return all(evaluate(child, read) for child in condition.operands)
    if op == "o":
        return any(evaluate(child, read) for child in condition.operands)
    if op == "non":
        return not evaluate(condition.operands[0], read)
    if condition.reference is None:
        raise RuleError("Confronto senza riferimento di proprietà.")
    left, right = read(condition.reference), condition.value
    if type(left) is not type(right):
        raise RuleError("Il valore runtime non rispetta il tipo del confronto.")
    if op == "uguale":
        return left == right
    if op == "diverso":
        return left != right
    if type(left) is not int or type(right) is not int:
        raise RuleError("Il confronto ordinato richiede interi.")
    return {
        "maggiore": left > right,
        "minore": left < right,
        "almeno": left >= right,
        "massimo": left <= right,
    }[op]


class Reader(Protocol):
    def __call__(self, address: Address) -> Value: ...


@dataclass
class _Run(Generic[S, E]):
    state: S
    host: Host[S, E]
    rules: tuple[RuleIR, ...]
    action: ActionCall
    outputs: list[E | str] = field(default_factory=list)
    trace: list[Trace] = field(default_factory=list)

    def book(self, phase: Phase) -> _Control:
        candidates = sorted(
            (
                rule
                for rule in self.rules
                if rule.phase == phase
                and rule.selector.action_id == self.action.action_id
                and rule.selector.target_id in (None, self.action.target_id)
                and rule.selector.indirect_id in (None, self.action.indirect_id)
            ),
            key=lambda rule: (-rule.priority, rule.order),
        )
        for rule in candidates:
            matched = False
            try:
                matched = evaluate(
                    rule.condition, lambda address: self.host.read(self.state, address)
                )
                if not matched:
                    self.trace.append(
                        Trace(
                            rule.id,
                            rule.name,
                            phase,
                            rule.priority,
                            False,
                            "condizione falsa",
                            rule.origin,
                        )
                    )
                    continue
                control = _Control()
                for effect in rule.effects:
                    if effect.kind == "dì":
                        assert isinstance(effect.value, str)
                        self.outputs.append(effect.value)
                    elif effect.kind in {"imposta", "aumenta"}:
                        assert effect.address is not None and effect.value is not None
                        value = effect.value
                        if effect.kind == "aumenta":
                            old = self.host.read(self.state, effect.address)
                            if type(old) is not int or type(value) is not int:
                                raise RuleError("Aumento di un valore non numerico.")
                            value = old + value
                        self.state = self.host.write(self.state, effect.address, value)
                    else:
                        control = _Control(effect.kind, effect.value, effect.action)
                        break
                self.trace.append(
                    Trace(rule.id, rule.name, phase, rule.priority, True, control.kind, rule.origin)
                )
                if control.kind == "continua":
                    continue
                if control.kind != "completata":
                    return control
                if phase in {"invece", "descrivi"}:
                    return _Control("gestita")
            except RuleError:
                self.trace.append(
                    Trace(
                        rule.id,
                        rule.name,
                        phase,
                        rule.priority,
                        matched,
                        "errore con ripristino",
                        rule.origin,
                    )
                )
                raise
        return _Control()


def execute(
    state: S,
    action: ActionCall,
    rules: tuple[RuleIR, ...],
    host: Host[S, E],
    *,
    max_actions: int = 8,
) -> Execution[S, E]:
    """Una transazione include tutte le sostituzioni e le fasi dell'azione."""
    if max_actions < 1:
        raise ValueError("Il limite di azioni deve essere positivo.")
    trace: list[Trace] = []

    def run(current: S, call: ActionCall, chain: tuple[ActionCall, ...]) -> Execution[S, E]:
        if call in chain or len(chain) >= max_actions:
            return Execution(
                state,
                "fallita",
                ("Sostituzione ciclica o limite di azioni superato.",),
                tuple(trace),
            )
        work = _Run(current, host, rules, call, trace=trace)

        def terminal(control: _Control) -> Execution[S, E] | None:
            if control.kind == "interrompi":
                return Execution(work.state, "interrotta", tuple(work.outputs), tuple(trace))
            if control.kind == "fallisci":
                return Execution(state, "fallita", (str(control.value),), tuple(trace))
            if control.kind == "restituisci":
                return Execution(
                    work.state, "risultato", tuple(work.outputs), tuple(trace), control.value
                )
            if control.kind == "sostituisci":
                assert control.replacement is not None
                replacement = run(work.state, control.replacement, (*chain, call))
                if replacement.outcome == "fallita":
                    return replacement
                return Execution(
                    replacement.state,
                    replacement.outcome,
                    (*work.outputs, *replacement.outputs),
                    replacement.trace,
                    replacement.value,
                )
            return None

        try:
            result = terminal(work.book("prima"))
            if result is not None:
                return result
            instead = work.book("invece")
            result = terminal(instead)
            if result is not None:
                return result
            if instead.kind != "gestita":
                for phase in ("verifica", "esegui"):
                    result = terminal(work.book(phase))
                    if result is not None:
                        return result
                performed = host.perform(work.state, call)
                if not performed.success:
                    return Execution(state, "fallita", performed.outputs, tuple(trace))
                work.state = performed.state
                narration = performed.outputs
            else:
                narration = ()
            before = tuple(work.outputs)
            work.outputs.clear()
            after = work.book("dopo")
            result = terminal(after)
            if result is not None:
                if result.outcome == "fallita":
                    return result
                return Execution(
                    result.state,
                    result.outcome,
                    (*before, *narration, *result.outputs),
                    result.trace,
                    result.value,
                )
            description = work.book("descrivi")
            result = terminal(description)
            if result is not None:
                if result.outcome == "fallita":
                    return result
                return Execution(
                    result.state,
                    result.outcome,
                    (*before, *narration, *result.outputs),
                    result.trace,
                    result.value,
                )
            outputs = (
                *before,
                *(narration if description.kind != "gestita" else ()),
                *work.outputs,
            )
            return Execution(work.state, "riuscita", outputs, tuple(trace))
        except RuleError as error:
            return Execution(state, "fallita", (str(error),), tuple(trace))

    return run(state, action, ())
