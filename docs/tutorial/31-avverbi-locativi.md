# 31. Dire «mettilo lì»

Apri `examples/tutorial/31_avverbi_locativi.locus` nello Studio e premi
**Compila e prova**.

## Stabilire il luogo

```text
> prendi bussola
Hai preso: bussola.
> metti bussola nel baule
Hai messo bussola dentro baule.
```

Il baule diventa il referente locativo perché è il secondo oggetto dell'ultima
azione riuscita.

## Usare lì o là

```text
> prendi sestante
Hai preso: sestante.
> metti il sestante lì
Hai messo sestante dentro baule.
```

Puoi sostituire `lì` con `là`: entrambe le parole indicano la destinazione
ricordata. L'oggetto resta esplicito e può essere un nome parziale univoco.

## Prova negativa

Riavvia, prendi il sestante e digita `metti sestante là`. LOCUS segnala che non
esiste ancora una destinazione ricordata e conserva il sestante nell'inventario.
`metti sestante lì nel baule` viene invece rifiutato perché specifica due volte
la destinazione.

## Esercizio

Aggiungi un secondo contenitore aperto. Colloca esplicitamente la bussola al suo
interno, poi usa `metti sestante là` e verifica che il referente locativo sia
stato aggiornato.

## Esercizio risolto: cambiare destinazione

Apri `examples/tutorial/31b_due_destinazioni.locus` oppure copia:

```locus
Titolo: "Cambiare destinazione".
Autore: "Esempio LOCUS".

La Sala carteggio è una stanza.
Inizia nella Sala carteggio.
Il baule è un contenitore nella Sala carteggio.
Il baule ha stato "aperto".
La cassetta è un contenitore nella Sala carteggio.
La cassetta ha stato "aperto".
La bussola è una cosa nella Sala carteggio.
Il sestante è una cosa nella Sala carteggio.
```

1. `prendi bussola`, `metti bussola nel baule`: ora lì indica il baule.
2. `prendi bussola`, `metti bussola nella cassetta`: la destinazione cambia.
3. `prendi sestante`, `metti sestante là`: il sestante va nella cassetta.
4. `esamina baule`: è vuoto. `esamina cassetta`: contiene entrambi gli strumenti.

Esaminare un contenitore cambia il referente diretto, ma non quello locativo.
Perciò guardare il baule dopo il passaggio 2 non annulla la scelta della cassetta.

**Un tentativo fallito non cambia destinazione.** Dopo il passaggio 2, chiudi
il baule e prendi il sestante. `metti sestante nel baule` fallisce perché
il baule è chiuso. `metti sestante lì` usa ancora la cassetta e riesce.
Un errore non sceglie implicitamente una nuova destinazione.

**Una destinazione ricordata può diventare inaccessibile.** In una nuova
partita arriva al passaggio 2, chiudi la cassetta e prendi il sestante.
`metti sestante là` riconosce la cassetta, ma chiede di aprirla. Aprila e
ripeti lo stesso comando: la memoria locativa è conservata anche dopo
l’apertura. Non serve riscrivere il nome della destinazione.
