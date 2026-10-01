# 32. Ricordare oggetto e strumento

Apri `examples/tutorial/32_pronomi_per_ruolo.locus` nello Studio e premi
**Compila e prova**.

## Stabilire i due ruoli

```text
> prendi chiave
Hai preso: chiave di bronzo.
> apri cofano con chiave
Hai aperto: cofano.
```

L'azione riuscita ricorda il cofano come oggetto diretto e la chiave come
secondo oggetto.

## Riutilizzare entrambi

```text
> chiudilo
Hai chiuso: cofano.
> aprilo con essa
Hai aperto: cofano.
```

`lo` indica il cofano; `essa`, trovandosi dopo `con`, indica la chiave. I due
pronomi vengono risolti prima di eseguire l'azione.

## Prova negativa

Riavvia, esamina il cofano e digita `aprilo con essa` senza aver preso una
chiave. Non esiste ancora un secondo referente: il ripiego usa il cofano anche
come strumento e i controlli di apertura lo rifiutano. Il gioco non sceglie una
chiave dalla stanza in modo nascosto.

## Esercizio

Aggiungi una chiave errata. Prova prima ad aprire il cofano con quella, poi usa
la chiave corretta e ripeti `chiudilo`, `aprilo con essa`. Verifica che soltanto
l'azione riuscita stabilisca lo strumento ricordato.
