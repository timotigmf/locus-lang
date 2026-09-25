# LOCUS — laboratorio LOCUS

Linguaggio naturale controllato italiano per narrativa interattiva e simulazioni.
Nome **LOCUS provvisorio**; il repository locale si chiama LOCUS.

## Stato reale

Prima sessione, versione `0.1.0a1`: skeleton architetturale, **non ancora giocabile**.
Funzionano dichiarazioni di entità, tokenizzazione con posizioni, AST immutabile,
risoluzione dei tipi forniti dall'esterno, IR, costruzione di un mondo iniziale e CLI.
Nessuna dipendenza runtime esterna, rete, modello linguistico o database.

```ita
La Cucina è una stanza.
Il Corridoio è una stanza.
La chiave di ottone è una cosa.
```

## Avvio

Python 3.11–3.14. Dalla radice:

```sh
python -m venv .venv
# macOS/Linux:
. .venv/bin/activate
# Windows PowerShell, in alternativa: .venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
locus controlla examples/dichiarazioni.locus
locus ast examples/dichiarazioni.locus
locus ir examples/dichiarazioni.locus
locus compila examples/dichiarazioni.locus > programma.json
python -m pytest
python -m ruff check .
python -m ruff format --check .
python -m mypy
```

`python -m locus` equivale a `locus`. Il JSON è un dump sperimentale,
non un formato caricabile o un eseguibile. Non esistono ancora `gioca` e `studio`.
Per usare il sorgente senza installazione: `PYTHONPATH=src python -m locus`
(sintassi della variabile da adattare su Windows).

Compilazione e modello del mondo funzionano offline. L'installazione degli
strumenti richiede pacchetti già presenti oppure rete; per ambienti isolati
preparare una wheelhouse come descritto in CONTRIBUTING.md.

## Documentazione

- [Visione](VISION.md), [architettura](ARCHITECTURE.md), [specifica](LANGUAGE_SPEC.md).
- [Roadmap](ROADMAP.md), [contribuire](CONTRIBUTING.md), [indice documentazione](docs/README.md).
- [Decisioni architetturali](docs/adr/README.md), [rapporto prima sessione](docs/rapporto-sessione-01.md).

La CI configura Windows, Linux, macOS Intel e Apple Silicon. Una configurazione
non equivale a una certificazione: vedere il rapporto per le verifiche eseguite.
Licenza del progetto da scegliere prima della distribuzione pubblica; nessun
codice di Inform o dei parser confrontati è stato incorporato.

## Repository GitHub

Destinazione indicata: [timotigmf/locus-lang](https://github.com/timotigmf/locus-lang).
Il remote locale `origin` è configurato. In questa sessione l'accesso Git HTTPS
non trova credenziali utilizzabili: contenuto remoto e CI non sono stati verificati.
