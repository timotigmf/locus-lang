# ADR 0031 — clitici con complemento esplicito

Stato: accettato, 2026-10-01.

## Contesto

Il referente di sessione permette `prendila`, ma un'azione a due oggetti richiede
anche una destinazione o uno strumento. Costringere il giocatore a tornare alla
forma completa in `metti gemma nella scatola` o `apri cofano con chiave` spezza
la composizione già disponibile nel parser.

## Decisione

Il parser riconosce il clitico unito come verbo più oggetto diretto pronominale e
continua ad analizzare il complemento con i separatori standard. Sono ammesse:

- `mettilo`/`mettila` seguito da `in`, `nel`, `nella`, `nello` o `nell'`;
- `aprilo`/`aprila` seguito facoltativamente da `con` una chiave;
- `bloccalo`/`bloccala` seguito obbligatoriamente da `con` una chiave.

L'intento conserva due ruoli separati: l'ID del referente occupa l'oggetto
diretto, mentre il complemento viene risolto normalmente nel campo d'azione.
Non si riscrive testo a runtime e le regole ricevono gli stessi riferimenti della
forma estesa.

## Alternative considerate

- Espandere la stringa in un comando italiano prima del parser: fragile con
  virgolette e separatori articolati.
- Introdurre subito `metticela`: richiede due memorie referenziali e una decisione
  separata sul clitico locativo `ci`.
- Elencare ogni frase completa: moltiplica le forme senza comporre i ruoli.

## Conseguenze e verifica

Le nuove forme sono comandi riservati e non possono essere ridefinite da
un'azione dell'autore. Senza complemento, `mettila` e `bloccala` sono rifiutati.
Test parser, runtime, CLI, Studio e browser coprono contenitore, porta e chiave.

