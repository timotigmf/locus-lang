# Ripetere l'ultimo comando

Stato: implementato nella stdlib di LOCUS 0.5.0a1, senza modifica dell'IR 21.

Queste forme sono equivalenti:

```text
ancora
ripeti
again
g
```

LOCUS ripete l'ultimo comando concluso con successo. La ripetizione attraversa
nuovamente regole, controlli e transazioni: `attendi` seguito da `g` fa passare
un altro turno; `suona campana` seguito da `ancora` esegue di nuovo l'azione
dell'autore.

Il runtime conserva un intento strutturato, non il testo. Se `esamina chiave`
ha richiesto di scegliere tra due oggetti, dopo la risposta `2` il comando `g`
esamina proprio l'oggetto selezionato senza aprire una nuova ambiguità.

## Cosa non sostituisce il ricordo

Un comando sconosciuto, un'azione fallita e i metacomandi `aiuto`, `turno`,
`punteggio` e `denaro` lasciano intatto l'ultimo intento riuscito. Anche la
descrizione mostrata automaticamente all'avvio non conta come comando del
giocatore.

Prima di qualsiasi successo, `g` risponde «Non c'è ancora un comando riuscito
da ripetere» senza consumare un turno. Durante una domanda di chiarimento,
`ripeti` ripropone la stessa domanda e conserva le alternative.

## Limiti

Le scelte e i comandi di dialogo non vengono memorizzati per la ripetizione.
La sessione conserva un solo intento. Non sono ancora disponibili una cronologia
navigabile, macro o ripetizioni numeriche come `ripeti 3 volte`.
