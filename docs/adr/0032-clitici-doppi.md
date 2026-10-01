# ADR 0032 — clitici doppi e secondo referente

Stato: accettato, 2026-10-01.

## Contesto

`mettila nella scatola` evita di ripetere l'oggetto diretto, ma la forma italiana
`metticela` richiede due riferimenti indipendenti: `la` indica la cosa e `ci` la
destinazione. Un solo `pronoun_id` non può rappresentarli senza perdere identità
o scegliere il referente in modo implicito.

## Decisione

La sessione aggiunge `indirect_pronoun_id`, aggiornato con il secondo oggetto di
ogni azione riuscita a due argomenti. Le azioni successive con un solo oggetto
aggiornano `pronoun_id` e conservano il referente indiretto. Il parser traduce
strutturalmente `metticelo` e `metticela` in un intento `put` con i marcatori
pronominali diretto e locativo; il parser di sessione li risolve nei due ID.

L'assenza del secondo referente produce l'evento dedicato
`no_indirect_referent`, non consuma un turno e non modifica la sessione. Entrambi
i referenti sono esposti dall'adattatore dello Studio.

## Alternative considerate

- Usare sempre l'ultimo oggetto menzionato: `guarda` e gli elenchi della stanza
  renderebbero il risultato imprevedibile.
- Spostare il vecchio referente diretto in una pila: confonderebbe un oggetto
  precedente con una destinazione grammaticalmente richiesta.
- Riscrivere `metticela` come testo prima del parser: perderebbe la separazione
  dei ruoli e duplicerebbe la risoluzione dei nomi.

## Conseguenze e verifica

Le due forme diventano comandi standard riservati. La destinazione ricordata
attraversa gli stessi controlli di accessibilità, tipo e stato del comando
esteso. Test parser, runtime, CLI, Studio, tutorial e browser coprono il caso
riuscito e l'assenza distinta dei due referenti. L'IR resta alla versione 21
perché il nuovo stato appartiene alla sessione, non al programma compilato.
