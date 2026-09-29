# Pronomi e clitici del giocatore

Dopo un'azione riuscita su un oggetto diretto, LOCUS lo conserva come referente.
Il giocatore può richiamarlo senza ripetere il nome:

```text
> esamina lanterna di vetro
lanterna di vetro
Il vetro conserva tracce di salsedine.
> prendila
Hai preso: lanterna di vetro.
> x essa
lanterna di vetro
Il vetro conserva tracce di salsedine.
```

Sono riconosciuti `esso`, `essa`, `questo`, `questa`, `quello`, `quella` e
l'inglese `it`. Possono occupare anche il secondo argomento: dopo aver esaminato
una scatola, `metti gemma in essa` usa quella scatola.

Le forme unite disponibili sono:

| Azione | Forme |
| --- | --- |
| prendere | `prendilo`, `prendila` |
| esaminare | `esaminalo`, `esaminala` |
| aprire | `aprilo`, `aprila` |
| chiudere | `chiudilo`, `chiudila` |
| lasciare | `lascialo`, `lasciala` |

Una scelta conclusa dopo «Quale intendi?» diventa il nuovo referente. `guarda`,
inventario, direzioni, errori e azioni fallite non lo cambiano. Se non esiste
ancora, LOCUS risponde «Non c'è ancora un oggetto a cui riferire il pronome».

Il modello corrente non assegna un genere grammaticale alle entità: `prendilo` e
`prendila` sono quindi equivalenti sul piano della risoluzione. Non sono ancora
supportati plurali, accordo grammaticale, clitici doppi (`metticela`) o clitici
per tutte le azioni definite dall'autore.

