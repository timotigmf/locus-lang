# Elenchi tipati

Stato: implementato nell'IR 14.

## Dichiarazione

Una proprietà può contenere un elenco omogeneo di testi, numeri o valori
logici. Ogni elenco nasce vuoto:

```locus
La indizi è una proprietà elenco di testi.
La temperature è una proprietà elenco di numeri.
La verifiche è una proprietà elenco di logici.
```

Il tipo dell'elemento fa parte dello schema. Il compilatore rifiuta, per
esempio, `aggiungi 3` su un elenco di testi con `E313`. In questa versione non
esistono letterali di elenco e non si assegna l'intera collezione con `ha` o
`imposta`: lo stato iniziale è sempre vuoto e si modifica con gli effetti.

## Aggiungere e rimuovere

```locus
La Sala è una stanza.
L'impronta è uno scenario nella Sala.
Il taccuino è uno scenario nella Sala.
La indizi è una proprietà elenco di testi.
Azione "dimenticare" senza oggetti con comando "dimentica".

Regola "registra l'orma" per esaminare "impronta" nella fase dopo:
    aggiungi "orma" a "indizi" di "taccuino";
Fine regola.

Regola "scarta l'orma" per dimenticare nella fase invece:
    rimuovi "orma" da "indizi" di "taccuino";
Fine regola.
```

`aggiungi` inserisce in coda e conserva eventuali duplicati. `rimuovi` elimina
la prima occorrenza uguale; se l'elemento non è presente non cambia nulla.
Entrambi gli effetti sono transazionali: se l'azione fallisce in una fase
successiva, il motore ripristina l'elenco precedente.

La fase `verifica` non può modificare collezioni, come non può usare `imposta` o
`aumenta`. Un tentativo produce `E307` con la posizione dell'istruzione.

## Verificare l'appartenenza

La condizione `contiene` confronta un elemento con l'elenco tipato:

```locus
La Sala è una stanza.
Il taccuino è uno scenario nella Sala.
La indizi è una proprietà elenco di testi.
Azione "dedurre" senza oggetti con comando "deduci".

Regola "deduzione completa" per dedurre nella fase invece
quando "indizi" di "taccuino" contiene "orma"
e "indizi" di "taccuino" contiene "fibra rossa":
    dì "I due indizi indicano la serra.";
Fine regola.
```

Per verificare l'assenza si usa l'operatore booleano `non`:

```text
quando non "indizi" di "taccuino" contiene "orma"
```

L'appartenenza usa uguaglianza esatta e non converte testi, numeri o valori
logici. Le normali parentesi e gli operatori `e`/`o` permettono di combinare più
prove.

## Limiti

Gli elenchi sono proprietà di entità e non valori annidabili. Non sono ancora
disponibili indice, ordinamento, lunghezza, scorrimento, interpolazione nella
narrazione, letterali, tabelle o record. Il giocatore non vede automaticamente
il contenuto: l'autore lo racconta con regole e condizioni. Le tabelle avranno
un contratto separato, perché richiedono colonne nominate e righe tipate.
