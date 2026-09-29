# M3 — regole controllate

Specifica normativa di LOCUS 0.3.0a1, aggiuntiva a M2. IR versione 4.
La sintassi autore, i comandi e i messaggi sono italiani; gli identificatori
interni Python/IR rimangono un contratto tecnico sperimentale.

Una regola ha nome unico, azione, fase, priorità intera facoltativa (default 0,
intervallo ±1000000), condizione facoltativa (default vero), istruzioni e chiusura.
L'indentazione è libera; ogni istruzione termina con `;`, il blocco con `Fine regola.`.
Nomi di regole, proprietà e oggetti nelle regole sono sempre fra virgolette.
Dichiarazioni e regole possono fare riferimenti in avanti.

```locus
La Sala è una stanza.
La leva è una cosa nella Sala.
La attiva è una proprietà logica.
Regola "attivazione" per esaminare "leva" nella fase dopo priorità 10
quando non "attiva" di "leva" è vero:
    imposta "attiva" di "leva" a vero;
    dì "La leva è attiva.";
Fine regola.
```

Azioni registrate dalla libreria narrativa: `guardare`, `inventariare`,
`andare a nord`, `andare a sud`, `andare a est`, `andare a ovest`, le quattro
azioni diagonali, `andare su`, `andare giù`, `prendere`,
`aprire`, `chiudere`, `mettere`, `lasciare`, `esaminare`, `bloccare`.
Un selettore senza oggetti si applica a tutti gli oggetti; un oggetto
quotato restringe il destinatario, `con "nome"` restringe il secondo oggetto.
La stessa sintassi specifica un'azione sostitutiva, ma lì gli oggetti obbligatori
non possono essere omessi. `mettere` e `bloccare` richiedono due oggetti;
`aprire` accetta una chiave facoltativa. Il parser giocatore conserva `metti X in Y`.
Nuovi verbi sono registrabili mediante API `ActionSpec`. La successiva specifica
delle [azioni dell'autore](azioni-autore.md) li rende dichiarabili anche nel sorgente.

## Condizioni e istruzioni

Valori: interi, stringhe, `vero` e `falso`, senza coercizioni implicite.
Condizioni: `"proprietà" di "oggetto" è valore`, oppure `è diverso da`,
`è maggiore di`, `è minore di`, `è almeno`, `è al massimo`.
I confronti ordinati richiedono numeri. `non`, `e`, `o` hanno questa precedenza,
con cortocircuito; parentesi per raggruppare, massimo 64 livelli annidati.
Le condizioni vengono rivalutate sullo stato corrente prima di ogni regola.

| Istruzione | Effetto |
| --- | --- |
| `dì "testo";` | Accoda testo all'uscita |
| `imposta "prop" di "oggetto" a valore;` | Assegna una proprietà tipata |
| `aumenta "prop" di "oggetto" di 2;` | Incrementa un intero |
| `diminuisci "prop" di "oggetto" di 2;` | Decrementa un intero |
| `continua;` | Termina questa regola e prova la successiva della fase |
| `interrompi;` | Termina l'azione conservando gli effetti riusciti |
| `fallisci "motivo";` | Ripristina lo stato iniziale e mostra soltanto il motivo |
| `sostituisci con prendere "oggetto";` | Esegue un'altra azione e termina la corrente |
| `restituisci valore;` | Termina l'azione con un risultato tipato |

Dopo un'istruzione terminale non sono ammesse altre istruzioni nella stessa regola.
Il risultato è disponibile in `Transition.result`; la CLI lo presenta in italiano.
Le proprietà enumerate della stdlib conservano i loro vincoli anche nelle regole.

## Ordine delle fasi

1. `prima`: preparazione.
2. `invece`: la prima regola applicabile che termina normalmente sostituisce
   verifica/esegui/azione predefinita. `continua` passa alla successiva; se nessuna
   gestisce l'azione si procede con il comportamento predefinito.
3. `verifica`: controlli; vietati assegnazioni, incrementi e sostituzioni.
4. `esegui`: effetti autore, poi azione predefinita, salvo esito terminale.
5. `dopo`: effetti successivi al successo.
6. `descrivi`: la prima regola che termina normalmente sostituisce la narrazione
   predefinita; `continua` permette di aggiungere testo senza sostituirla.

Ogni fase ordina per priorità decrescente e poi ordine sorgente. Nelle fasi
prima/verifica/esegui/dopo, il termine normale passa alla regola successiva.
Interrompi/fallisci/restituisci/sostituisci terminano l'azione, senza fasi successive.
Una sostituzione ricomincia dalla fase prima dell'azione nuova. Una ripetizione
identica nella catena oppure più di otto azioni produce un errore con ripristino.
Nessuna ricorsione illimitata o valutazione di testo durante l'esecuzione.

Lo stato è immutabile: il fallimento di qualsiasi fase, azione predefinita o
sostituzione annulla tutte le modifiche e i testi dell'intera azione iniziale.
Il trace rimane disponibile. Un'azione predefinita impossibile, anche perché già
compiuta, è un fallimento. `interrompi` invece conserva gli effetti precedenti.
Output normale: testi prima dell'azione, narrazione predefinita, testi dopo/descrivi.
Un esito terminale in dopo/descrivi conserva la narrazione già prodotta, tranne
fallisci. Gli eventi sono resi sullo stato finale della transazione.

La risoluzione iniziale degli oggetti del comando giocatore precede le regole:
un nome assente/non raggiungibile non attiva regole. `esci` e comandi non riconosciuti
non attraversano il motore. Un movimento produce la descrizione della nuova stanza
senza generare un secondo evento autore `guardare`. All'avvio `gioca`/`debug`
eseguono invece una vera azione guardare, conservandone gli effetti.

## Diagnostica e debug

`locus debug examples/regole.locus` gioca e scrive su stderr nome, fase, priorità,
esito e posizione delle regole considerate. `gioca` conserva soltanto la narrazione.
Le regole escluse per azione/oggetti non appaiono; quelle con condizione falsa sì.
Trace strutturato disponibile come `Transition.trace` anche in caso di rollback.

E301 nome duplicato; E302 istruzione/annidamento non valido; E303 azione sconosciuta;
E304 proprietà sconosciuta; E305 tipo incompatibile; E306 numero di oggetti;
E307 mutazione nella verifica; E308 istruzione irraggiungibile; E309 priorità fuori
intervallo. Gli errori sintattici comuni riutilizzano E002 e gli errori di riferimento
E103. I confronti puntano all'inizio della regola, gli effetti alla loro istruzione.

Limiti: niente variabili locali, riferimenti al destinatario implicito, funzioni,
espressioni aritmetiche generali, regole su relazioni,
salvataggi o debugger interattivo. Le regole sono compilate in IR strutturata;
non esiste un caricatore JSON per input esterno. Non è una parità funzionale con Inform.
