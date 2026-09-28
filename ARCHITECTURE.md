# Architettura tecnica

Stato: Studio M5 e linguaggio incrementale fino all'IR 19.
Le decisioni strutturali sono motivate negli [ADR](docs/adr/README.md).

## Pipeline e dipendenze

```text
UTF-8 → lexer → parser autore → AST → analisi semantica → IR
                                                        ↓
                                                modello del mondo
                                                        ↓
frontend → parser giocatore → intento → dispatcher → runtime / regole
                                                        ↓
                                                  eventi → renderer
```

La CLI è il punto di composizione: seleziona la stdlib e passa i cataloghi di tipi e relazioni
al compilatore. Il compilatore non importa la stdlib né il runtime. Il runtime
importa esclusivamente il contratto IR e i suoi modelli, mai il parser o l'AST.
La stdlib fornisce `stanza`, `cosa`, `scenario`, `persona`, `veicolo`, `valuta`,
`prodotto`, containment e quattro direzioni cardinali.
Il core gestisce una gerarchia nominale generica; la stdlib dichiara contenitore
e chiave come sottotipi di cosa.
Un test compila tipi e relazioni non narrativi per verificare concretamente l'indipendenza del core.

| Livello | Responsabilità e contratto | Stato |
| --- | --- | --- |
| source / diagnostica | file, intervallo, codice stabile, testo italiano | implementato |
| lexer | token, originale, posizione; nessuna risoluzione di nomi | implementato |
| parser autore | grammatica → AST immutabile | dichiarazioni, relazioni, regole, metadati e vocabolario |
| semantica | nomi canonici, tipi noti, duplicati, ID risolti | implementato |
| IR | programma immutabile senza articoli o sintassi | schema sperimentale 19 |
| mondo | istanze indipendenti dai nodi AST | snapshot validati e relazioni dinamiche |
| regole | ordinamento, condizioni, esiti, tracing | implementato con rollback |
| runtime | transizioni, eventi e servizi deterministici | transizioni IF nella stdlib |
| parser giocatore | testo → intenzioni/candidati | standard, abbreviazioni e azioni autore |
| stdlib | tipi, relazioni, azioni, lessico del dominio | tipi, schemi, sessione e renderer |
| strumenti | CLI, Studio web, dump e diagnostica | implementato |

## AST e modello semantico iniziali

`Program` contiene dichiarazioni, tipi, relazioni, regole, metadati e vocabolario;
fra i nodi di base restano `Declaration(name, kind, span, location)` e
`Relation(subject, predicate, target, span)`. I nomi mantengono grafia e parole; l'AST non
contiene oggetti runtime. `Span(source, start, end, line, column)` usa offset
Unicode originali, fine esclusiva e riga/colonna da 1. Tab = un carattere, non
una colonna visiva. L'intervallo della dichiarazione include il punto.

La semantica riceve `Mapping[str, str]` (nome normalizzato del tipo → ID).
Le chiavi devono essere canoniche, gli ID non vuoti e univoci. I nomi delle entità
sono confrontati dopo NFC, casefold e collasso degli spazi. Due dichiarazioni
omonime sono errore, anche se identiche: una dichiarazione non è un'affermazione
idempotente. Futuri scope/moduli qualificati risolveranno gli omonimi.

La semantica risolve in due passaggi: prima entità e tipi, poi relazioni e
riferimenti in avanti. Il catalogo `RelationSpec` definisce tipi agli estremi,
orientamento e inversi. Nessuna conoscenza di stanze o direzioni nel compilatore.
Conflitti funzionali, auto-collegamenti e riferimenti non risolti sono diagnosticati.

