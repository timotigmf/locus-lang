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

## Esercizio risolto: una chiave errata non cambia lo strumento

Apri `examples/tutorial/32b_due_chiavi_e_pronomi.locus` oppure copia:

```locus
Titolo: "Ricordare la chiave giusta".
Autore: "Esempio LOCUS".

La Sala è una stanza.
Inizia nella Sala.
Il cofano è un contenitore nella Sala.
Il cofano ha stato "bloccato".
La chiave di bronzo è una chiave nella Sala.
La chiave di ferro è una chiave nella Sala.
La chiave di bronzo apre il cofano.
```

| Comando | Risultato e memoria |
| --- | --- |
| `prendi chiave di ferro` | Presa; referente diretto: ferro |
| `prendi chiave di bronzo` | Presa; referente diretto: bronzo |
| `apri cofano con chiave di ferro` | Chiave errata; nessuno strumento memorizzato |
| `apri cofano con chiave di bronzo` | Aperto; diretto: cofano, indiretto: bronzo |
| `chiudilo` | Cofano chiuso; strumento ancora bronzo |
| `bloccalo con chiave di ferro` | Fallisce; entrambi i referenti restano invariati |
| `bloccalo con essa` | Blocca usando la chiave di bronzo |
| `aprilo con essa` | Apre di nuovo con la chiave di bronzo |

La memoria non corrisponde all’ultimo nome scritto: segue gli argomenti delle
azioni riuscite. Anche dopo aver nominato ferro in un tentativo fallito,
`essa` nel ruolo dello strumento continua a indicare bronzo.

**Prova di accessibilità.** Dopo l’ultima apertura, usa `lascia chiave di bronzo`,
poi `esamina cofano` e `chiudilo`. Ora `aprilo con essa` riconosce ancora
la chiave di bronzo, ma richiede di prenderla. Ricordare un oggetto non permette
di usarlo senza rispettare possesso e accessibilità. Correggi con
`prendi chiave di bronzo`, `esamina cofano`, `aprilo con essa`.

**Ambiguità.** Le due chiavi sono entrambe raggiungibili: il solo nome
`chiave` può richiedere un chiarimento. Questo copione usa i nomi completi
per isolare il comportamento dei pronomi.
