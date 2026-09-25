# Milestone 1 — 2026-09-25

Implementato LOCUS `0.1.0a2` sul ramo `codex/milestone-1`, basato sulla rinomina
preservata e sincronizzata in `rename-locus`. Il remoto GitHub è accessibile;
il precedente problema di autenticazione è risolto.

## Funzionalità

- Dichiarazioni con collocazione iniziale e collegamenti nord/sud reciproci.
- Risoluzione in due passaggi, riferimenti in avanti, errori su tipi,
  nomi non dichiarati, auto-collegamenti e uscite in conflitto.
- Schemi di relazione esterni al compilatore, verificati anche con un dominio non-IF.
- AST strutturato, IR versione 2, mondo e sessioni immutabili.
- Parser giocatore separato: guarda, prendi, inventario, nord, sud, esci.
- Transizioni pure con eventi e renderer italiano separato.
- CLI `locus gioca`, esempio `examples/prima_storia.locus` e transcript di soluzione.

## Verifiche locali

136 test superati, Ruff lint/format, mypy strict su 21 file Python, build di
wheel e sdist. Wheel installato con `--no-index --no-deps` in una venv separata;
transcript CLI eseguito da `/tmp`, fuori dal checkout, con presa/inventario/
movimento/uscita. Nessuna dipendenza runtime o servizio remoto per giocare.

La CI del commit di rinomina `a87033f` è passata su GitHub. La CI di M1 viene
attivata dal push del ramo; lo stato aggiornato è consultabile nelle
[Actions del repository](https://github.com/timotigmf/locus-lang/actions).
`main` non viene aggiornato automaticamente: il lavoro è disponibile nel ramo
[Milestone 1](https://github.com/timotigmf/locus-lang/tree/codex/milestone-1).

## Limiti espliciti

Prima stanza dichiarata come inizio provvisorio; nomi esatti e parole riservate;
nessuna porta, contenitore, proprietà o regola avanzata. Oggetti senza collocazione
non raggiungibili. IR interna non caricabile da JSON e senza compatibilità v1.
La sessione mantiene le posizioni iniziali nel mondo e il possesso nello stato
separato; M2 richiederà un modello di posizione più generale.

Specifica e API aggiornate; decisioni nell'[ADR 0004](adr/0004-milestone-1.md).
Prossimo sviluppo: M2, a partire da proprietà tipate e vincoli di contenimento.
