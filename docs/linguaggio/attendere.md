# Attendere e far trascorrere un turno

Stato: implementato nella stdlib di LOCUS 0.5.0a1, senza modifica dell'IR 21.

Il giocatore può far trascorrere un turno senza agire sul mondo:

```text
attendi
aspetta
z
wait
```

Tutte le forme producono l'azione standard `attendere`. Senza regole aggiunte la
risposta è «Il tempo passa.». `z` conserva la convenzione delle avventure
testuali classiche; messaggi, regole e documentazione restano in italiano.

## Regole

L'azione attraversa le stesse fasi delle altre azioni della libreria:

```locus
Regola "ascoltare la pioggia" per attendere nella fase dopo:
    dì "La pioggia tamburella sulle tegole.";
Fine regola.
```

Non serve dichiarare `Azione "attendere"`: il nome e i comandi sono già
riservati dalla stdlib. Una regola nella fase `invece` può sostituire il testo
predefinito; `prima`, `dopo` e `descrivi` possono affiancarlo secondo il normale
ordine del rulebook.

## Tempo e scene

L'attesa è un'azione riconosciuta e consuma un turno quando la storia usa
scene. Può quindi iniziare o terminare una scena e assegnarne il punteggio. Un
comando sconosciuto o una forma incompleta continua a non far avanzare il tempo.

## Limiti

LOCUS usa un orologio discreto a turni: `attendi` avanza di un solo turno. Non
esistono ancora durate come «aspetta cinque minuti» o eventi ricorrenti; questi
richiederanno un contratto temporale distinto.
