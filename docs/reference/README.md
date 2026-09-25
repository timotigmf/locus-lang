# Reference S0

## CLI

`locus COMANDO FILE` oppure `python -m locus COMANDO FILE`.
`-h`/`--help` mostra l'aiuto italiano. Gli unici comandi implementati:

| Comando | Output su stdout |
| --- | --- |
| controlla | conferma e numero di entità validate |
| ast | JSON dell'AST, senza analisi semantica |
| ir | JSON dell'IR dopo validazione |
| compila | come ir, alias esplicito in questa fase |

Output diagnostico su stderr. Codici: 0 successo, 1 sorgente/file non valido,
2 invocazione non valida. Nessuna scrittura implicita; usare redirezione per i dump.
JSON leggibile Unicode; AST e IR sono sperimentali, non formati di scambio stabili.

## API Python

- `locus.lexer.tokenize(text, source='<memoria>')`: tupla Token, incluso EOF.
- `locus.parser.parse(text, source='<memoria>')`: Program AST.
- `locus.compiler.compile_source(text, kinds, source='<memoria>')`: ProgramIR.
- `locus.compiler.analyze(program, kinds)`: validazione e lowering.
- `locus.stdlib.default_kinds()`: nuovo dizionario dei tipi base ad ogni chiamata.
- `locus.runtime.instantiate(program)`: World immutabile con entità runtime.
- `locus.diagnostics.CompileError`: attributi `code`, `message`, `span`.
- `locus.diagnostics.canonical(text)`: confronto NFC/casefold/spazi.

`kinds` mappa nomi canonici a ID non vuoti e univoci. Cataloghi invalidi sollevano
ValueError. L'IR è un contratto interno prodotto dal compilatore: instantiate
rifiuta versioni ignote e ID duplicati; non è un loader per dati non fidati.
Non costruire un loader deserializzando genericamente le dataclass.

I modelli pubblici sono le dataclass in ast.py, ir.py, runtime.py e Span/Token.
Non vi sono altre API di gioco, parsing giocatore o regole.
