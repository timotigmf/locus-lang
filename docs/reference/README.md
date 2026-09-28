# Reference LOCUS — 0.5.0a1

## CLI

`locus COMANDO FILE` oppure `python -m locus COMANDO FILE`.
`-h`/`--help` mostra l'aiuto italiano.

| Comando | Comportamento |
| --- | --- |
| controlla | valida entità e relazioni; stampa numero di entità |
| ast | JSON AST senza validazione semantica |
| ir / compila | JSON IR versione 21, dopo validazione |
| gioca | compila e avvia la sessione IF dalla prima stanza dichiarata |

`gioca`: guarda, esamina, prendi, lascia, metti, apri, chiudi, blocca,
inventario, nord, sud, est, ovest, esci. Alias classici: l/look, x/examine,
i/inv/inventory, n/north, s/south, e/east, o/w/west, q/quit, get/take,
open, close, drop, put, lock.
Quando la storia contiene dialoghi sono disponibili anche `parla con persona`,
`p persona`, `talk to persona`, il numero della scelta, `scegli testo`, `basta`
e `fine dialogo`.
Quando la storia contiene scene sono disponibili `turno`/`tempo` e
`punteggio`/`score`; questi metacomandi non fanno avanzare il clock logico.
Quando contiene veicoli sono disponibili `sali`/`entra`, `scendi`, `esci da`,
`board`/`enter`, `exit` e `get out`; le direzioni spostano anche il mezzo guidato.
Quando contiene una valuta sono disponibili `compra`/`acquista`, `buy`/`purchase`
e i metacomandi `denaro`/`saldo`/`money`/`balance`. Con mercanti sono disponibili
anche `compra MERCE da MERCANTE`, `vendi`/`vendere MERCE a MERCANTE` e
`sell MERCE to MERCHANT`; il mercante può essere omesso se è l'unico raggiungibile.
I nomi parziali sono accettati soltanto quando identificano un solo oggetto
raggiungibile; altrimenti l'evento è `ambiguous` e contiene tutte le alternative.
EOF termina senza errore, Ctrl-C termina con codice 130. Prompt soltanto su TTY,
quindi si possono fornire comandi da stdin per script e transcript.
Codici: 0 successo, 1 sorgente/file/avvio non valido, 2 invocazione errata.
Diagnosi su stderr; nessuna scrittura implicita. Dump non caricabili come giochi.

## API Python

- `lexer.tokenize(text, source='<memoria>')`: tuple Token con span originali e EOF.
- `parser.parse(text, source='<memoria>')`: AST Program con tipi, entità, relazioni e regole.
- `compiler.compile_source(text, kinds, source='<memoria>', *, relations=None, properties=None, actions=None, kind_parents=None, reserved_commands=(), dialogue_actor_types=())`: ProgramIR.
- `compiler.analyze(program, kinds, *, relations=None, properties=None, actions=None, kind_parents=None, reserved_commands=(), dialogue_actor_types=())`: risoluzione a passaggi e lowering.
- `schema.RelationSpec(id, source_type, target_type, reverse_operands=False, inverse_id=None, acyclic=False, verb=None, mutable=False)`:
  contratto funzionale e irriflessivo di una relazione; tipi/ID già risolti.
- `stdlib.default_kinds()` / `stdlib.default_kind_parents()` / `stdlib.default_relations()` / `stdlib.default_properties()` / `stdlib.default_actions()`: cataloghi nuovi e sostituibili.
- `runtime.instantiate(program)`: World immutabile con entità e relazioni.
- `player.parse_command(text, actions=(), dialogue_enabled=False, scene_enabled=False, vehicle_enabled=False, commerce_enabled=False)`: Intent(verb, noun=None, indirect=None); riceve le azioni compilate del mondo, abilita esplicitamente conversazioni, metacomandi temporali, veicoli e commercio e usa `unknown` per un comando sconosciuto.
- `stdlib.game.start(world)`: Session; ValueError se mancano stanze.
- `stdlib.game.visible(session)`: ID delle entità percepibili nella stanza e non possedute; considera `visibile`, contenimento e stato dei contenitori.
- `stdlib.game.step(session, intent, advance_time=True)`: Transition(session, event), senza I/O; l'avvio passa `False` per non consumare un turno con la descrizione iniziale.
- `stdlib.render.render(transition)`: testo italiano di un evento.
- `diagnostics.CompileError`: code, message, span; `canonical(text)`: NFC/casefold/spazi.

