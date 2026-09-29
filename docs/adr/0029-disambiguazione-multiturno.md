# ADR 0029 — chiarimenti di disambiguazione a più turni

Stato: accettato, 2026-09-29.

## Contesto

Il risolutore riconosce già nomi completi, sinonimi e nomi parziali nel campo
d'azione. Quando più entità corrispondono, ripetere l'intero comando rende però
inutile la domanda «Quale intendi?» e separa CLI, Studio e release web.

## Decisione

La sessione conserva un chiarimento immutabile: intento originale, argomento
ambiguo e identificatori delle candidate. Il parser di sessione accetta nel turno
seguente un numero, un nome completo, un nome parziale univoco o un sinonimo. Il
runtime inserisce nell'intento l'identificatore scelto e riesegue la normale
azione; il testo del giocatore non viene trasformato in codice.

Una risposta non univoca mantiene aperto il chiarimento. `annulla` lo chiude. Un
nuovo comando riconosciuto sostituisce il chiarimento e viene eseguito. Domanda,
risposta non valida e annullamento non fanno avanzare l'orologio narrativo.

## Alternative considerate

- Ripetere sempre il comando completo: semplice, ma non costituisce un dialogo.
- Conservare soltanto le etichette: fragile dopo mutazioni e incapace di
  distinguere entità omonime.
- Risolvere nel frontend: produrrebbe semantiche diverse fra CLI, Studio e release.

## Conseguenze

`Session` espone lo stato del chiarimento e `Intent` può portare identificatori
risolti internamente. Gli identificatori sono accettati soltanto se ancora
raggiungibili. Il meccanismo copre oggetto diretto e indiretto e resta separato
dal parser delle frasi dell'autore.

## Verifica

I test coprono selezione per numero, nome parziale e sinonimo, risposta invalida,
annullamento, sostituzione con un nuovo comando e secondo oggetto ambiguo.

