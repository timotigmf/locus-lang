# Persone e dialoghi strutturati

Stato: implementato nell'IR 16.

## Persone

`persona` è un tipo predefinito della libreria narrativa. Una persona può stare
in una stanza, essere visibile ed essere esaminata, ma non può essere presa o
inserita nell'inventario:

```locus
La Sala è una stanza.
La guardiana è una persona nella Sala.
La guardiana ha descrizione "Porta il sigillo del faro.".
```

Per compatibilità, la vecchia frase `Una persona è un tipo di cosa.` è accettata
e non crea un secondo tipo.

## Dichiarare un dialogo

Un dialogo appartiene a una persona e contiene da 1 a 128 nodi. Il primo nodo è
il punto iniziale. Ogni nodo pronuncia una battuta e può offrire fino a 32
scelte:

```locus
La Sala è una stanza.
La guardiana è una persona nella Sala.

Dialogo "segreti del faro" con "guardiana":
    Nodo "inizio" dice "La guardiana attende la tua domanda.":
        Scelta "Chiedi della lanterna" porta a "lanterna".
        Scelta "Saluta e concludi" termina.
    Fine nodo.
    Nodo "lanterna" dice "La fiamma rivela i segni sulla parete.":
        Scelta "Torna indietro" porta a "inizio".
        Scelta "Concludi" termina.
    Fine nodo.
Fine dialogo.
```

I nomi di dialogo e nodo sono univoci. Ogni scelta conduce a un nodo dello
stesso dialogo oppure termina la conversazione. I cicli sono ammessi; un nodo
che non può essere raggiunto dal primo è rifiutato. Un nodo senza scelte termina
dopo la propria battuta.

Il compilatore produce identificatori distinti per dialoghi, nodi e scelte e
risolve tutte le destinazioni nell'IR. `E118` segnala dialoghi duplicati o più
dialoghi assegnati alla stessa persona; `E119` segnala grafi, nodi o scelte non
validi; `E120` segnala un partecipante assente o di tipo diverso da `persona`.

## Giocare una conversazione

Nei progetti che dichiarano almeno un dialogo sono disponibili:

| Comando | Effetto |
| --- | --- |
| `parla con guardiana` | apre il dialogo dal primo nodo |
| `parla guardiana`, `p guardiana`, `talk to guardiana` | forme equivalenti |
| `1`, `2`, … | sceglie l'opzione numerata |
| `scegli lanterna` | sceglie un testo univoco anche parziale |
| `basta`, `fine dialogo` | interrompe la conversazione |

Durante una conversazione occorre scegliere o terminarla; gli altri comandi non
avanzano il mondo. Ogni passaggio produce un record di trace con dialogo, nodo,
scelta ed esito. La sessione conserva i nodi già visitati. Parlare di nuovo con
la persona ricomincia dal primo nodo senza cancellare questa memoria.

Una scelta inesistente, fuori intervallo o testualmente ambigua restituisce
`invalid_choice` senza cambiare la sessione. La presentazione ripropone le
opzioni numerate del nodo corrente, senza ripetere la battuta o avanzare il
turno. Il giocatore può correggere la risposta nello stesso dialogo.

Lo Studio elenca dialoghi, persona, numero di nodi e nodo iniziale nell'Indice
del mondo. Il pannello **Regole e trace** mostra il nodo percorso e la scelta.

## Limiti dell'incremento

Le scelte e le battute sono statiche. Non hanno ancora condizioni o effetti di
regola, non interpolano proprietà e non cambiano parlante. Ogni persona ha un
solo dialogo. Argomenti liberamente digitati, conoscenze condivise, scelte
visibili soltanto in certe condizioni e modifiche transazionali del mondo sono
estensioni successive del contratto, non testo reinterpretato dal runtime.

## Robustezza delle risposte numeriche

Le risposte decimali sono confrontate con il numero delle alternative senza
convertire l'intera stringa in un intero illimitato. Anche un numero incollato
molto lungo produce il normale errore di scelta e conserva la sessione. Zero
non seleziona alcuna alternativa; gli zeri iniziali sono ammessi (`0001` vale
`1`), anche con cifre decimali Unicode.

## Risposte testuali senza prefisso

Durante un dialogo, un testo che non è un comando riconosciuto viene cercato
fra le scelte del nodo corrente. `chiave` equivale quindi a `scegli chiave`
se identifica una sola opzione. Un testo ambiguo, assente o vuoto produce
`invalid_choice` e ripresenta le alternative senza avanzare la conversazione.

I comandi riconosciuti mantengono la precedenza: `aiuto` mostra l'aiuto e
`basta` termina il dialogo. Per scegliere un'etichetta che coincide con un
comando, usa il suo numero o il prefisso `scegli`. Fuori dalla conversazione
non viene interpretata alcuna risposta testuale contestuale.

## Etichette fra virgolette

Durante una conversazione puoi rispondere con `"Chiedi della chiave"`.
Le virgolette vengono rimosse e gli articoli interni all'etichetta restano
parte del testo da confrontare. Anche `"Aiuto"` seleziona una scelta chiamata
Aiuto, mentre `aiuto` senza virgolette conserva il significato di comando.
Virgolette non chiuse o etichette assenti producono una scelta non valida
e lasciano aperta la conversazione. Fuori dal dialogo non avviene questa
interpretazione contestuale.
