# Rapporto prima sessione — 2026-09-25

## Risultato

Bootstrap `0.1.0a1` completo: architettura, specifica, ADR, progetto Python,
CLI e skeleton verificato. Il primo milestone giocabile non è ancora implementato,
come richiesto per questa sessione. Nome linguaggio/CLI Italica provvisorio;
repository GitHub indicata dall'autore: https://github.com/timotigmf/locus-lang.

La pipeline esegue lexer → parser → AST → analisi/lowering → IR → mondo iniziale.
CLI: controlla, ast, ir, compila. Tipi narrativi forniti dalla stdlib separata;
test con dispositivo non-IF dimostra che il compilatore non li incorpora.

## Decisioni

- Parser originale predittivo per una sola produzione; confronto Lark/ANTLR/
  pyparsing/PEG documentato. Revisione del parser prima di regole ed espressioni.
- AST e IR distinti, immutabili; catalogo tipi esplicito. IR interna versione 1,
  JSON solo per ispezione, nessuna compatibilità persistente promessa.
- Python >=3.11, argparse, Hatchling, pytest, Ruff e mypy strict.
- Zero dipendenze runtime esterne; nessun database, NLP o servizio cloud.
- S0 limitato alle dichiarazioni; S1 proposto per collocazione e direzioni.
- Nomi canonici NFC/casefold, duplicati rifiutati; accordi morfologici rinviati.

Motivazioni, alternative e criteri di revisione: [ADR](adr/README.md).
Fonti primarie e licenze dei parser: [registro](architettura/fonti.md).

## Verifiche effettuate

Ambiente locale: macOS Apple Silicon (arm64), Python 3.14.5.

- **83 test superati**, inclusi esempi documentati, casi negativi, Unicode,
  regressione offset CRLF nella CLI, pipeline, isolamento runtime e import.
- Ruff lint e controllo formattazione superati.
- mypy strict: nessun problema nei 15 file Python di sorgente/test.
- Wheel e sdist generati; wheel installato offline con `--no-deps` in una venv
  separata, CLI e dump IR eseguiti da `/tmp`, fuori dal repository.
- Primo tentativo di installazione ostacolato dalla rete ristretta; ripetizione
  con accesso autorizzato riuscita. Nessuna dipendenza scaricata per compilare.

Il numero finale esclude i documenti senza esempi: ogni blocco `ita` è un caso
parametrico; non si conteggiano come test documentali Markdown privi di codice.

CI configurata per Linux/Python 3.11–3.14, Windows, macOS Intel e ARM64.
Non eseguita su GitHub in questa sessione: non si dichiara la matrice già verde.

## GitHub

`origin` configurato su `https://github.com/timotigmf/locus-lang.git`.
La lettura `git ls-remote` fallisce perché Git HTTPS non può ottenere credenziali
in questo ambiente (`could not read Username`). Non è una prova che il repository
sia assente: potrebbe essere privato. Contenuto remoto non verificato, nessun
push effettuato. Checkout iniziale vuoto, branch locale `master`, nessun commit.
Prima di sincronizzare: autenticare Git, leggere HEAD remoto e integrare eventuali
file esistenti senza sovrascriverli o creare storie divergenti per errore.

## Problemi aperti e rischi

1. Identità persistenti e scope dei nomi: ID ordinali non adatti a save/restore.
2. Grammatica estensibile e nomi composti: delimitatori e parole riservate possono
   confliggere; servono corpus e policy di ambiguità prima di ampliare la sintassi.
3. Regole: ordine, effetti, rollback e sostituzioni hanno conseguenze globali;
   l'architettura propone una direzione ma richiede un ADR prima di M3.
4. IR, plugin e browser: contratti non stabili; il runtime Python non garantisce
   automaticamente un backend web efficiente o una sandbox per codice nativo.
5. Licenza del progetto e nome definitivo da decidere; dipendenze di sviluppo
   per intervalli, senza lockfile. Prestazioni non ancora misurate.
6. Diagnostica interrompe al primo errore; editor richiederà recupero e più errori.
7. Accesso remoto Git non autenticato; verifica CI multipiattaforma ancora pendente.

## Prossimi cinque task consigliati

1. Precisare AST/IR per relazioni S1 e risolvere conflitti fra nomi e delimitatori.
2. Aggiungere semantica in due passaggi con riferimenti in avanti e diagnosi.
3. Implementare containment e collegamenti con vincoli e inversi nella stdlib.
4. Aggiungere parser giocatore separato e transizioni M1 con transcript di test.
5. Completare `gioca`, esempi di soluzione e verifiche dei pacchetti in CI.

## File creati

- `.github/workflows/ci.yml`
- `.gitignore`
- `AGENTS.md`
- `ARCHITECTURE.md`
- `CONTRIBUTING.md`
- `LANGUAGE_SPEC.md`
- `README.md`
- `ROADMAP.md`
- `VISION.md`
- `docs/README.md`
- `docs/adr/0001-parser.md`
- `docs/adr/0002-ir.md`
- `docs/adr/0003-toolchain.md`
- `docs/adr/README.md`
- `docs/architettura/fonti.md`
- `docs/architettura/repository.md`
- `docs/contributori/README.md`
- `docs/cookbook/README.md`
- `docs/linguaggio/README.md`
- `docs/manuale/README.md`
- `docs/rapporto-sessione-01.md`
- `docs/reference/README.md`
- `examples/dichiarazioni.ita`
- `pyproject.toml`
- `src/italica/__init__.py`
- `src/italica/__main__.py`
- `src/italica/ast.py`
- `src/italica/cli.py`
- `src/italica/compiler.py`
- `src/italica/diagnostics.py`
- `src/italica/ir.py`
- `src/italica/lexer.py`
- `src/italica/parser.py`
- `src/italica/py.typed`
- `src/italica/runtime.py`
- `src/italica/stdlib/__init__.py`
- `tests/test_cli.py`
- `tests/test_contracts.py`
- `tests/test_frontend.py`
- `tests/test_pipeline.py`

Ambiente `.venv/`, cache e artefatti `dist/` sono locali e ignorati da Git.
