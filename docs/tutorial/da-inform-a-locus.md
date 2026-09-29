# Da Inform a LOCUS: concetti simili, contratti diversi

Questa scheda riguarda LOCUS 0.5.0a1 e le copie dei manuali elencate nel
[registro delle letture](../architettura/materiali-didattici.md). Non promette
compatibilità del sorgente o equivalenza del comportamento con Inform.

| Concetto incontrato nei manuali | In LOCUS oggi | Differenza da ricordare |
| --- | --- | --- |
| Modello del mondo | Entità, proprietà e relazioni | La prosa descrittiva non crea il modello |
| Luoghi e mappa | `stanza`, rosa dei venti, su/giù | Dieci direzioni con inverse; dentro/fuori non sono ancora registrati |
| Tipi e proprietà | Tipi dell'autore a ereditarietà singola; proprietà numeriche, testuali, logiche | Niente ereditarietà multipla o proprietà limitate a un tipo autore |
| Descrizione del luogo e oggetti visibili | `descrizione`, `visibile`, `scenario`, `guarda`, `esamina` | Niente supporter, trasparenza, luce o locale priorities |
| Controllo, modifica e resoconto | `verifica`, `esegui`, `dopo`, `descrivi` | Semantica propria, non traduzione diretta dei rulebook |
| Ordine delle regole | Priorità esplicita e ordine sorgente | Nessun ordinamento automatico per specificità |
| Regole instead | Fase `invece` | Termine normale gestisce l'azione e può proseguire in dopo/descrivi |
| Stop/fallimento | `interrompi` oppure `fallisci` | Il primo conserva gli effetti; il secondo annulla la transazione |
| Descrizioni condizionali | Regole che cambiano proprietà testuali | Niente interpolazione Inform con parentesi quadre |
| Oggetto dell'azione | Nomi quotati espliciti | Nessun equivalente parametrico generale di noun/second noun |
| Azioni dell'autore | `Azione` con comandi e zero, uno o due tipi | Forme iniziali e separatori fino a quattro parole; niente pattern liberi o argomenti facoltativi |
| Estensioni | Inclusione di file locali | Nessun package manager, namespace o formato di estensione Inform |
| Test e transcript | Copioni stdin, uscita attesa e pytest | Non esiste ancora una direttiva autore `Test ...` |
| Tracing | `locus debug` | Mostra le regole autore considerate, non tutte le operazioni interne |

Le regole di Inform descritte nei manuali sono ricche di eccezioni e ordinamenti.
Non sostituire semplicemente le parole inglesi con parole italiane: controlla
sempre la [specifica M3](../linguaggio/milestone-3.md). In particolare, una regola
più specifica scritta dopo una generale non ha automaticamente precedenza in LOCUS.

Il rollback di LOCUS è una scelta esplicita del suo motore: tutte le fasi e le
sostituzioni appartengono alla stessa transazione. Non viene dedotto da Inform.
