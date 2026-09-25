# Rapporto M3 — regole transazionali

Versione 0.3.0a1. Ramo di sviluppo `codex/milestone-3`, basato su M2.

Implementati parser e controllo statico di regole nominate, condizioni tipate,
priorità e sei fasi; esiti continua/interrompi/fallisci/sostituisci/restituisci.
Motore generico indipendente dal dominio, adattatore alle azioni narrative,
trace sorgente e CLI `debug`. IR versione 4. Esempio `examples/regole.locus`.
Nessun codice esterno incorporato; Lark usato solo come strumento opzionale di confronto.

## Verifiche locali

Python 3.14.5, macOS Apple Silicon:

- 243 test passati, inclusi i 196 precedenti e i contratti degli esempi/documenti.
- Ruff check e controllo formato passati; mypy strict passato.
- Sdist e wheel costruiti con `python -m build --no-isolation`.
- Wheel installata senza dipendenze in un ambiente temporaneo, fuori dal checkout:
  controllo sorgente e sessione completa leva/scrigno/gemma/esci riusciti con trace.
- Confronto riproducibile Lark LALR/Earley/produzione registrato in ADR 0006.
- Replay deterministico, cortocircuito, priorità, rollback di ogni fase e sostituzioni,
  ciclo e limite di azioni, host non narrativo, errori statici e CLI coperti dai test.

La CI configurata verifica Linux Python 3.11–3.14, Windows, macOS Intel e ARM;
include esecuzione dell'esempio M3 dalla wheel. L'esito remoto del commit pubblicato
va consultato nelle GitHub Actions: non viene dedotto dalle verifiche locali.

## Limiti

È un primo sistema di regole controllato, non un linguaggio equivalente a Inform.
Nessuna espressione aritmetica generale, variabile locale, funzione, modulo, nuovo verbo
nel sorgente, persistenza o debugger interattivo. Oggetti delle regole espliciti,
non parametrici. Host API puri richiesti per la garanzia di rollback.
La [specifica M3](linguaggio/milestone-3.md) descrive ordine, output e restrizioni;
[ADR 0006](adr/0006-regole.md) documenta alternative e criteri di revisione.
