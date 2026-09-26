# Rapporto M4 — progetti e percorso didattico

LOCUS 0.4.0a1, ramo `codex/milestone-4`, basato su M3.

## Consegnato

- Inclusioni locali risolte prima della compilazione, una sola lettura per file
  canonico, controlli su cicli, limiti e percorsi; riferimenti tra moduli.
- Punto iniziale esplicito con verifica narrativa; IR versione 5.
- Diagnostica con file e righe originali; AST espanso nei comandi CLI.
- Quattro lezioni originali in italiano, esercizi con soluzioni, quattro esempi
  completi e progetto finale su più file: il faro di Selce.
- Copione con uscita attesa verificata automaticamente, test separati dello stato.
- Registro dei sei manuali forniti, sezioni effettivamente consultate, confronto
  Inform/LOCUS e proposte future distinte dalle funzionalità disponibili.

## Verifiche locali

Python 3.14.5, macOS Apple Silicon: **280 test passati**, inclusi i 243 di M3,
nuovi casi di progetto, snippet della documentazione e transcript del tutorial.
Ruff check, formato, mypy strict e `git diff --check` passati. Sdist e wheel
costruiti senza isolamento. Wheel installata senza dipendenze in un ambiente
separato; dalla directory temporanea il progetto del faro compila e produce
un'uscita identica al file atteso, verificata con diff.

La CI contiene sette configurazioni Linux/Windows/macOS e uno smoke test dei
progetti modulari dalla wheel. Il risultato remoto va verificato sul commit
pubblicato nelle GitHub Actions, non dedotto dalle verifiche locali.

## Ambito e limiti

I moduli condividono ancora uno spazio dei nomi; non sono pacchetti versionati.
M4 non implementa tipi autore, funzioni, scenografia, luce simulata o test
in sintassi autore. Il tutorial usa soltanto funzionalità eseguibili.
Consultati indici e sezioni pertinenti dei sei PDF, non ogni pagina dei volumi.
I PDF e i relativi esempi non sono copiati nel repository.

[Specifica](linguaggio/milestone-4.md), [ADR](adr/0007-progetti.md),
[tutorial](tutorial/README.md), [materiali](architettura/materiali-didattici.md).
