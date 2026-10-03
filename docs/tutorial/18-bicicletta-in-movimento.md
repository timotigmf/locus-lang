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

## Soluzione: due mezzi, un conducente

Apri `examples/tutorial/18b_due_mezzi.locus` oppure copia questa storia completa:

```locus
Titolo: "Due mezzi in rimessa".
Autore: "Esempio LOCUS".

La Rimessa è una stanza.
La Piazza è una stanza.
La Piazza è a est della Rimessa.
Inizia nella Rimessa.

Una bicicletta da carico è un tipo di veicolo.
La saetta rossa è una bicicletta da carico nella Rimessa.
Il triciclo blu è un veicolo nella Rimessa.
```

| Comando | Cosa verificare |
| --- | --- |
| `sali sul triciclo` | Il nome parziale seleziona il triciclo blu |
| `sali sulla saetta` | Cambio rifiutato: sei ancora sul triciclo |
| `scendi dalla saetta` | Mezzo sbagliato: resti sul triciclo |
| `nord` | Non c'è un passaggio: conducente e mezzo restano in Rimessa |
| `est` | Conducente e triciclo raggiungono la Piazza; la saetta resta in Rimessa |
| `scendi` | Lasci il triciclo in Piazza |
| `ovest` | Torni a piedi in Rimessa |
| `sali sulla saetta` | Ora puoi guidare la saetta |
| `est` | Raggiungi il triciclo in Piazza |

Controlla la mappa dopo ciascun viaggio. Il mezzo non guidato conserva la
propria posizione: non segue il giocatore e non torna automaticamente in rimessa.
Il rifiuto del cambio e la discesa dal mezzo sbagliato conservano anche il mezzo
attualmente guidato. Non basta scrivere il nome di un altro veicolo per cambiarlo.

Questo laboratorio verifica il contratto esistente di un solo conducente.
Il sottotipo «bicicletta da carico» è un nome scelto dall'autore: non aggiunge
un inventario di carico, passeggeri o capacità, che restano fuori da questo incremento.
