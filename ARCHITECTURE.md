# Architettura tecnica

Stato: progetto della piattaforma; implementazione attuale: milestone M2, proprietà e mondo narrativo.
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
La stdlib fornisce `stanza`, `cosa`, containment e nord/sud, senza ereditarietà.
Un test compila tipi e relazioni non narrativi per verificare concretamente l'indipendenza del core.

| Livello | Responsabilità e contratto | Stato |
| --- | --- | --- |
| source / diagnostica | file, intervallo, codice stabile, testo italiano | implementato |
| lexer | token, originale, posizione; nessuna risoluzione di nomi | implementato |
| parser autore | grammatica → AST immutabile | dichiarazioni e relazioni |
| semantica | nomi canonici, tipi noti, duplicati, ID risolti | implementato |
| IR | programma immutabile senza articoli o sintassi | schema sperimentale 3 |
| mondo | istanze indipendenti dai nodi AST | istanziazione minima |
| regole | ordinamento, condizioni, esiti, tracing | solo progetto |
| runtime | transizioni, eventi e servizi deterministici | transizioni IF nella stdlib |
| parser giocatore | testo → intenzioni/candidati | comandi M1 separati |
| stdlib | tipi, relazioni, azioni, lessico del dominio | tipi, schemi, sessione e renderer |
| strumenti | CLI, dump, diagnostica | cinque comandi, incluso gioca |

## AST e modello semantico iniziali

`Program(declarations, relations)` contiene `Declaration(name, kind, span, location)`
e `Relation(subject, predicate, target, span)`. I nomi mantengono grafia e parole; l'AST non
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

`ProgramIR(version, entities, relations)` contiene `EntityIR(id, label, type_id)`
e `RelationIR(source_id, predicate_id, target_id)`; ID ordinali riproducibili per
lo stesso sorgente, non persistenti fra modifiche. Nessuna serializzazione di
oggetti Python o codice eseguibile. Il JSON è solo un dump.
Source map separata e loader validante sono rinviati: non congelare un ABI ora.

## Mondo e runtime previsti

Il mondo generale sarà un grafo tipato: EntityId, TypeId, PropertyId, RelationId.
Proprietà e relazioni avranno schemi, cardinalità e vincoli; containment sarà una
relazione aciclica con destinazione unica. Stanze, porte, regioni e direzioni
saranno vocabolario e vincoli della stdlib. Ereditarietà singola iniziale proposta;
tratti e composizione da valutare prima di ereditarietà multipla.

`World(entities, relations)` è uno snapshot immutabile iniziale. `stdlib.game`
implementa `Session(world, room_id, inventory)` e transizioni pure da intenti a
`Transition(session, event)`. `stdlib.render` traduce gli eventi in testo italiano.
Il giocatore è stato di sessione distinto dalle entità. La presa sposta logicamente
una cosa dalla sua collocazione iniziale all'inventario; l'IR non viene mutata.

Nessun print nel core. `player.parse_command` produce intenti senza usare lexer
o parser autore; la sessione controlla visibilità, tipo e possesso prima di una
transizione. Nessun rule engine M3: le azioni M1 restano esplicite e sostituibili.
Dettagli e limiti nell'[ADR 0004](docs/adr/0004-milestone-1.md).

Per replay: input semantici, seme casuale, clock logico, versione programma e
ordine eventi; niente clock reale o casualità globale nel core. Salvataggi
richiederanno schema validato, migrazioni e identità persistenti; niente pickle.
Mappa, albero, proprietà e debugger leggeranno viste del mondo senza mutarlo.

## Motore di regole proposto (M3, non implementato)

Rulebook distinti: prima, invece, verifica, esegui, dopo, descrivi. `quando` è
un trigger di evento; `ogni turno` una sottoscrizione al clock, non ulteriori
fasi della stessa azione. Il contratto di una regola includerà ID, provenienza,
priorità intera, condizione pura e corpo con effetti espliciti.

Ordine proposto: priorità decrescente, poi ordine di dichiarazione stabile;
nessuna euristica di specificità nascosta. Gli esiti saranno una somma tipata:
continua, interrompi, fallisci(motivo), sostituisci(intento), risultato(valore).
Verifica e condizioni non mutano lo stato; gli effetti della fase esegui saranno
validati e applicati in una transizione. Politica di rollback delle altre fasi
ancora aperta: da decidere prima di abilitarne effetti arbitrari.

Sostituzioni avranno limite di profondità e rilevamento cicli; eventi avranno coda
ordinata e budget per evitare loop. Trace per valutazione: regola, condizione,
esito, variazioni e azione causale. I test dovranno precisare se dopo/descrivi
si eseguono per azioni fallite o interrotte; proposta: solo in caso di successo,
con evento di fallimento separato. Questa proposta richiede un ADR M3.

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
`Transition` espone output, trace e risultato. IR corrente versione 4.
Vedere [ADR 0006](docs/adr/0006-regole.md).
