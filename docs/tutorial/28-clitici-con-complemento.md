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
viene rifiutato senza modificare la storia. Digita `mettila nella cassa` quando
non esiste una cassa: LOCUS conserva il referente ma segnala che la destinazione
non è presente.

## Esercizio

Chiudi il cofano e usa `bloccala con chiave di bronzo`. Poi prova la chiave
sbagliata aggiungendone una seconda: il chiarimento e il controllo della chiave
continuano a funzionare anche con la forma breve.