Tutti i nomi sopra sono sotto `locus`. Program, KindDeclaration,
ActionDeclaration, Declaration, Relation, TypeIR, ActionIR, EntityIR, RelationIR,
ProgramIR, Entity, World, Intent, Session, Event e Transition sono
dataclass immutabili. Session e World costruite manualmente dal chiamante devono
avere riferimenti coerenti; non sono un'API di caricamento di dati non fidati.

`ProgramIR.dialogues` e `World.dialogues` contengono `DialogueIR`, composto da
`DialogueNodeIR` e `DialogueChoiceIR`. Tutti i riferimenti sono ID risolti. La
stdlib passa `mondo.persona` fra `dialogue_actor_types`; il core non assume il
significato narrativo di alcun tipo. `Session` conserva dialogo e nodo attivi e
l'insieme ordinato dei nodi visitati. `Transition.dialogue` espone il trace delle
battute e delle scelte senza ricostruire testo sorgente.

`ProgramIR.scenes` e `World.scenes` contengono `SceneIR` con intervallo, testi e
punti. `Session` conserva turno, scene attive/concluse, totale e `ScoreEntry`;
`Transition.scenes` espone `SceneStep` per inizio, fine e variazione del
punteggio. La conclusione di una scena registra il premio una sola volta.

La stdlib aggiunge `mondo.veicolo` come tipo radice non trasportabile.
`Session.vehicle_id` identifica il mezzo guidato; `validate_session` verifica che
mezzo e giocatore condividano la stanza. La posizione resta una relazione
`mondo.dentro`, quindi mappa e Indice del mondo leggono lo stesso snapshot.

La stdlib aggiunge `mondo.valuta`, `mondo.merce`, `commercio.saldo` e
`commercio.prezzo`. `Session.owned_ids` registra le merci acquistate anche dopo
che vengono lasciate; un acquisto riuscito aggiorna proprietà, inventario e
registro nello stesso snapshot. `validate_session` rifiuta merci non acquistate
in inventario e registri di possesso incoerenti.

IR 20 aggiunge `mondo.mercante`, `commercio.vende`, `commercio.cassa` e
`commercio.rivendita`. Acquisto e vendita trasferiscono atomicamente merce,
relazione di scorta, possesso, saldo e cassa. `validate_world` richiede che ogni
merce non posseduta di una storia con mercanti appartenga a una sola scorta e
condivida direttamente la stanza del venditore.

IR 21 aggiunge `ResourceIR` e `ProgramIR.resources`. La stdlib costruisce il
manifest dalle proprietà `immagine`, `suono` e `testo alternativo`; ogni record
contiene ID dell'entità, genere, percorso, MIME e alternativa testuale. La
compilazione da file verifica che la risorsa resti nella radice del progetto.

Cataloghi con nomi non canonici, ID vuoti/duplicati, tipi sconosciuti o inversi
incompatibili sollevano ValueError. `relations=None` supporta dichiarazioni senza
relazioni; l'API non importa implicitamente la stdlib. instantiate verifica versione,
ID duplicati, riferimenti inesistenti e conflitti funzionali, non sostituisce un
futuro loader validante. Niente pickle o eval.

`kind_parents` associa ID figlio a ID genitore o `None`; entrambi devono comparire
in `kinds`. La funzione generica `schema.is_subtype(actual, expected, parents)`
segue la catena senza ricorsione. `ProgramIR.types` e `World.types` contengono
`TypeIR(id, label, parent_id)`. `runtime.has_type` applica la stessa relazione al
mondo. Il compilatore rifiuta cataloghi ciclici con `ValueError`; il sorgente usa
`E113` per tipi duplicati ed `E114` per cicli dell'autore.

