# 36. Tornare sui propri passi

Apri `examples/tutorial/36_tornare_indietro.locus` nello Studio e premi
**Compila e prova**. Il percorso comprende un corridoio normale e una caduta
senza ritorno.

```locus
La Banchina è una stanza.
La Lanterna è una stanza.
La Cripta è una stanza.

La Lanterna è a nord della Banchina.
Dalla Lanterna si va giù verso la Cripta.
```

## Prova guidata

1. Scrivi `indietro`: non esiste ancora un luogo precedente.
2. Scrivi `nord`, poi `torna indietro`: ritorni alla Banchina.
3. Scrivi ancora `back`: torni alla Lanterna.
4. Scrivi `giù`: cadi nella Cripta.
5. Scrivi `indietro`: LOCUS non inventa una salita che la mappa non contiene.

Il luogo precedente viene registrato solo quando il movimento riesce. Un
comando incomprensibile, una direzione senza uscita o una porta chiusa non
cancellano il ricordo.

## Caso negativo

Dalla Cripta il comando `indietro` produce «Non puoi tornare indietro da qui».
La posizione resta invariata e un eventuale veicolo guidato non viene separato
dal conducente.

## Esercizio

Sostituisci la caduta con un collegamento verticale normale usando `sovrasta`.
Verifica che `indietro` torni alla Lanterna e che una seconda esecuzione riporti
alla Cripta.

Il [riferimento sul ritorno](../linguaggio/ritorno-indietro.md) descrive memoria,
porte, veicoli e passaggi a senso unico.
