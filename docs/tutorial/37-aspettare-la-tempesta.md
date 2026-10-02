# 37. Aspettare la tempesta

Apri `examples/tutorial/37_aspettare.locus` nello Studio e premi **Compila e
prova**. L'esempio collega l'azione standard di attesa a una scena temporale.

```locus
La Torre è una stanza.

Scena "il temporale" dal turno 1 al turno 2:
    Inizio "Un tuono scuote i vetri.".
    Fine "La pioggia si allontana oltre i tetti.".
    Punti 2.
Fine scena.

Regola "gocce" per attendere nella fase dopo:
    dì "Conti le gocce sul davanzale.";
Fine regola.
```

## Prova guidata

1. Scrivi `turno`: l'orologio indica zero e non avanza.
2. Scrivi `attendi`: compare il testo standard, la regola e l'inizio della scena.
3. Scrivi `z`: termina la scena e assegna due punti.
4. Scrivi `punteggio`: il totale è due e il turno resta invariato.
5. Prova anche `aspetta` e `wait`: entrambe le forme eseguono la stessa azione.

## Caso negativo

Prova a dichiarare `Azione "sostare" senza oggetti con comando "attendi".`:
la compilazione produce `E311`, perché la forma appartiene alla libreria.

## Esercizio

Aggiungi una seconda regola `invece` per attendere e osserva come sostituisce il
messaggio «Il tempo passa.». Poi falla fallire con un testo: il rollback lascia
intatto lo stato, secondo il contratto generale delle regole.

Il [riferimento sull'attesa](../linguaggio/attendere.md) descrive alias, rulebook
e avanzamento delle scene.
