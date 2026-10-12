# 30. Sottintendere soltanto la destinazione

Apri `examples/tutorial/30_clitico_locativo.locus` nello Studio e premi
**Compila e prova**.

## Ricordare la cassetta

```text
> prendi gettone rosso
Hai preso: gettone rosso.
> metti gettone rosso nella cassetta
Hai messo gettone rosso dentro cassetta.
```

La riuscita del secondo comando conserva `cassetta` come ultimo secondo
oggetto.

## Nominare il nuovo oggetto

```text
> prendi gettone blu
Hai preso: gettone blu.
> mettici il gettone blu
Hai messo gettone blu dentro cassetta.
```

In `mettici`, il clitico `ci` sostituisce la destinazione; `il gettone blu`
rimane esplicito. Puoi usare anche un sinonimo dichiarato o un nome parziale
univoco.

## Prova negativa

Riavvia, prendi il gettone blu e digita `mettici il gettone blu`: non essendo
stata ancora ricordata una destinazione, LOCUS produce un messaggio specifico e
lascia il gettone nell'inventario. `mettici` da solo richiede invece il nome
dell'oggetto.

## Esercizio

Dichiara `Comprendi "disco" come "gettone blu".`. Ripeti la sequenza con
`mettici disco`, poi aggiungi una seconda cassetta per osservare quale
destinazione viene aggiornata dall'ultima azione riuscita.

## Una destinazione chiamata tasche

Copia questo esempio completo:

```locus
La Sala è una stanza.
La "tasche" è un contenitore nella Sala.
La "tasche" ha stato "aperto".
Il gettone è una cosa nella Sala.
```

Prova `prendi gettone` e `mettilo nelle tasche`. Le tasche sono una sola
entità contenitore: la preposizione plurale non crea né seleziona un gruppo.
LOCUS non controlla l’accordo grammaticale dell’articolo nella dichiarazione.
`mettici gettone nelle tasche` resta rifiutato perché specifica due destinazioni.
