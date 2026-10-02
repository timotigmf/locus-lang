# ADR 0040 — azione standard di attesa

Stato: accettato, 2026-10-02.

## Contesto

Le avventure testuali usano comunemente un comando che consuma un turno senza
modificare il mondo. Prima di questa decisione ogni storia LOCUS doveva
dichiarare una propria azione per ottenere `attendi`, e la scorciatoia classica
`z` non era disponibile.

## Decisione

La libreria narrativa definisce l'azione senza oggetti `attendere`, riconosciuta
da `attendi`, `aspetta`, `z` e `wait`. Il comportamento predefinito produce
l'evento `waited` e il testo «Il tempo passa.». L'azione attraversa il normale
rulebook, quindi una storia può aggiungere o sostituire la risposta con regole
`per attendere`.

L'attesa è un'azione valida e fa avanzare l'orologio delle scene. Le quattro
forme sono riservate e non possono essere assegnate a un'azione dell'autore.
Il formato IR 21 resta invariato perché l'azione appartiene alla stdlib.

## Alternative considerate

- Lasciare l'attesa a ogni storia: duplica una convenzione fondamentale e rende
  incompatibili i copioni che usano `z`.
- Incrementare direttamente il turno nel parser: aggirerebbe regole, rollback e
  il dispatcher comune.
- Abilitare `attendi` solo nelle storie con scene: cambierebbe il vocabolario in
  base al contenuto compilato.

## Conseguenze e verifica

Una regola può osservare o descrivere l'attesa, mentre scene e punteggio usano lo
stesso avanzamento temporale delle altre azioni. Test di parser, runtime, regole,
scene, tutorial e browser coprono forme italiane e compatibilità inglese.
