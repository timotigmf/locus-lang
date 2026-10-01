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
l'inglese `it`. Possono occupare anche il secondo argomento. Se esiste un ultimo
secondo oggetto riuscito, il pronome usa quello; altrimenti ripiega sul referente
diretto. Dopo aver esaminato una scatola, `metti gemma in essa` continua quindi
a usare la scatola. La regola completa è nella specifica dei
[pronomi per ruolo](pronomi-per-ruolo.md).

Le forme unite disponibili sono:

| Azione | Forme |
| --- | --- |
| prendere | `prendilo`, `prendila` |
| esaminare | `esaminalo`, `esaminala` |
| aprire | `aprilo`, `aprila`, anche seguiti da `con CHIAVE` |
| chiudere | `chiudilo`, `chiudila` |
| lasciare | `lascialo`, `lasciala` |
| mettere | `mettilo`, `mettila`, seguiti da `in CONTENITORE` |
| bloccare | `bloccalo`, `bloccala`, seguiti da `con CHIAVE` |

Una scelta conclusa dopo «Quale intendi?» diventa il nuovo referente. `guarda`,
inventario, direzioni, errori e azioni fallite non lo cambiano. Se non esiste
ancora, LOCUS risponde «Non c'è ancora un oggetto a cui riferire il pronome».

Il modello corrente non assegna un genere grammaticale alle entità: `prendilo` e
`prendila` sono quindi equivalenti sul piano della risoluzione. Non sono ancora
supportati plurali, accordo grammaticale o clitici per tutte le azioni definite
dall'autore. I [complementi espliciti](clitici-con-complemento.md) e i
[clitici doppi locativi](clitici-doppi.md) hanno specifiche separate.