`ProgramIR` versione 19 contiene gerarchia dei tipi, azioni dell'autore, entità,
relazioni, proprietà, tabelle, dialoghi, scene, regole, punto iniziale, titolo,
autore e sinonimi risolti; i record di base sono
`TypeIR(id, label, parent_id)`, `ActionIR(id, label, commands, ..., separators)`,
`EntityIR(id, label, type_id)`
e `RelationIR(source_id, predicate_id, target_id)`. Gli effetti di relazione
contengono archi già risolti e l'eventuale inversa, applicati atomicamente dal runtime.
Gli ID sono ordinali riproducibili per
lo stesso sorgente, non persistenti fra modifiche. Nessuna serializzazione di
oggetti Python o codice eseguibile. Il JSON è solo un dump.
Source map separata e loader validante sono rinviati: non congelare un ABI ora.

## Mondo e runtime

Il mondo è un grafo tipato: EntityId, TypeId, PropertyId, RelationId.
Proprietà e relazioni hanno schemi, cardinalità e vincoli; containment è una
relazione aciclica con destinazione unica. Stanze, porte e direzioni sono
vocabolario e vincoli della stdlib. L'ereditarietà singola è implementata;
tratti e composizione vanno valutati prima dell'ereditarietà multipla.

`World(entities, relations)` è uno snapshot immutabile. `stdlib.game`
implementa `Session(world, room_id, inventory)` e transizioni pure da intenti a
`Transition(session, event)`. `stdlib.render` traduce gli eventi in testo italiano.
Il giocatore è stato di sessione distinto dalle entità. La presa sposta logicamente
una cosa dalla sua collocazione iniziale all'inventario. Proprietà, contenimento
e direzioni dinamiche producono un nuovo snapshot; l'IR iniziale non viene mutata.
La sessione conserva inoltre l'eventuale veicolo guidato. Una direzione riuscita
aggiorna atomicamente stanza del giocatore e relazione di posizione del mezzo.
Il registro delle merci acquistate distingue possesso e collocazione: comprare
aggiorna saldo, inventario e possesso in un solo snapshot; lasciare un bene non
annulla l'acquisto.

Nessun print nel core. `player.parse_command` produce intenti senza usare lexer
o parser autore; la sessione controlla visibilità, tipo e possesso prima di una
transizione. Le azioni della stdlib e dell'autore passano nel motore M3 quando
esistono regole applicabili. Dettagli e limiti negli ADR
[0004](docs/adr/0004-milestone-1.md), [0006](docs/adr/0006-regole.md) e
[0016](docs/adr/0016-relazioni-dinamiche.md).

Per replay: input semantici, seme casuale, clock logico, versione programma e
ordine eventi; niente clock reale o casualità globale nel core. Salvataggi
richiederanno schema validato, migrazioni e identità persistenti; niente pickle.
Mappa, albero, proprietà e debugger leggeranno viste del mondo senza mutarlo.

## Motore di regole M3

I rulebook sono distinti in prima, invece, verifica, esegui, dopo e descrivi.
Il contratto di una regola include ID, provenienza, priorità intera, condizione
pura e corpo con effetti espliciti. Le scene temporali IR 17 hanno un ciclo di
vita separato; effetti periodici `ogni turno` nel rulebook restano futuri.

L'ordine è priorità decrescente, poi ordine di dichiarazione stabile, senza
euristiche di specificità nascoste. Gli esiti formano una somma tipata:
continua, interrompi, fallisci(motivo), sostituisci(intento), risultato(valore).
Verifica e condizioni non mutano lo stato; gli effetti sono validati e applicati
nella transazione. Ogni fallimento ripristina lo snapshot ricevuto dall'azione.

Le sostituzioni hanno limite di profondità e rilevamento cicli. Il trace registra
regola, condizione ed esito. Le fasi dopo e descrivi sono eseguite soltanto dopo
un'azione riuscita. Eventi con coda e budget restano futuri.

## Moduli e strumenti futuri

Moduli espliciti con dipendenze acicliche, namespace, versioni e registrazioni
controllate. Prima estendere tipi, lessico e regole entro una grammatica stabile;
solo successivamente template sintattici con analisi delle collisioni. Nessun
caricamento automatico di plugin installati. Extension Python = codice fidato,
non sandbox: separare in futuro estensioni dichiarative e native.

