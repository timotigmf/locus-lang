# Reference LOCUS — 0.5.0a1

## CLI

`locus COMANDO FILE` oppure `python -m locus COMANDO FILE`.
`-h`/`--help` mostra l'aiuto italiano.

| Comando | Comportamento |
| --- | --- |
| controlla | valida entità e relazioni; stampa numero di entità |
| ast | JSON AST senza validazione semantica |
| ir / compila | JSON IR versione 11, dopo validazione |
| gioca | compila e avvia la sessione IF dalla prima stanza dichiarata |

`gioca`: guarda, esamina, prendi, lascia, metti, apri, chiudi, blocca,
inventario, nord, sud, est, ovest, esci. Alias classici: l/look, x/examine,
i/inv/inventory, n/north, s/south, e/east, o/w/west, q/quit, get/take,
open, close, drop, put, lock.
I nomi parziali sono accettati soltanto quando identificano un solo oggetto
raggiungibile; altrimenti l'evento è `ambiguous` e contiene tutte le alternative.
EOF termina senza errore, Ctrl-C termina con codice 130. Prompt soltanto su TTY,
quindi si possono fornire comandi da stdin per script e transcript.
Codici: 0 successo, 1 sorgente/file/avvio non valido, 2 invocazione errata.
Diagnosi su stderr; nessuna scrittura implicita. Dump non caricabili come giochi.

## API Python

- `lexer.tokenize(text, source='<memoria>')`: tuple Token con span originali e EOF.
- `parser.parse(text, source='<memoria>')`: AST Program con tipi, entità, relazioni e regole.
- `compiler.compile_source(text, kinds, source='<memoria>', *, relations=None, properties=None, actions=None, kind_parents=None, reserved_commands=())`: ProgramIR.
- `compiler.analyze(program, kinds, *, relations=None, properties=None, actions=None, kind_parents=None, reserved_commands=())`: risoluzione a passaggi e lowering.
- `schema.RelationSpec(id, source_type, target_type, reverse_operands=False, inverse_id=None, acyclic=False, verb=None)`:
  contratto funzionale e irriflessivo di una relazione; tipi/ID già risolti.
- `stdlib.default_kinds()` / `stdlib.default_kind_parents()` / `stdlib.default_relations()` / `stdlib.default_properties()`: cataloghi nuovi e sostituibili.
- `runtime.instantiate(program)`: World immutabile con entità e relazioni.
- `player.parse_command(text, actions=())`: Intent(verb, noun=None, indirect=None); riceve le azioni compilate del mondo e usa `unknown` per un comando sconosciuto.
- `stdlib.game.start(world)`: Session; ValueError se mancano stanze.
- `stdlib.game.visible(session)`: ID degli oggetti nella stanza e non posseduti.
- `stdlib.game.step(session, intent)`: Transition(session, event), senza I/O.
- `stdlib.render.render(transition)`: testo italiano di un evento.
- `diagnostics.CompileError`: code, message, span; `canonical(text)`: NFC/casefold/spazi.

Tutti i nomi sopra sono sotto `locus`. Program, KindDeclaration,
ActionDeclaration, Declaration, Relation, TypeIR, ActionIR, EntityIR, RelationIR,
ProgramIR, Entity, World, Intent, Session, Event e Transition sono
dataclass immutabili. Session e World costruite manualmente dal chiamante devono
avere riferimenti coerenti; non sono un'API di caricamento di dati non fidati.

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
not_portable, ambiguous, no_exit, unknown, quit. Event.entities contiene ID,
mai frasi da reinterpretare. La sessione è pura: il chiamante adotta la nuova
sessione solo dopo step; la precedente rimane invariata.
Le azioni dell'autore aggiungono gli eventi `custom` e `wrong_kind`.

## API aggiunte M2

- `stdlib.authoring.compile_story(text, source='<memoria>')`: composizione ufficiale
  della stdlib con validazione della topologia narrativa; usata dalla CLI.
- `schema.PropertySpec(id, owner_types, value_kind, default, choices=())`: schema
  immutabile; accepts verifica tipo esatto e appartenenza alle scelte.
- `schema.Value`: str | int | bool; `ValueKind`: numero/testo/logico.
- `schema.type_ids` normalizza singolo tipo/tupla; `valid_value` verifica tipi esatti.
- `compiler.relation_verbs(catalog)`: mappa verbo → predicato per `parser.parse(..., verbs=...)`.
- `graph.cycle_node(parents)`: rileva un ciclo in un grafo funzionale senza ricorsione.
- `stdlib.game.reachable(session, id)` e `carried(session, id)`: controlli distinti.
- `stdlib.validation.validate_world(world, inventory=())`: invarianti narrative;
  `WorldError` ha entity_id e messaggio italiano. property_value legge un valore/default.

AST aggiunge PropertyDeclaration e Assignment. ProgramIR/World aggiungono
property_specs e properties (tuple di PropertySpec e PropertyIR). Il parser produce
valori già decodificati, non stringhe da valutare. runtime.instantiate rifiuta
riferimenti di proprietà mancanti, duplicati e valori fuori tipo.

Event.kind aggiunge opened, closed, locked, already_open, already_closed,
already_locked, not_openable, wrong_key, not_carried, container_closed,
door_closed, not_container, cycle, put, dropped, examined, must_close, lock_success.
`locked` è un fallimento, `lock_success` una transizione riuscita.

Verbi e cataloghi Python restano espliciti: l'API core senza stdlib non assume
stanze, chiavi o significato di un predicato. Il programma autore, i comandi e le
diagnosi sono in italiano; nomi Python e campi dei dump sono contratti tecnici.
