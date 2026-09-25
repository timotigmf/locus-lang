# Milestone 2 — LOCUS 0.2.0a1

Sessione conclusa il 2026-09-26. Sviluppo su `codex/milestone-2`, derivato dal
milestone precedente; nessuna fusione automatica in main.

## Espansione realizzata

- Proprietà definite dall'autore: interi, testi e valori logici con default tipati.
- Stringhe, escape e nomi quotati; confronto coerente degli apostrofi italiani.
- Contenitori annidati e stati aperto/chiuso/bloccato.
- Porte bidirezionali, chiavi, controllo del possesso e accessibilità effettiva.
- Azioni esamina, apri, chiudi, blocca … con …, metti … nel … e lascia.
- Schemi di relazione con insiemi di tipi, cicli vietati e verbi registrati.
- IR versione 3; validazione narrativa separata dal compilatore generale.
- Nuova storia `examples/porte_e_contenitori.locus`, eseguibile offline.

Fonti, revisioni e licenze di Favella 1, Dialog e Inform sono registrate nel
[confronto](architettura/confronto-linguaggi.md). Sono stati esaminati estratti e
organizzazione dei progetti, non tutto il codice. Nessun codice esterno copiato.
Non si dichiara LOCUS superiore a tali sistemi: il documento definisce prove e
capacità da raggiungere progressivamente.

## Verifiche

196 test superati localmente, compresi tutti gli esempi del manuale, regressioni
M1, tipo esatto dei valori, errori sorgente, riferimenti in avanti, contenimento
ciclico/doppio, trasporto di contenitori, chiavi nascoste, porte dai due lati,
comandi a due oggetti e sessioni immutabili. Ruff lint/formatter e mypy strict
superati (26 file Python di sorgente/test).

Build wheel/sdist e prova del wheel in ambiente separato senza dipendenze runtime.
La CI GitHub include ora anche lo smoke test della storia M2 nel wheel installato;
l'esito corrente del ramo è consultabile nelle [Actions](https://github.com/timotigmf/locus-lang/actions).

## Decisioni e limiti

[ADR 0005](adr/0005-proprieta-e-mondo.md) documenta scelte e alternative.
Il sorgente autore, i comandi e i messaggi sono italiani. Gli identificatori
Python e i campi IR rimangono contratti tecnici interni. Il programma è un
linguaggio italiano controllato, non italiano libero.

Non sono ancora disponibili aritmetica, funzioni, tipi autore, ereditarietà,
regole, moduli, anafore, clitici o editor. Le proprietà numeriche sono intere,
non decimali; proprietà autore applicabili a tutte le entità. Una chiave può
abilitare un solo bersaglio M2. Le porte richiedono collegamenti direzionali già
dichiarati; prima stanza come punto iniziale ancora provvisorio. IR non persistente,
prestazioni su grandi mondi da misurare prima di introdurre indici e cache.

## Prossima fase

M3: specificare condizioni ed esiti, confrontare parser su un corpus di regole,
poi introdurre rulebook deterministici e tracing mantenendo i transcript esistenti.
