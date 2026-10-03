# M4 — progetti su più file e punto iniziale

Specifica normativa di LOCUS 0.4.0a1, aggiuntiva a M2/M3. IR versione 5.
La compilazione da file supporta due nuove direttive italiane:

```text
Includi "moduli/mondo.locus".
Includi "moduli/regole.locus".
Inizia nella "Atrio".
```

Il progetto completo è `examples/progetto.locus`. Per giocare:
`locus debug examples/progetto.locus`. Prova `prendi chiave`, `nord`, `sud`, `esci`.
Il Laboratorio è dichiarato prima dell'Atrio, ma la storia inizia nell'Atrio.

## Inclusioni

`Includi` richiede un percorso relativo quotato, terminato da punto. È risolto
rispetto alla cartella del file che contiene la direttiva, non alla cartella del
terminale. Separatore portabile `/`; ammessi spazi, Unicode, `.` e `..`.
Non sono ammessi percorsi assoluti, drive Windows, backslash, `:` o NUL.
Non vengono espansi URL, variabili d'ambiente o `~`. I file sono letti come UTF-8;
non vengono scaricati file dalla rete. Non è un sandbox dei percorsi: `..` e
symlink possono indirizzare file esterni alla cartella del progetto.

Si visitano le inclusioni nell'ordine in cui compaiono; ogni dipendenza viene
compilata prima del file che la include. La posizione della direttiva rispetto
alle altre dichiarazioni del file non cambia questa precedenza. All'interno
ciascun file conserva il proprio ordine. Una stessa destinazione canonica,
anche attraverso un symlink o `./`, è caricata una sola volta. Una dipendenza
condivisa da due moduli non duplica entità o regole. Gli hard link con percorsi
canonici diversi non sono deduplicati.

Le inclusioni cicliche sono errori, anche per file che non dichiarano entità.
Limiti predefiniti: 256 file distinti e 64 livelli, contando il file principale.
Le API permettono di restringere o aumentare i limiti; non è un limite di byte
né una garanzia per input ostile. La compilazione legge una sola volta ogni file
per invocazione, senza cache persistente o snapshot atomico del filesystem.

Tutti i file condividono un unico spazio dei nomi: i riferimenti in avanti
funzionano anche fra file, i nomi duplicati sono errori. Non esistono ancora
namespace, alias, visibilità privata, esportazioni o pacchetti versionati.
A parità di priorità, le regole delle dipendenze precedono quelle del chiamante.
Questa versione è composizione di sorgenti, non isolamento dei moduli.

## Punto iniziale

```locus
Il Deposito è una stanza.
La Sala è una stanza.
Inizia nella "Sala".
```

Il progetto può contenere al massimo una direttiva `Inizia`, anche se più
file indicano lo stesso luogo. Il nome è risolto dopo aver raccolto tutte le
entità. La libreria narrativa richiede una stanza. Se la direttiva manca, resta
il comportamento storico: prima stanza nell'ordine delle dichiarazioni espanse.

Nel nucleo generico l'ingresso è un ID di entità, senza tipi narrativi imposti:
la restrizione alla stanza appartiene alla stdlib. Nessuna azione viene eseguita
dalla compilazione; `gioca` e `debug` creano la sessione ed eseguono il primo guarda.

## API e diagnostica

- `parse(text)` riconosce direttive e produce AST senza leggere file.
- `load_project(Path(...), verbs=...)` legge e unisce gli AST; `source_order`
  elenca i percorsi canonici in ordine di compilazione. Le inclusioni sono risolte.
- `analyze` e `compile_source` restano senza I/O. Un'inclusione non risolta è E401.
- `compile_story_file(Path(...))` compone caricamento, compilazione e vincoli narrativi.
- `compile_story(text)` resta l'API per un sorgente autosufficiente, senza inclusioni.

Tutti i comandi CLI da file usano il progetto completo. `ast` mostra l'AST espanso
senza controlli semantici; `ir` e `compila` mostrano l'IR con ingresso risolto.
Gli span mantengono file, offset, riga e colonna originali, senza concatenare testi.
Il runtime non conosce percorsi né direttive e non apre file.

| Codice | Significato |
| --- | --- |
| E401 | Inclusioni passate direttamente al compilatore senza caricatore |
| E402 | File assente, illeggibile, non regolare o UTF-8 non valido |
| E403 | Ciclo di inclusioni, con catena dei percorsi |
| E404 | Percorso non relativo/portabile |
| E405 | Limite di file o profondità superato |
| E406 | Più di un punto iniziale |
| E407 | Punto iniziale non narrativamente valido |

File mancanti e cicli puntano alla direttiva responsabile; errori interni puntano
al sorgente incluso. E103 resta l'errore per un'entità iniziale non dichiarata.
Le normali diagnosi sintattiche E002 si applicano a direttive incomplete.

## Preposizioni del punto iniziale

La direttiva accetta `Inizia nella "Sala".`, `Inizia nel "Mercato".`,
`Inizia nello "Studio".` e `Inizia nell'"Atrio".`. L'apostrofo può essere
diritto o tipografico; il nome può essere quotato oppure seguire la sintassi dei nomi nelle dichiarazioni.
Le forme usano lo stesso punto iniziale nell'AST e nell'IR. Non viene
verificato l'accordo grammaticale con il nome. `in`, `al` e `nell` senza
apostrofo sono rifiutati con `E002`. Un secondo ingresso, anche espresso
con una preposizione diversa, resta un errore `E406`.

## Nomi non quotati

`Inizia nel Mercato Coperto.` equivale a `Inizia nel "Mercato Coperto".`.
Le parole del nome vengono raccolte fino al punto finale; i nomi con parole
riservate o apostrofi interni richiedono le virgolette, come nelle dichiarazioni.
Un nome assente produce `E103`; la mancanza del nome produce `E002`.
`Includi` conserva invece l'obbligo di un percorso fra virgolette.
