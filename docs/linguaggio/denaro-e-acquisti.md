# Denaro e acquisti

Stato: implementato nell'IR 19.

## Dichiarare valuta e merci

Una `valuta` identifica l'unità usata dalla storia. `saldo` indica quante unità
possiede il giocatore. Un `prodotto` è una cosa trasportabile che richiede un
`prezzo` positivo:

```locus
La Bottega è una stanza.
Il credito portuale è una valuta.
Il credito portuale ha saldo 15.

Una provvista è un tipo di prodotto.
La bussola è una provvista nella Bottega.
La bussola ha prezzo 7.
```

La valuta è globale: non deve essere collocata in una stanza e non appare fra
gli oggetti visibili. In IR 19 una storia ammette una sola valuta. Più valute,
saldo negativo, merci senza valuta e prezzi nulli o negativi producono `E124`
con la posizione della dichiarazione responsabile.

## Comprare e controllare il saldo

Il giocatore può usare `compra la bussola`, `acquista bussola`, `buy compass`
quando il nome inglese è stato dichiarato come sinonimo, oppure `purchase`.
`denaro`, `saldo`, `money` e `balance` mostrano il saldo senza consumare un
turno narrativo.

Un acquisto riuscito esegue in un'unica transizione:

1. verifica che l'oggetto sia raggiungibile e sia una merce;
2. legge prezzo e saldo della valuta;
3. rifiuta l'operazione se i fondi non bastano;
4. sposta la merce nell'inventario;
5. registra il possesso e sottrae il prezzo.

`prendi` non può evitare il pagamento. Dopo l'acquisto, una merce lasciata può
essere ripresa senza un secondo addebito. Un tentativo di ricomprarla invita a
usare `prendi`. La sessione e l'API dello Studio espongono il registro `owned`.

## Regole e prezzi dinamici

`comprare` è un'azione standard con un argomento di tipo `prodotto`:

```locus
La Bottega è una stanza.
Il credito è una valuta.
Il credito ha saldo 10.
La bussola è un prodotto nella Bottega.
La bussola ha prezzo 4.

Regola "ricevuta" per comprare "bussola" nella fase dopo:
    dì "La bottegaia annota l'acquisto.";
Fine regola.
```

Le regole possono leggere, aumentare, diminuire o impostare `saldo` e `prezzo`
come le altre proprietà numeriche. La validazione transazionale impedisce che
il saldo diventi negativo o che un prezzo diventi non positivo.

## Studio e limiti

L'Indice del mondo contiene una sezione **Commercio** con valuta, saldo, merci,
prezzi e posizione corrente. Dopo un acquisto aggiorna saldo e posizione in
inventario. La diagnostica `E124` apre direttamente questa pagina.

IR 19 non modella ancora venditori, incassi, scorte, vendita da parte del
giocatore, più valute, cambio, prestiti, merci gratuite o prezzi espressi in
unità diverse. Questi casi richiedono contratti ulteriori; non sono simulati da
testi o convenzioni implicite.