L'API compilatore dovrà supportare diagnostica multipla e recupero per l'editor;
oggi interrompe al primo errore. AST/IR inspectabili sono il primo supporto a LSP,
non un'implementazione di LSP. `testa`, `esplora`, `debug`, `esporta`, `studio`,
solution tests e browser restano sulla roadmap.

## Decisioni costose da cambiare

Identità e scope dei nomi, numeri e coercizioni, ordine regole, persistenza,
confini degli effetti, ABI delle estensioni e grammatica pubblica comportano
costi di migrazione. Il parser Python, il backend di packaging e la struttura
interna dei file sono sostituibili. Nessuna promessa di compatibilità prima di
una release stabile; le modifiche semantiche vanno comunque documentate e testate.

[Struttura completa proposta](docs/architettura/repository.md).

## Implementazione M2 (sostituisce il modello di posizione M1)

`schema.PropertySpec` definisce dominio, proprietari ammessi, default e scelte;
`RelationSpec` accetta insiemi di tipi, vincolo aciclico e verbo facoltativo.
Il compilatore raccoglie entità e proprietà, risolve relazioni, verifica grafi e
valori; non importa la stdlib. `ProgramIR` versione 3 contiene schemi e valori.

`stdlib.authoring.compile_story` compone parsing, analisi e validazione narrativa.
`stdlib.validation` verifica la topologia delle porte; `graph.cycle_node` resta
una funzione generica senza dominio. `runtime.instantiate` valida gli ID e i
valori IR ma non sostituisce un loader per JSON non fidato.

Una sessione mantiene un World immutabile corrente: le transizioni ne creano
una nuova versione quando cambiano proprietà o containment. L'inventario contiene
solo oggetti direttamente posseduti; figli dei contenitori seguono la posizione
dei genitori. Nessun oggetto può risultare insieme contenuto e nell'inventario.
Raggiungibilità e possesso sono controlli distinti. La libreria verifica invarianti
dopo ogni transizione riuscita; un fallimento restituisce la sessione originale.

Il parser giocatore resta distinto dal lexer autore, incluse le sue virgolette.
I verbi apri/chiudi/metti/blocca sono azioni della stdlib, non codice eseguito dal
parser. Si consulti l'[ADR 0005](docs/adr/0005-proprieta-e-mondo.md) per le alternative.

## Implementazione M3

`rule_parser` produce AST, `rule_compiler` risolve e tipa i riferimenti; `rule_model`
contiene record immutabili generici. `rules.execute` esegue rulebook attraverso
un protocollo Host indipendente da IF. `stdlib.game` adatta sessioni e azioni;
`Transition` espone output, trace e risultato. Questi record furono introdotti
con l'IR 4 e sono conservati nell'IR 19.
Vedere [ADR 0006](docs/adr/0006-regole.md).

## Implementazione M4

`project.load_project` gestisce I/O e grafo delle inclusioni prima di `analyze`.
AST espanso con span originali e ordine dei file; IR 5 con `entry_id` opzionale.
La stdlib valida il tipo del punto iniziale. Vedere [ADR 0007](docs/adr/0007-progetti.md).

## Studio M5

`studio.Studio` è un adattatore JSON per progetti virtuali, compilazione e sessioni.
Il frontend in `web/` usa CodeMirror e un module worker Pyodide; il compilatore
e il runtime LOCUS sono gli stessi della CLI. Distribuzione statica ed export ZIP,
senza caricamento di IR non fidata. Vedere [ADR 0008](docs/adr/0008-studio-web.md).

## Direzioni cardinali

La stdlib registra nord/sud ed est/ovest come due coppie inverse; il compilatore
continua a vedere soltanto schemi di relazione generici. Il runtime seleziona
l'arco dall'intento tipato e lo Studio proietta le direzioni nella mappa senza
reinterpretare il testo narrativo. Vedere [ADR 0009](docs/adr/0009-direzioni-cardinali.md).

## Relazioni dinamiche

