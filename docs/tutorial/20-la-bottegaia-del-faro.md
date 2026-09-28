# 20. La bottegaia, la scorta e la rivendita

Apri `examples/tutorial/20_bottegaia_e_rivendita.locus` nello Studio e scegli
**Compila e prova**. Questa lezione estende il mercato con una persona che vende,
incassa e può ricomprare gli oggetti.

## Preparare venditore e scorta

```locus
La Bottega è una stanza.
Il credito portuale è una valuta.
Il credito portuale ha saldo 20.

La Ada è una mercante nella Bottega.
La Ada ha cassa 25.

La bussola è un prodotto nella Bottega.
La bussola ha prezzo 7.
La bussola ha prezzo di rivendita 3.
La Ada vende la bussola.
```

Prova questo percorso:

```text
> compra bussola da Ada
Hai comprato: bussola da Ada per 7 unità di credito portuale. Saldo: 13.
> vendi bussola a Ada
Hai venduto: bussola a Ada per 3 unità di credito portuale. Saldo: 16.
> compra bussola
Hai comprato: bussola da Ada per 7 unità di credito portuale. Saldo: 9.
```

Nel primo acquisto la cassa passa da 25 a 32. La rivendita la porta a 29 e
rimette la bussola nella scorta. Il secondo acquisto porta la cassa a 36.

## Verificare l'Indice del mondo

Apri **Indice del mondo**, sezione **Commercio**. Prima dell'acquisto la bussola
mostra `Ada` come venditore. Mentre è nell'inventario il venditore è assente;
dopo la vendita ricompare. La stessa tabella mostra saldo, cassa, prezzo e
rivendita aggiornati.

## Esperimenti negativi

Togli `La Ada vende la bussola.`: la compilazione produce `E125`, perché una
storia con mercanti non può lasciare merci non possedute fuori da ogni scorta.
Poi imposta la cassa a `0` e la rivendita a `10`: dopo l'acquisto Ada ha soltanto
7 crediti e rifiuta la vendita senza modificare inventario, proprietà o saldi.

## Esercizio

Aggiungi il mercante Bruno nella stessa stanza. Dopo aver comprato la bussola,
prova `vendi bussola`: LOCUS chiederà quale mercante intendi. Completa con
`vendi bussola a Bruno` e controlla che la bussola entri nella scorta di Bruno,
non in quella di Ada.

La [specifica di mercanti e vendita](../linguaggio/mercanti-e-vendita.md)
descrive tutti gli invarianti e le forme dei comandi.
