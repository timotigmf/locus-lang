# ADR 0003 — toolchain minima

Stato: accettato, 2026-09-25.

Python 3.11 come minimo, test fino a 3.14. Dataclass frozen/slots e type hints;
nessun database. La versione del linguaggio resta separata da Python.

CLI: argparse (stdlib) rispetto a Click e Typer. Click semplifica applicazioni
più articolate; Typer aggiunge inferenza dai tipi e altre dipendenze. Per quattro
comandi argparse basta; sottile adattatore per aiuto/errori italiani. Niente
parser CLI interamente proprietario: gestione opzioni e codici sarebbe duplicata.

Packaging: Hatchling con metadata PEP 621, rispetto a setuptools (più flessibile
per build complesse) e Flit (adatto a pacchetti semplici). Hatchling offre un
backend dichiarativo sufficiente per il layout src; non serve l'intero gestore
Hatch né un package manager obbligatorio. Wheel puro Python, nessuna estensione
nativa. Backend proprietario rifiutato: manutenzione degli standard senza beneficio.

pytest, Ruff (lint e formatter) e mypy strict come strumenti di sviluppo.
Intervalli di versioni limitano cambi maggiori ma non sono un lock: accettiamo
questo limite nel bootstrap e richiediamo pin verificati prima del rilascio.
La CI è un servizio facoltativo di sviluppo, non una dipendenza per giocare.

Riconsiderare CLI solo se completion/UI diventano requisiti; backend solo per
esigenze concrete di distribuzione. Non cambiano la semantica del linguaggio.
