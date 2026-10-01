# ADR 0033 — clitico locativo con oggetto esplicito

Stato: accettato, 2026-10-01.

## Contesto

Il secondo referente introdotto per `metticelo` e `metticela` permette anche una
forma italiana complementare: `mettici la moneta`, dove l'oggetto resta
esplicito e soltanto la destinazione è sottintesa. Trattare l'intera parola come
sinonimo testuale di `metti` perderebbe il ruolo locativo di `ci`.

## Decisione

Il parser del giocatore riserva `mettici` e produce direttamente un intento
`put` con il nome esplicito nel ruolo diretto e il marcatore `ci` nel ruolo
indiretto. Il parser di sessione risolve quest'ultimo tramite
`indirect_pronoun_id`. Articoli e nomi continuano a seguire la pipeline nominale
esistente; non viene riscritta alcuna frase.

La forma priva di oggetto produce `missing_noun`. Una forma che aggiunge anche
`in` o una preposizione articolata viene rifiutata come doppia destinazione.

## Alternative considerate

- Interpretare `ci` come sinonimo nominale globale: entrerebbe in conflitto con
  il vocabolario delle storie e non conserverebbe un'identità.
- Accettare qualsiasi suffisso `-ci` per ogni verbo: richiede una grammatica dei
  clitici e significati verbali che questo incremento non definisce.
- Espandere la stringa in `metti ... nella ...`: duplicazione fragile della
  risoluzione già tipata nella sessione.

## Conseguenze e verifica

`mettici` è un comando standard riservato e usa gli stessi controlli e le stesse
regole di `metti`. Test parser, runtime, CLI, Studio, tutorial e browser coprono
oggetto esplicito, destinazione ricordata, destinazione assente e sintassi
contraddittoria. L'IR resta alla versione 21.
