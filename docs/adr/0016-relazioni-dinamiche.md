# ADR 0016 — relazioni dinamiche transazionali

Stato: accettato, 27 settembre 2026.

## Contesto

Passaggi segreti, ponti mobili e mappe che cambiano richiedono di modificare
relazioni durante una partita. Una riscrittura testuale del sorgente violerebbe
la separazione fra parser autore e runtime e renderebbe fragile il rollback.

## Decisione

`RelationSpec` dichiara esplicitamente se una relazione è mutabile. Il lowering
risolve `crea/rimuovi relazione` in un `RelationChange` con ID di entità e
predicato. Eventuali inverse sono incluse nello stesso cambiamento. Il motore di
regole delega l'applicazione all'host e conserva il rollback dell'intera azione.

La libreria standard rende dinamiche soltanto le quattro direzioni cardinali.
La mappa dello Studio legge lo snapshot `World` corrente dopo ogni comando.
L'[ADR 0026](0026-direzioni-diagonali.md) estende in seguito lo stesso contratto
alle quattro diagonali senza cambiare la forma dell'IR.
L'[ADR 0027](0027-livelli-verticali.md) lo applica poi a `sopra` e `sotto`.

## Alternative considerate

- Riscrivere frasi LOCUS a runtime: scartato perché reintrodurrebbe parsing nel
  motore e perderebbe riferimenti già tipati.
- Rendere mutabile ogni relazione: scartato perché contenimento e struttura
  delle porte hanno invarianti differenti.
- Salvare solo la direzione richiesta e calcolare l'inversa durante il movimento:
  scartato perché produrrebbe viste del grafo incoerenti fra runtime e strumenti.

## Conseguenze

L'IR sale alla versione 12. Le mutazioni sono ispezionabili, atomiche e
indipendenti dalla sintassi italiana. Nuove relazioni dinamiche potranno essere
registrate da cataloghi futuri senza modificare il motore. Cardinalità diverse e
relazioni a senso unico richiederanno ulteriori contratti. La visibilità degli
oggetti è stata aggiunta successivamente dall'[ADR 0017](0017-visibilita-scenario.md).
