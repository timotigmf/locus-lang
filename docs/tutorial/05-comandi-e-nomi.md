# 5. Comandi, abbreviazioni e nomi degli oggetti

Questa lezione usa `examples/tutorial/02_custodia.locus`. Nello Studio scegli
**Apri esempio del faro**, poi apri il file `faro/mondo.locus` per confrontare il
mondo dichiarato con ciò che il giocatore può comandare.

## Obiettivo

Imparerai a distinguere tre elementi:

1. il **verbo**, che indica l'azione (`esamina`, `prendi`, `apri`);
2. il **nome**, che individua un oggetto raggiungibile (`custodia`, `chiave`);
3. l'eventuale **secondo oggetto** (`metti chiave nella custodia`).

La sintassi con cui si scrive la storia resta italiana. Nel riquadro di gioco sono
accettate anche alcune convenzioni storiche delle avventure testuali in inglese.

| Forma italiana | Forma compatibile | Azione |
| --- | --- | --- |
| `guarda` | `l`, `look` | Ripete la descrizione del luogo |
| `esamina custodia` | `x custodia`, `examine custodia` | Mostra dettagli e stato |
| `inventario` | `i`, `inv`, `inventory` | Elenca ciò che porti |
| `nord`, `sud`, `est`, `ovest` | `n`, `s`, `e`, `o`, `w` e forme inglesi | Si sposta sulla mappa |
| `prendi chiave` | `get chiave`, `take chiave` | Prende un oggetto |
| `esci` | `q`, `quit` | Termina la sessione |

Sono disponibili anche `open`, `close`, `drop`, `put ... in ...` e
`lock ... with ...`. Le forme inglesi sono scorciatoie di input: i messaggi, il
manuale e il linguaggio dell'autore restano italiani.

## Esperimento guidato

Esegui questi comandi uno alla volta:

```text
x custodia
open custodia
x custodia
take chiave
i
```

Prima dell'apertura, la chiave non appartiene al campo d'azione del giocatore.
Dopo `open custodia`, `take chiave` individua **chiave di rame** anche senza il
complemento `di rame`, perché in quel momento esiste una sola chiave raggiungibile.

## Nomi abbreviati e ambiguità

LOCUS prova prima il nome completo. Se non lo trova, usa le parole fornite come
vocabolario parziale. Per esempio, `chiave` può indicare `chiave di rame` e
`porta rossa` continua a preferire un oggetto chiamato esattamente `porta rossa`.

Il completamento avviene soltanto fra gli oggetti raggiungibili. Se sono presenti
sia `chiave di rame` sia `chiave di ferro`, il sistema non sceglie arbitrariamente:

```text
> prendi chiave
Quale intendi: chiave di rame o chiave di ferro?
> prendi chiave di rame
Hai preso: chiave di rame.
```

Questa richiesta di chiarimento evita che una storia dipenda dall'ordine interno
degli oggetti. Non è ancora un dialogo a due turni: dopo la domanda occorre ripetere
il comando completo.

## Prova negativa

Digita soltanto `x`. Il verbo viene riconosciuto, ma manca l'oggetto:

```text
> x
Indica quale oggetto vuoi esaminare o manipolare.
```

Un comando incompleto è diverso da un verbo sconosciuto. Questa distinzione è
utile quando si scrivono test e quando si progetta l'esperienza del giocatore.

## Esercizio d'autore

Aggiungi una seconda chiave raggiungibile al Molo:

```locus
Il Molo è una stanza.
La chiave di ferro è una chiave nel Molo.
```

Ricompila e prova `prendi chiave`. Verifica la domanda di disambiguazione, poi
sposta la chiave di ferro in una stanza diversa e ripeti. Il comando corto tornerà
a essere sufficiente perché nel luogo corrente rimane una sola candidata.

## Verifica automatica

Nel pannello **Test** crea un copione esplorativo con i cinque comandi della prova
guidata. Eseguilo, controlla il transcript e scaricalo. Poi copia l'uscita nel campo
**Uscita attesa**: da quel momento il test segnalerà qualsiasi cambiamento futuro.

Il percorso segue una progressione simile ai manuali narrativi: esempio completo,
esperimento, caso ambiguo, esercizio e verifica. Tutto il codice mostrato è LOCUS
eseguibile; i limiti sono dichiarati accanto alla funzione che insegnano.
