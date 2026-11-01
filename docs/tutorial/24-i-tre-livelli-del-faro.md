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

## Esercizio risolto: la botola della cisterna

Apri `examples/tutorial/24b_botola_cisterna.locus` oppure copia:

```locus
Titolo: "La botola della cisterna".
Autore: "Esempio LOCUS".

La Sala Macchine è una stanza.
La Terrazza è una stanza.
La Cisterna è una stanza.
La Terrazza sovrasta la Sala Macchine.
La Sala Macchine sovrasta la Cisterna.
Inizia nella Sala Macchine.
La botola è una porta.
La botola collega la Sala Macchine alla Cisterna.
La botola ha stato "chiuso".
La Sala Macchine ha descrizione "Una scala sale alla terrazza; una botola protegge la discesa.".
La Cisterna ha descrizione "La botola conduce alla sala macchine sopra di te.".
```

1. `d`: la botola chiusa impedisce di scendere.
2. `u`, `d`: puoi comunque salire sulla Terrazza e tornare.
3. `apri botola`, `d`: raggiungi la Cisterna.
4. `chiudi botola`, `u`: ora la botola impedisce la risalita.
5. `apri botola`, `u`: torni alla Sala Macchine.
6. `d`, `d`: la prima discesa riesce; la seconda non trova un livello inferiore.

La botola controlla soltanto il collegamento Sala Macchine–Cisterna.
Non chiude anche la scala verso la Terrazza. I due versi usano lo stesso
stato della porta e lo stesso oggetto, senza duplicarlo.

Nella Mappa ci sono tre stanze e due collegamenti verticali, non quattro:
ciascuna coppia su/giù viene rappresentata una sola volta. Chiudere la botola
non rimuove il collegamento dalla topologia; impedisce di percorrerlo finché
non viene riaperta. Le descrizioni dell’esempio evitano di chiamarla
«aperta» quando lo stato può cambiare.
