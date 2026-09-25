# LOCUS — laboratorio LOCUS

Linguaggio naturale controllato italiano per narrativa interattiva e simulazioni.
Nome **LOCUS provvisorio**; il repository locale si chiama LOCUS.

## Stato reale

Versione `0.3.0a1`: **regole tipate, priorità e azioni transazionali**.
Proprietà numeriche/testuali/logiche definite dall’autore, contenimento annidato,
accessibilità verificata e azioni con due oggetti. Nessuna dipendenza runtime esterna o servizio cloud.

```locus
La Cucina è una stanza.
Il Corridoio è una stanza.
Il Corridoio è a nord della Cucina.
La chiave è una cosa nella Cucina.
```

## Avvio

Python 3.11–3.14. Dalla radice:

```sh
python -m venv .venv
# macOS/Linux:
. .venv/bin/activate
# Windows PowerShell, in alternativa: .venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
locus gioca examples/regole.locus
locus debug examples/regole.locus
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
non un formato caricabile o un eseguibile. Sono disponibili condizioni booleane e regole;
non ancora espressioni aritmetiche generali, ereditarietà e `studio`.
Per usare il sorgente senza installazione: `PYTHONPATH=src python -m locus`
(sintassi della variabile da adattare su Windows).

Compilazione e modello del mondo funzionano offline. L'installazione degli
strumenti richiede pacchetti già presenti oppure rete; per ambienti isolati
preparare una wheelhouse come descritto in CONTRIBUTING.md.

## Documentazione

- [Visione](VISION.md), [architettura](ARCHITECTURE.md), [specifica](LANGUAGE_SPEC.md).
- [Roadmap](ROADMAP.md), [contribuire](CONTRIBUTING.md), [indice documentazione](docs/README.md).
- [Rapporto M1](docs/rapporto-milestone-1.md).
- [Decisioni architetturali](docs/adr/README.md), [rapporto prima sessione](docs/rapporto-sessione-01.md).

La CI configura Windows, Linux, macOS Intel e Apple Silicon. Una configurazione
non equivale a una certificazione: vedere il rapporto per le verifiche eseguite.
Licenza del progetto da scegliere prima della distribuzione pubblica; nessun
codice di Inform o dei parser confrontati è stato incorporato.

## Repository GitHub

Destinazione indicata: [timotigmf/locus-lang](https://github.com/timotigmf/locus-lang).
Il remote locale `origin` è configurato e l'accesso Git è stato verificato.
La rinomina è sul ramo `rename-locus`; M1 è su `codex/milestone-1`, M2 su `codex/milestone-2`.
Il ramo `main` viene mantenuto separato fino all'integrazione delle modifiche.

## Giocare

Dopo l'avvio: `guarda`, `prendi la chiave`, `inventario`, `nord`, `sud`, `esci`.
La prima stanza dichiarata è il punto iniziale provvisorio. EOF termina la sessione;
Ctrl-C la interrompe. Vedi il [manuale](docs/manuale/README.md) per un transcript.

## Espansione M2

[Specifica ed esempi](docs/linguaggio/milestone-2.md),
[rapporto M2](docs/rapporto-milestone-2.md),
[confronto con Favella, Dialog e Inform](docs/architettura/confronto-linguaggi.md).
Per la nuova storia: `apri scrigno`, `prendi chiave di ottone`,
`apri porta rossa con chiave di ottone`, `nord`. Anche `esamina`, `chiudi`,
`metti`, `lascia` e `blocca … con …` sono disponibili.

Le [regole M3](docs/linguaggio/milestone-3.md) includono prima/invece/verifica/esegui/dopo/descrivi,
sostituzioni limitate, risultati tipati e ripristino completo in caso di fallimento.
