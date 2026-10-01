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
