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

## Soluzione completa: trasferire la scorta fra mercanti

Apri `examples/tutorial/20b_due_mercanti.locus` oppure copia questo progetto:

```locus
Titolo: "Due banchi al mercato".
Autore: "Esempio LOCUS".

Il Mercato è una stanza.
Inizia nella "Mercato".
Il credito è una valuta.
Il credito ha saldo 20.
La Ada è una mercante nel Mercato.
La Ada ha cassa 25.
Il Bruno è un mercante nel Mercato.
Il Bruno ha cassa 10.
La bussola è un prodotto nel Mercato.
La bussola ha prezzo 7.
La bussola ha prezzo di rivendita 3.
La Ada vende la bussola.
```

Segui `20b_due_mercanti.comandi`. All'inizio Bruno non vende la bussola:
`compra bussola da Bruno` fallisce senza trasferire denaro. Comprala da Ada
per sette crediti: il saldo diventa 13, Ada ha 32 e Bruno resta a 10.

Ora scrivi `vendi bussola`: LOCUS chiede quale mercante intendi. `denaro`
mostra 13 e conserva la domanda; `scegli 99` la ripropone. Con `scegli Bruno`
la vendita riesce: il saldo diventa 16, Bruno scende a 7 e Ada resta a 32.
Nell'Indice la bussola deve risultare nella scorta di Bruno.

Prova a ricomprarla da Ada: deve fallire. Da Bruno costa ancora sette crediti:
il saldo scende a 9 e la cassa di Bruno sale a 14. I prezzi appartengono al
prodotto, non cambiano automaticamente in base al venditore.

**Variante negativa:** imposta la cassa iniziale di Bruno a 2. La rivendita
richiede tre crediti e viene rifiutata: mantieni bussola e saldo 13, mentre
Bruno conserva i suoi due crediti. Non avviene alcun trasferimento parziale.
