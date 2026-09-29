# 24. I tre livelli del faro

Apri `examples/tutorial/24_livelli_verticali.locus` nello Studio e premi
**Compila e prova**. La storia parte nella Sala Macchine, fra la Terrazza e la
Cisterna.

```locus
La Sala Macchine è una stanza.
La Terrazza è una stanza.
La Cisterna è una stanza.

La Terrazza sovrasta la Sala Macchine.
La Sala Macchine sovrasta la Cisterna.

Inizia nella "Sala Macchine".
```

## Prova guidata

1. Scrivi `su`: raggiungi la Terrazza.
2. Scrivi `giù`: torni alla Sala Macchine.
3. Scrivi `d`: scendi nella Cisterna.
4. Scrivi `u`: risali alla Sala Macchine.
5. Apri **Mappa**: i collegamenti tratteggiati mostrano `su / giù`.

Le forme senza accento `giu`, `alto`, `basso`, `up` e `down` sono equivalenti.
I messaggi e il sorgente della storia restano italiani.

## Caso negativo

Queste frasi assegnano due stanze sopra la stessa Sala e producono `E106`:

```text
La Terrazza sovrasta la Sala.
La Soffitta sovrasta la Sala.
```

LOCUS conserva una sola destinazione per direzione e stanza. Collega la Soffitta
dalla Terrazza oppure scegli un'altra relazione.

## Esercizio

Aggiungi una botola come porta fra Sala Macchine e Cisterna, inizialmente chiusa.
Verifica che `d` sia bloccato, poi apri la botola e scendi. Controlla nell'Indice
del mondo gli archi `sopra` e `sotto` e nella Mappa la singola linea verticale.

Il [riferimento dei livelli](../linguaggio/livelli-verticali.md) descrive forme,
semantica, regole dinamiche e limiti.
