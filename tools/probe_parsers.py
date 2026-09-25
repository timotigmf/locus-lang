"""Esperimento opzionale e riproducibile; nessuna dipendenza di produzione."""

import json
from pathlib import Path
from time import perf_counter

from lark import Lark, UnexpectedInput

from locus.diagnostics import CompileError
from locus.parser import parse

GRAMMAR = Path(__file__).with_name("rule_probe.lark").read_text(encoding="utf-8")
VALID = [
    'Regola "saluto" per guardare nella fase prima: dì "Ciao."; Fine regola.',
    'Regola "porta" per aprire "porta" nella fase verifica priorità 10 '
    'quando non ("attiva" di "leva" è vero o "carica" di "leva" è almeno 2): '
    'fallisci "Prima aziona la leva."; Fine regola.',
    'Regola "azione" per andare a nord nella fase invece: '
    'sostituisci con aprire "porta" con "chiave"; Fine regola.',
    'Regola "conta" per prendere "gemma" nella fase dopo: '
    'aumenta "punti" di "gemma" di 2; continua; Fine regola.',
]
INVALID = [
    VALID[0].replace('Ciao.";', 'Ciao."'),
    VALID[1].replace("almeno 2", "almeno"),
    VALID[2].replace("Fine regola.", ""),
    VALID[0].replace("fase prima", "fase ignota"),
]


def main() -> None:
    report = []
    for algorithm in ("lalr", "earley"):
        start = perf_counter()
        parser = Lark(GRAMMAR, parser=algorithm, propagate_positions=True)
        build_ms = (perf_counter() - start) * 1000
        failures = []
        for source in VALID:
            parser.parse(source)
        for source in INVALID:
            try:
                parser.parse(source)
                raise AssertionError("Sorgente negativo accettato")
            except UnexpectedInput as error:
                failures.append({"line": error.line, "column": error.column})
        start = perf_counter()
        for _ in range(100):
            for source in VALID:
                parser.parse(source)
        report.append(
            {
                "parser": algorithm,
                "valid": len(VALID),
                "invalid": len(INVALID),
                "build_ms": round(build_ms, 2),
                "400_parses_ms": round((perf_counter() - start) * 1000, 2),
                "errors": failures,
            }
        )
    failures = []
    for source in VALID:
        parse(source)
    for source in INVALID:
        try:
            parse(source)
            raise AssertionError("Sorgente negativo accettato")
        except CompileError as error:
            failures.append({"line": error.span.line, "column": error.span.column})
    start = perf_counter()
    for _ in range(100):
        for source in VALID:
            parse(source)
    report.append(
        {
            "parser": "produzione",
            "valid": len(VALID),
            "invalid": len(INVALID),
            "400_parses_ms": round((perf_counter() - start) * 1000, 2),
            "errors": failures,
        }
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
