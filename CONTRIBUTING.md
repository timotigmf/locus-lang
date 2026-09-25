# Contribuire

Seguire README per l'ambiente Python 3.11–3.14. Layout `src`, pytest per test,
Ruff per lint/format e mypy strict per tipi. Nessun servizio remoto nei test.

Prima di una modifica: definire comportamento, esempi e casi di errore. Ogni
feature pubblica aggiorna specifica, reference e test; ogni bug ha un test di
regressione quando riproducibile. Le decisioni strutturali richiedono un ADR.
Non usare regex per risoluzione semantica, `eval`, stato globale mutabile o I/O
nel compilatore. Type hints su funzioni e strutture, dataclass immutabili per
contratti. Tenere messaggi per l'autore in italiano.

```sh
python -m pytest
python -m ruff check .
python -m ruff format --check .
python -m mypy
python -m build
```

La CI esegue gli stessi controlli e un test dell'entry point dal wheel installato
fuori dal checkout. Un test importa e compila ogni blocco `locus` (o `ita` storico) nei Markdown:
le proposte non eseguibili usano `ita-proposta`. Non segnare come completate
funzioni soltanto progettate. Il branch principale deve rimanere verificabile.

Dipendenze di sviluppo vincolate per intervallo, non ancora lockfile: le CI non
sono byte-per-byte riproducibili. Prima del primo rilascio fissare un insieme
verificato con hash e procedura di aggiornamento. Oggi la runtime dependency list
è vuota. Hatchling è solo backend di build, non dipendenza di esecuzione.

Per installazione offline preparare sul sistema/architettura destinatario:

```sh
python -m pip download --dest wheelhouse '.[dev]'
python -m pip install --no-index --find-links wheelhouse '.[dev]'
```

Il download preliminare richiede rete. Per un utilizzatore finale basta distribuire
il wheel e Python compatibile: non occorrono gli strumenti di sviluppo.

Nessun codice esterno senza verifica di licenza e registrazione della provenienza.
La licenza del progetto resta una decisione del titolare prima della pubblicazione.
