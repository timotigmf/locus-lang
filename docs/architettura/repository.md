# Struttura completa proposta

Questa è la destinazione architetturale, non un invito a creare moduli vuoti.
`[futuro]` indica directory non ancora necessarie.

```text
README.md VISION.md ARCHITECTURE.md LANGUAGE_SPEC.md ROADMAP.md
CONTRIBUTING.md AGENTS.md pyproject.toml
.github/workflows/ci.yml
src/italica/
  __init__.py __main__.py cli.py
  diagnostics.py lexer.py parser.py ast.py compiler.py ir.py runtime.py
  stdlib/__init__.py
  frontend/                 [futuro: migrazione di lexer/parser, non duplicazione]
  semantic/                 [futuro: simboli, tipi, lowering]
  world/                    [futuro: schemi, proprietà, relazioni, invarianti]
  rules/                    [futuro: rulebook, esiti, trace]
  player/                   [futuro: lessico, intenti, disambiguazione]
  modules/                  [futuro: manifesti e risoluzione]
  tooling/                  [futuro: replay, ispezione, test script, LSP]
  backends/                 [futuro: esportazione e browser]
  stdlib/
    base/ mondo/ azioni/ parser_it/ conversazioni/ tempo/ scene/ [futuro]
tests/                      # separare in unit/integration/conformance crescendo
examples/
docs/
  adr/ linguaggio/ manuale/ reference/ architettura/ cookbook/ contributori/
```

La stdlib resta nel pacchetto per essere inclusa correttamente nei wheel;
separazione logica verificata dagli import, separazione in distribuzioni solo
quando serva versionarla indipendentemente. Non serve un monorepo di pacchetti ora.
