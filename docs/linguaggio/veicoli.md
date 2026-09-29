# Veicoli e movimento del conducente

Stato: implementato nell'IR 18.

## Dichiarare un veicolo

`veicolo` è un tipo standard collocabile e non trasportabile. Può essere usato
direttamente oppure come genitore di categorie più precise:

```locus
La Rimessa è una stanza.
La Piazza è una stanza.
La Piazza è a est della Rimessa.

Una bicicletta da carico è un tipo di veicolo.
La saetta rossa è una bicicletta da carico nella Rimessa.
```

Un veicolo deve trovarsi direttamente in una stanza. Collocarlo dentro un
contenitore produce `E123` con la posizione della dichiarazione. Un veicolo può
essere descritto, esaminato, nascosto o rivelato con le proprietà standard, ma
non può essere preso e messo nell'inventario.

## Salire, muoversi e scendere

Il giocatore può usare:

- `sali sulla saetta`, `entra nella saetta` o `sali a bordo della saetta`;
- `scendi`, `scendi dalla saetta` o `esci dalla saetta`;
- gli alias classici `board`, `enter`, `exit` e `get out`.

Il nome parziale deve identificare un solo veicolo raggiungibile. Salire su un
oggetto comune, tentare di cambiare veicolo senza scendere o indicare il mezzo
sbagliato produce un evento distinto e un messaggio italiano.

Quando il giocatore è a bordo, un comando cardinale sposta nello stesso snapshot
la posizione del giocatore e la relazione `nella` del veicolo. Se una porta
chiusa o l'assenza di un'uscita impedisce il viaggio, nessuno dei due cambia
posizione. `guarda` indica il mezzo guidato senza elencarlo di nuovo fra gli
oggetti visibili.

Le azioni standard `salire` e `scendere` partecipano alle fasi delle regole:

```locus
La Rimessa è una stanza.
La saetta rossa è un veicolo nella Rimessa.

Regola "campanello" per salire "saetta rossa" nella fase dopo:
    dì "Il campanello annuncia la partenza.";
Fine regola.
```

Le parole di comando dei veicoli sono riservate soltanto quando la storia
dichiara almeno un veicolo. I progetti precedenti possono continuare a definire
un'azione propria con comando `entra`.

## Studio, mappa e stato

Lo Studio conta i veicoli, mostra tipo e posizione nell'Indice del mondo e li
scrive nei dati JSON della mappa. L'SVG annota il mezzo nella stanza corrente e
si aggiorna dopo ogni viaggio. L'API dello Studio espone inoltre `vehicle` con
l'ID del mezzo guidato e le relazioni dello snapshot corrente.

## Limiti dell'incremento

IR 18 modella un solo conducente e un solo veicolo guidato alla volta. Passeggeri,
oggetti caricati, capienza, carburante, rotte riservate a strada o acqua,
veicoli autonomi e movimento verticale richiedono contratti successivi. In
questa versione il giocatore può percorrere a piedi gli stessi collegamenti
della rosa dei venti o fra livelli quando non è a bordo.