`schema.ActionSpec` accetta inoltre `target_types` e `indirect_types`. Le azioni
del sorgente vengono compilate in `ProgramIR.actions` e poi in `World.actions`.
`reserved_commands` è iniettato dall'host; la stdlib passa le forme riconosciute
dal parser standard. ID, tipi, forme di comando e separatori di ogni `ActionIR`
sono convalidati dal runtime. `ActionIR.commands` contiene la forma primaria e i
sinonimi, ciascuno da uno a quattro token; forme uguali o in rapporto di prefisso
sono rifiutate. `ActionIR.separators` contiene forme da uno a quattro token fra
i due oggetti; l'ultima preposizione ammette le varianti articolate e duplicati o
prefissi, anche dopo l'articolazione, sono rifiutati.
`E310` segnala nomi di azione duplicati; `E311` forme non valide, duplicate o in
conflitto.

Event.kind distingue look, inventory, taken, already_carried, not_here,
not_portable, ambiguous, no_exit, unknown, quit, boarded, disembarked, money,
purchased, sold e gli errori specifici di veicoli e commercio. Event.entities
contiene ID, mai frasi da reinterpretare. La sessione è pura: il chiamante adotta
la nuova sessione solo dopo step; la precedente rimane invariata.
Le azioni dell'autore aggiungono gli eventi `custom` e `wrong_kind`.

## API aggiunte M2

- `stdlib.authoring.compile_story(text, source='<memoria>')`: composizione ufficiale
  della stdlib con validazione della topologia narrativa; usata dalla CLI.
- `schema.PropertySpec(id, owner_types, value_kind, default, choices=())`: schema
  immutabile; accepts verifica tipo esatto e appartenenza alle scelte.
- `schema.Value`: str | int | bool oppure tupla omogenea di uno di questi tipi;
  `ValueKind`: numero/testo/logico ed elenco_testi/elenco_numeri/elenco_logici.
- `schema.type_ids` normalizza singolo tipo/tupla; `valid_value` verifica tipi esatti.
- `compiler.relation_verbs(catalog)`: mappa verbo → predicato per `parser.parse(..., verbs=...)`.
- `graph.cycle_node(parents)`: rileva un ciclo in un grafo funzionale senza ricorsione.
- `stdlib.game.reachable(session, id)` e `carried(session, id)`: controlli distinti;
  il primo rifiuta entità con `visibile` falso e discendenti di contenitori invisibili o chiusi.
- `stdlib.validation.validate_world(world, inventory=(), owned_ids=())`: invarianti narrative;
  `WorldError` ha entity_id, codice e messaggio italiano. `validate_session`
  controlla inoltre veicolo guidato, possesso delle merci e inventario;
  `property_value` legge un valore/default.

AST aggiunge PropertyDeclaration e Assignment. ProgramIR/World aggiungono
property_specs e properties (tuple di PropertySpec e PropertyIR). Il parser produce
valori già decodificati, non stringhe da valutare. runtime.instantiate rifiuta
riferimenti di proprietà mancanti, duplicati e valori fuori tipo.

Gli elenchi autore nascono vuoti. `PropertySpec.accepts_item` convalida un
elemento; `aggiungi` lo accoda, `rimuovi` elimina la prima occorrenza e
`contiene` verifica l'appartenenza. Gli effetti sulle collezioni partecipano al
rollback delle regole e sono vietati nella fase `verifica`.

`ProgramIR.tables` e `World.tables` contengono `TableIR`: ID, etichetta,
`TableColumnIR` ordinate e righe scalari immutabili. Le condizioni
`contiene_riga` e gli effetti `aggiungi_riga`/`rimuovi_riga` conservano ID e
valori già risolti. Il runtime ricontrolla schemi e riferimenti dell'IR.

Event.kind aggiunge opened, closed, locked, already_open, already_closed,
already_locked, not_openable, wrong_key, not_carried, container_closed,
door_closed, not_container, cycle, put, dropped, examined, must_close, lock_success.
`locked` è un fallimento, `lock_success` una transizione riuscita.

Verbi e cataloghi Python restano espliciti: l'API core senza stdlib non assume
stanze, chiavi o significato di un predicato. Il programma autore, i comandi e le
diagnosi sono in italiano; nomi Python e campi dei dump sono contratti tecnici.
