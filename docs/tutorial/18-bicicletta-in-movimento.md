# 18. Attraversare la città in bicicletta

Questa lezione introduce il tipo `veicolo`, le azioni di salita e discesa e il
movimento congiunto. Apri
`examples/tutorial/18_bicicletta_in_movimento.locus` nello Studio e scegli
**Compila e prova**.

## Un tipo di veicolo

```locus
La Rimessa è una stanza.
La Piazza è una stanza.
La Piazza è a est della Rimessa.

Una bicicletta da carico è un tipo di veicolo.
La saetta rossa è una bicicletta da carico nella Rimessa.
```

Prova questo percorso:

```text
> sali sulla saetta
Sei salito a bordo di: saetta rossa.
Il campanello annuncia la partenza.
> est
Piazza
...
Sei a bordo di: saetta rossa.
> scendi
Sei sceso da: saetta rossa.
Appoggi con cura il cavalletto.
```

Apri **Mappa** prima e dopo `est`: la bicicletta passa dalla Rimessa alla Piazza.
Nell'**Indice del mondo**, la sezione Veicoli mostra il sottotipo e la posizione
corrente.

## Esperimento negativo

Aggiungi un contenitore e prova a collocarvi la bicicletta:

```text
Il cassone è un contenitore nella Rimessa.
La saetta rossa è una bicicletta da carico nel cassone.
```

La compilazione produce `E123`, perché il primo contratto dei veicoli richiede
una collocazione diretta in una stanza. Durante il gioco prova anche `sali sulla
Rimessa`: LOCUS risponde che la Rimessa non è un veicolo.

## Esercizio

Aggiungi un secondo mezzo chiamato `triciclo blu`. Verifica che `sali sul
triciclo` lo selezioni e che non sia possibile passare alla saetta senza prima
usare `scendi`.

La [specifica dei veicoli](../linguaggio/veicoli.md) descrive alias, invarianti,
regole e limiti del primo incremento.
