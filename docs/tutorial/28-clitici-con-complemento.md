# 28. Conservare il complemento

Apri `examples/tutorial/28_clitici_con_complemento.locus` nello Studio e premi
**Compila e prova**.

## Aprire il cofano

```text
> prendi chiave
Hai preso: chiave di bronzo.
> esamina cofano
cofano
Non noti nulla di particolare.
Stato: bloccato.
> aprilo con chiave
Hai aperto: cofano.
```

`esamina cofano` rende il cofano il referente. In `aprilo con chiave`, `lo`
occupa l'oggetto diretto e `chiave` resta lo strumento esplicito.

## Mettere un oggetto

```text
> prendi gemma
Hai preso: gemma.
> mettila nel cofano
Hai messo gemma dentro cofano.
```

Anche qui il clitico indica soltanto l'oggetto diretto. Il contenitore scritto
dopo `nel` viene risolto indipendentemente.

## Prova negativa

Digita soltanto `mettila` oppure `bloccala`: manca il secondo oggetto e il comando
mostra un suggerimento sulla destinazione o sulla chiave, senza modificare la storia. Digita `mettila nella cassa` quando
non esiste una cassa: LOCUS conserva il referente ma segnala che la destinazione
non è presente.

## Esercizio

Chiudi il cofano e usa `bloccala con chiave di bronzo`. Poi prova la chiave
sbagliata aggiungendone una seconda: il chiarimento e il controllo della chiave
continuano a funzionare anche con la forma breve.


## La chiave con una preposizione articolata

Nel progetto della lezione prova `prendi chiave`, `esamina cofano`,
`aprilo colla chiave di bronzo`, `chiudi cofano`, `bloccalo colla chiave`.
La forma `con la` resta equivalente. Anche `apri cofano colla chiave` è valida.
`aprilo colla` è incompleto; due complementi con chiave sono rifiutati.

## Correggere un complemento mancante

Nell’esempio della lezione, esegui:

```text
prendi chiave
esamina cofano
aprilo con chiave
prendi gemma
mettila
mettila nel cofano
chiudi cofano
bloccalo
bloccalo con chiave
```

`mettila` indica la destinazione mancante; `bloccalo` indica la chiave
mancante. Le forme maschili e femminili funzionano allo stesso modo.
I due tentativi incompleti non consumano turni e conservano il referente:
puoi correggerli usando ancora il pronome. Devi ripetere il comando completo,
non rispondere con il solo nome del complemento.

Anche a inizio partita il comando incompleto mostra prima il suggerimento
sul complemento. Se aggiungi il complemento senza avere ancora un referente,
LOCUS segnala invece che manca un oggetto a cui riferire il pronome.

## Riporre una gemma in un cofano bloccato

Nell’esempio della lezione, riparti e scrivi `prendi gemma`, poi
`metti gemma nel cofano`. Il messaggio nomina il cofano bloccato e suggerisce
di aprirlo con una chiave adatta. La gemma resta nell’inventario.

Esegui `prendi chiave`, `apri cofano con chiave`, `chiudi cofano` e ripeti
`metti gemma nel cofano`: ora il messaggio segnala soltanto la chiusura.
Basta `apri cofano`, poi `metti gemma nel cofano` per completare il deposito.

Come prova negativa, prima del deposito usa `metti gemma nella chiave`:
LOCUS nomina la chiave come destinazione non compatibile. Non basta che
un oggetto sia raggiungibile per poterlo usare come contenitore.
