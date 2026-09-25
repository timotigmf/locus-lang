# Reference M1 — 0.1.0a2

## CLI

`locus COMANDO FILE` oppure `python -m locus COMANDO FILE`.
`-h`/`--help` mostra l'aiuto italiano.

| Comando | Comportamento |
| --- | --- |
| controlla | valida entità e relazioni; stampa numero di entità |
| ast | JSON AST senza validazione semantica |
| ir / compila | JSON IR versione 2, dopo validazione |
| gioca | compila e avvia la sessione IF dalla prima stanza dichiarata |

`gioca`: guarda, prendi [articolo] nome, inventario, nord, sud, esci.
EOF termina senza errore, Ctrl-C termina con codice 130. Prompt soltanto su TTY,
quindi si possono fornire comandi da stdin per script e transcript.
Codici: 0 successo, 1 sorgente/file/avvio non valido, 2 invocazione errata.
Diagnosi su stderr; nessuna scrittura implicita. Dump non caricabili come giochi.

## API Python

- `lexer.tokenize(text, source='<memoria>')`: tuple Token con span originali e EOF.
- `parser.parse(text, source='<memoria>')`: AST Program con declarations e relations.
- `compiler.compile_source(text, kinds, source='<memoria>', *, relations=None)`: ProgramIR.
- `compiler.analyze(program, kinds, *, relations=None)`: due passaggi e lowering.
- `schema.RelationSpec(id, source_type, target_type, reverse_operands=False, inverse_id=None)`:
  contratto funzionale e irriflessivo di una relazione; tipi/ID già risolti.
- `stdlib.default_kinds()` / `stdlib.default_relations()`: cataloghi nuovi e sostituibili.
- `runtime.instantiate(program)`: World immutabile con entità e relazioni.
- `player.parse_command(text)`: Intent(verb, noun=None); verb sconosciuto = unknown.
- `stdlib.game.start(world)`: Session; ValueError se mancano stanze.
- `stdlib.game.visible(session)`: ID degli oggetti nella stanza e non posseduti.
- `stdlib.game.step(session, intent)`: Transition(session, event), senza I/O.
- `stdlib.render.render(transition)`: testo italiano di un evento.
- `diagnostics.CompileError`: code, message, span; `canonical(text)`: NFC/casefold/spazi.

Tutti i nomi sopra sono sotto `locus`. Program, Declaration, Relation, EntityIR,
RelationIR, ProgramIR, Entity, World, Intent, Session, Event e Transition sono
dataclass immutabili. Session e World costruite manualmente dal chiamante devono
avere riferimenti coerenti; non sono un'API di caricamento di dati non fidati.

Cataloghi con nomi non canonici, ID vuoti/duplicati, tipi sconosciuti o inversi
incompatibili sollevano ValueError. `relations=None` supporta dichiarazioni senza
relazioni; l'API non importa implicitamente la stdlib. instantiate verifica versione,
ID duplicati, riferimenti inesistenti e conflitti funzionali, non sostituisce un
futuro loader validante. Niente pickle o eval.

Event.kind distingue look, inventory, taken, already_carried, not_here,
not_portable, ambiguous, no_exit, unknown, quit. Event.entities contiene ID,
mai frasi da reinterpretare. La sessione è pura: il chiamante adotta la nuova
sessione solo dopo step; la precedente rimane invariata.
