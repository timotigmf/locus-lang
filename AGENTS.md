# Istruzioni per contribuire a LOCUS

- Leggere README.md, LANGUAGE_SPEC.md e gli ADR prima di cambiare contratti.
- Limitare lo scope alla fase richiesta; non implementare anticipatamente la roadmap.
- Compilatore indipendente da IF e stdlib; runtime indipendente dal frontend autore.
- Parser autore e giocatore separati. Semantica strutturata, niente riscritture testuali.
- Type hints completi, dati immutabili ai confini, core puro, nessun servizio cloud.
- Ogni feature: specifica, esempio, test positivo/negativo e reference.
- Diagnostica autore in italiano, codice stabile e posizione del sorgente.
- Per decisioni strutturali creare un ADR numerato con alternative e conseguenze.
- Eseguire pytest, ruff check, ruff format --check e mypy; build se cambia packaging.
- Documentare limiti e controlli effettivamente eseguiti, senza simulare feature.
- Non incorporare codice esterno senza verificare e annotare la licenza.