`RelationSpec.mutable` separa gli archi che una regola può cambiare da quelli
strutturali. Il lowering produce `RelationChange` con sorgente, predicato,
destinazione e inversa già risolti. L'host applica il cambiamento a un nuovo
`World`, controlla conflitti e invarianti e lascia al motore il rollback. La
mappa dello Studio proietta lo snapshot della sessione dopo ogni comando. Vedere
[ADR 0016](docs/adr/0016-relazioni-dinamiche.md).

## Visibilità e scenario

La stdlib registra `visibile` come proprietà logica tipata e `scenario` come
radice distinta da `cosa`. Il cammino di raggiungibilità consulta la proprietà
su entità e contenitori antenati; parser giocatore, descrizione e inventario
leggono lo stesso snapshot. Gli scenari possono essere collocati, descritti e
usati nei selettori delle regole, ma il controllo `PORTABLE` li esclude da
`prendere`. Vedere [ADR 0017](docs/adr/0017-visibilita-scenario.md).

## Elenchi tipati

Gli elenchi sono valori immutabili e omogenei dello schema delle proprietà. Il
compilatore risolve l'indirizzo e controlla il tipo dell'elemento prima di
produrre gli effetti `aggiungi` e `rimuovi`; il rulebook costruisce un nuovo
valore nella transazione corrente. `contiene` legge lo stesso snapshot e non
interpreta testo sorgente. Vedere [ADR 0018](docs/adr/0018-elenchi-tipati.md).

## Tabelle tipate

`TableIR` conserva colonne ordinate, tipi scalari e righe immutabili. Il
compilatore risolve i nomi di tabella e convalida ogni riga prima del rulebook;
l'host espone lettura e sostituzione strutturate dello snapshot. Lo Studio
proietta lo stato corrente senza ricostruire dati dal testo. Vedere
[ADR 0019](docs/adr/0019-tabelle-tipate.md).

## Persone e dialoghi

`DialogueIR` conserva partecipante, nodo iniziale, nodi e scelte con riferimenti
risolti. Il compilatore riceve dall'host i tipi ammessi, mentre il runtime
generico convalida struttura e raggiungibilità senza conoscere la narrativa.
La stdlib conserva nodo attivo e visite nella sessione e produce trace separato
dalle regole. Vedere [ADR 0020](docs/adr/0020-dialoghi-strutturati.md).

## Scene, tempo e punteggio

`SceneIR` conserva intervallo temporale, testi e premio. La sessione mantiene un
clock logico, gli ID delle scene attive e concluse e un registro immutabile dei
punti assegnati. Il trace temporale resta distinto da quello delle regole e dei
dialoghi. Vedere [ADR 0021](docs/adr/0021-scene-tempo-punteggio.md).

## Metadati e vocabolario

Titolo e autore appartengono al progetto compilato, non allo stato separato del
frontend. Gli alias nominali vengono risolti verso ID in compilazione e usati
dal dispatcher soltanto entro l'insieme raggiungibile. Questa struttura evita
riscritture testuali e mantiene separati parser autore e parser giocatore. Vedere
[ADR 0010](docs/adr/0010-metadati-e-vocabolario.md).

## Gerarchia dei tipi

Il parser produce dichiarazioni nominali separate dalle entità. L'analisi
semantica raccoglie i nomi, risolve i genitori in un secondo passaggio e registra
la gerarchia nell'IR 7. Schemi, regole, runtime e strumenti usano lo stesso
confronto transitivo. Vedere [ADR 0011](docs/adr/0011-gerarchia-tipi.md).

## Azioni definite dall'autore

Le dichiarazioni di azione vengono unite al catalogo `ActionSpec` dell'host dopo
la risoluzione dei tipi. L'IR 19 conserva forme di comando e separatori anche
multiparola, oltre ai tipi degli argomenti. Il parser giocatore riceve questo catalogo
compilato e produce ID di azione; il dispatcher usa le stesse fasi transazionali
delle azioni standard.
Vedere [ADR 0012](docs/adr/0012-azioni-autore.md) e
[ADR 0013](docs/adr/0013-forme-comando.md), oltre ad
[ADR 0014](docs/adr/0014-comandi-multiparola.md) e
[ADR 0015](docs/adr/0015-separatori-multiparola.md).
