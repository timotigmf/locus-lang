# Da Inform a LOCUS: concetti simili, contratti diversi

Questa scheda riguarda LOCUS 0.5.0a1 e le copie dei manuali elencate nel
[registro delle letture](../architettura/materiali-didattici.md). Non promette
compatibilità del sorgente o equivalenza del comportamento con Inform.

| Concetto incontrato nei manuali | In LOCUS oggi | Differenza da ricordare |
| --- | --- | --- |
| Modello del mondo | Entità, proprietà e relazioni | La prosa descrittiva non crea il modello |
| Luoghi e mappa | `stanza`, rosa dei venti, su/giù, dentro/fuori | Dodici direzioni con inverse e contenimento separato |
| Tipi e proprietà | Tipi dell'autore a ereditarietà singola; proprietà numeriche, testuali, logiche | Niente ereditarietà multipla o proprietà limitate a un tipo autore |
| Descrizione del luogo e oggetti visibili | `descrizione`, `visibile`, `scenario`, `guarda`, `esamina` | Niente supporter, trasparenza, luce o locale priorities |
| Controllo, modifica e resoconto | `verifica`, `esegui`, `dopo`, `descrivi` | Semantica propria, non traduzione diretta dei rulebook |
| Ordine delle regole | Priorità esplicita e ordine sorgente | Nessun ordinamento automatico per specificità |
| Regole instead | Fase `invece` | Termine normale gestisce l'azione e può proseguire in dopo/descrivi |
| Stop/fallimento | `interrompi` oppure `fallisci` | Il primo conserva gli effetti; il secondo annulla la transazione |
| Descrizioni condizionali | Regole che cambiano proprietà testuali | Niente interpolazione Inform con parentesi quadre |
| Oggetto dell'azione | Nomi quotati espliciti | Nessun equivalente parametrico generale di noun/second noun |
| Azioni dell'autore | `Azione` con comandi e zero, uno o due tipi | Forme iniziali e separatori fino a quattro parole; niente pattern liberi o argomenti facoltativi |
| Disambiguazione | Domanda persistente; risposta per numero, nome o sinonimo | Campo d'azione LOCUS e una sola posizione ambigua per volta |
| Pronomi | Referenti diretto e indiretto dell'ultima azione riuscita, clitici standard, `metticelo/a` e `mettici OGGETTO` | Singolare senza deduzione del genere |
| Clitico più complemento | `mettila nella scatola`, `aprilo con chiave` | Il complemento resta esplicito; niente referente locativo separato |
| Estensioni | Inclusione di file locali | Nessun package manager, namespace o formato di estensione Inform |
| Test e transcript | Copioni stdin, uscita attesa e pytest | Non esiste ancora una direttiva autore `Test ...` |
| Tracing | `locus debug` | Mostra le regole autore considerate, non tutte le operazioni interne |

Le regole di Inform descritte nei manuali sono ricche di eccezioni e ordinamenti.
Non sostituire semplicemente le parole inglesi con parole italiane: controlla
sempre la [specifica M3](../linguaggio/milestone-3.md). In particolare, una regola
più specifica scritta dopo una generale non ha automaticamente precedenza in LOCUS.

Il rollback di LOCUS è una scelta esplicita del suo motore: tutte le fasi e le
sostituzioni appartengono alla stessa transazione. Non viene dedotto da Inform.
