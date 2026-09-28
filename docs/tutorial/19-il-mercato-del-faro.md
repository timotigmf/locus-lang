# 19. Comprare provviste al mercato

Questa lezione introduce valuta, saldo, merci e acquisti atomici. Apri
`examples/tutorial/19_mercato_del_faro.locus` nello Studio e scegli
**Compila e prova**.

## Preparare il mercato

```locus
La Bottega è una stanza.
Il credito portuale è una valuta.
Il credito portuale ha saldo 15.

Una provvista nautica è un tipo di prodotto.
La bussola tascabile è una provvista nautica nella Bottega.
La bussola tascabile ha prezzo 7.
La corda cerata è una provvista nautica nella Bottega.
La corda cerata ha prezzo 9.
```

Prova questo percorso:

```text
> denaro
Saldo: 15 unità di credito portuale.
> prendi bussola
Devi prima comprare: bussola tascabile.
> compra bussola
Hai comprato: bussola tascabile per 7 unità di credito portuale. Saldo: 8.
La bottegaia annota l'acquisto sul registro.
> compra corda
Fondi insufficienti: servono 9 unità, saldo disponibile 8.
```

Apri **Indice del mondo**: la tabella Commercio mostra il nuovo saldo e la
bussola nell'inventario. La corda resta nella Bottega perché il pagamento
fallito non modifica alcuna parte del mondo.

## Esperimento negativo

Togli la riga del prezzo della bussola:

```text
La bussola tascabile è una provvista nautica nella Bottega.
```

La compilazione produce `E124`: ogni merce deve avere un prezzo maggiore di
zero. Prova anche ad aggiungere una seconda valuta; IR 19 rifiuta l'ambiguità
anziché scegliere silenziosamente quale saldo addebitare.

## Esercizio

Aggiungi una `mappa nautica` da 5 crediti. Comprala dopo la bussola e verifica
che il saldo passi da 15 a 8 e poi a 3. Lasciala e usa `prendi mappa`: LOCUS deve
riconoscere che è già stata pagata.

La [specifica di denaro e acquisti](../linguaggio/denaro-e-acquisti.md) descrive
invarianti, alias, regole e limiti del primo incremento commerciale.
