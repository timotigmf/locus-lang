# Analisi architetturale del repository Inform 7

Data dell'analisi: 27 settembre 2026. Fonte primaria:
[`ganelson/inform`](https://github.com/ganelson/inform), revisione
[`5c7ba42b74db69b93b1290453c65189fa60cfc67`](https://github.com/ganelson/inform/tree/5c7ba42b74db69b93b1290453c65189fa60cfc67/inform7).

Scopo: ricavare principi verificabili per LOCUS. Questa non è una traduzione di
Inform, una promessa di compatibilità o un'importazione del suo codice. Non è
stato copiato alcun frammento. Il repository principale usa Artistic License
2.0; alcune risorse incorporate dichiarano licenze proprie. Prima di qualsiasi
futuro riuso letterale occorrerà registrare file, copyright, licenza e modifiche.

## Perimetro esaminato

Il checkout selettivo comprende `inform7`, `resources/Documentation`, `docs` e
`notes`. L'inventario osservato alla revisione indicata contiene:

- 4.254 file sotto `inform7`, per circa 44 MB nel checkout;
- 3.647 file sotto `inform7/Tests`;
- 953 esempi sotto `resources/Documentation/Examples`;
- 25.972 righe in *Writing with Inform*;
- 2.437 righe in *The Recipe Book*.

Sono stati letti gli indici dei moduli e campioni mirati relativi a passaggi di
compilazione, risoluzione dei nomi, modello del mondo, valori e condizioni,
diagnostica, spazio, regioni, scene, punteggio, azioni, grammatica dei comandi,
dialogo, generazione runtime e test. L'inventario copre tutto il sottoprogetto;
non afferma una revisione riga per riga delle migliaia di file.

## Struttura da cui LOCUS può imparare

| Area Inform | Responsabilità osservata | Applicazione originale in LOCUS |
| --- | --- | --- |
| `core-module` | regia della compilazione e messaggi di problema | pipeline esplicita e catalogo diagnostico italiano |
| `assertions-module` | dichiarazioni, asserzioni, regole, tabelle ed equazioni | passaggi separati per simboli, tipi, relazioni e regole |
| `knowledge-module` | fatti, proprietà, relazioni, inferenze e coerenza | grafo tipato con completamento e validazione a fasi |
| `values-module` | valori, descrizioni, condizioni e controllo dei tipi | espressioni tipate senza reinterpretazione testuale |
| `imperative-module` | blocchi, variabili, funzioni e invocazioni | linguaggio di effetti controllati per le regole |
| `if-module` | spazio, tempo, azioni, parser giocatore e dialogo | libreria narrativa separata dal compilatore generico |
| `runtime-module` | abbassamento verso risorse eseguibili | IR versionata e backend autonomi per browser e CLI |
| `multimedia-module` | figure, suoni e file | manifest di risorse con controlli, non path impliciti |
| `Tests` | corpus di regressione e casi di problema | test positivi, negativi, transcript e conformità |
| documentazione | manuale progressivo, ricettario e indice semantico | manuale italiano a due percorsi con esempi compilati |

Il principio principale è la separazione dei livelli. Le conoscenze specifiche
della narrativa interattiva non devono entrare nel parser o nel compilatore
generico. LOCUS conserva quindi i confini già fissati: parser autore e giocatore
separati, semantica strutturata, IR senza frasi da rileggere e runtime indipendente
dall'interfaccia dello Studio.

## Lezioni per il compilatore

Inform attraversa le dichiarazioni più volte: prima scopre nomi e strutture, poi
crea tipi e istanze, infine risolve proprietà e relazioni. LOCUS usa già una
risoluzione in due passaggi; l'estensione sicura è rendere esplicite queste fasi:

1. raccolta di metadati, tipi, proprietà, azioni, relazioni e nomi;
2. costruzione dei simboli e della gerarchia dei tipi;
3. risoluzione di riferimenti, valori e schemi;
4. completamento controllato del modello da parte della stdlib;
5. verifica di coerenza senza ulteriori mutazioni;
6. abbassamento verso IR e indici dello Studio.

Questo ordine permette riferimenti in avanti e diagnosi precise senza creare
entità per errore. Le estensioni non devono inserire testo da riparsare: devono
produrre nodi o fatti tipati attraverso API controllate.

La risoluzione dei nomi di Inform tiene conto del contesto e può gestire nomi
simili. Per LOCUS il passo utile non è imitare l'inglese libero, ma introdurre
scope deterministici, forme nominali italiane e candidati con una spiegazione del
motivo della scelta. Ogni ambiguità visibile deve restare un esito, non diventare
una scelta nascosta.

## Italiano e comprensione dei comandi

Il modello di grammatica dei comandi separa linee, token tipati, priorità e azione
risultante. LOCUS può generalizzare l'attuale `Comprendi` con costrutti italiani
strutturati, per esempio in una futura specifica:

```text
Comprendi "acquista [una cosa] da [una persona]" come comprare.
Comprendi "paga [una persona] con [una cosa]" come pagare.
```

La stringa non dovrà diventare una sostituzione testuale. Il compilatore dovrà
produrre una sequenza di token letterali e argomenti tipati, controllare numero e
tipi degli argomenti dell'azione, ordinare le forme con criteri documentati e
rifiutare collisioni non risolvibili.

La comprensione italiana richiede quattro livelli indipendenti:

1. normalizzazione ortografica non distruttiva;
2. lessico base con genere, numero e forme flesse;
3. vocabolario contestuale dichiarato dall'autore;
4. disambiguazione a più turni basata su visibilità, raggiungibilità e tipo.

Un dizionario generale può fornire candidati offline, ma non può decidere il
significato narrativo di parole polisemiche. Il nucleo deve restare riproducibile:
stessa storia e stesso comando devono produrre gli stessi candidati su ogni
piattaforma. Dizionari estesi saranno pacchetti versionati, mai servizi cloud
obbligatori.

## Modello del mondo e funzionalità richieste

L'ordine seguente costruisce fondamenta condivise invece di aggiungere eccezioni
per ogni singolo gioco.

### Dungeon, mappe e passaggi segreti

- regioni annidate distinte dal contenimento fisico;
- relazioni spaziali dinamiche con effetti transazionali;
- visibilità di luoghi, uscite e oggetti separata dalla loro esistenza;
- porte, scale, ponti e collegamenti a senso unico come entità o relazioni tipate;
- luce, oscurità e fonti luminose come calcolo di visibilità;
- mappa derivata dallo stato conosciuto dal giocatore oltre alla mappa d'autore.

Un passaggio segreto dovrà esistere nel modello ma avere uno stato di scoperta;
la regola di scoperta aggiornerà lo stato e renderà visibile il collegamento. Non
verrà simulato soltanto cambiando una descrizione.

### Oggetti complessi

- gerarchia di tipi definita dall'autore;
- parti, supporti, contenitori, indumenti e capacità;
- dispositivi accesi/spenti con azioni e proprietà condivise;
- componenti creati da uno schema di tipo, senza generare nuove frasi;
- proprietà calcolate e vincoli di compatibilità verificati dal compilatore.

### Persone e dialoghi

Inform tratta il dialogo come valori strutturati: battute, blocchi, scelte,
soggetti e condizioni. LOCUS IR 16 introduce il tipo standard `persona` e grafi
di dialogo compilati con:

- nodi e scelte con identità stabile;
- destinazioni risolte, cicli ammessi e nodi irraggiungibili rifiutati;
- stato multi-turno, conclusione esplicita e memoria dei nodi visitati;
- trace della battuta, del nodo e della scelta nello Studio.

Restano da aggiungere condizioni ed effetti sulle scelte, argomenti di
conversazione, conoscenze dei personaggi e più dialoghi selezionabili per la
stessa persona.

### Veicoli

LOCUS IR 18 introduce il tipo standard `veicolo`, le azioni di salita e discesa,
lo stato del mezzo guidato e lo spostamento atomico di conducente e veicolo.
Sottotipi, regole, mappa e Indice del mondo leggono lo stesso grafo di posizione.
Passeggeri, carico, capienza e destinazioni compatibili con strada, acqua o
rotaia restano estensioni successive del contratto.

### Denaro e commercio

LOCUS IR 19 introduce una valuta tipata, saldo, merci, prezzi e un registro del
possesso. `compra` verifica oggetto, prezzo e fondi, poi trasferisce denaro e
merce in un unico snapshot; un fallimento non modifica saldo o collocazione.
IR 20 aggiunge mercanti tipati, relazione di scorta, cassa e rivendita atomica;
la forma `compra ... da ...` non richiede riscritture del comando. Più valute,
cambio, quantità e capacità restano contratti successivi.

### Risorse multimediali

LOCUS IR 21 associa immagini e suoni locali alle entità mediante un manifest
tipato, con percorsi confinati, formati espliciti e testo alternativo. Studio e
release consumano gli stessi record e la release incorpora i file. Video,
risorse condizionali e controllo della riproduzione da regole restano futuri.

### Punti, tempo, scene ed enigmi

LOCUS IR 17 introduce un clock logico, scene con intervalli assoluti e un
registro che attribuisce ogni premio alla scena e al turno. Inizio, fine e punti
compaiono nel trace. Restano da aggiungere condizioni ed effetti delle scene,
ricorrenza e un massimo del punteggio dichiarato. Gli enigmi non richiedono una
categoria speciale: emergono da azioni, relazioni, condizioni, stato e regole
verificabili.

## Azioni e regole

LOCUS possiede già fasi e rollback. L'analisi conferma le prossime estensioni:

- azioni dichiarabili dall'autore con zero, uno o due argomenti tipati;
- argomenti con ruoli nominati invece di `nome` e `secondo nome` impliciti;
- visibilità, raggiungibilità e possesso come verifiche della stdlib;
- regole ordinate con criteri ispezionabili e risultato tipato;
- attività per operazioni estendibili che non sono comandi del giocatore;
- effetti su relazioni, liste e tabelle con validazione prima del commit;
- trace completo dalla grammatica del comando agli effetti applicati.

LOCUS non adotterà la precedenza di Inform per semplice imitazione. Ogni nuova
fase o criterio di specificità richiederà un ADR e casi in cui due regole
competono.

## Manuale e Studio

La documentazione di Inform combina un manuale progressivo e un ricettario per
problemi concreti. LOCUS seguirà lo stesso principio editoriale con contenuti
originali in italiano:

- **Imparare LOCUS**: corso lineare, una capacità per capitolo;
- **Ricettario**: dungeon, conversazioni, commercio, veicoli, enigmi e interfaccia;
- esempi interamente copiabili e compilati durante i test;
- indice distinto per sintassi dell'autore, comandi del giocatore, tipi, azioni,
  proprietà, relazioni e codici diagnostici;
- pagine di errore con spiegazione, esempio minimo errato e correzione;
- collegamenti dallo Studio alla sezione esatta e al relativo esempio.

Lo Studio dovrà derivare indici da IR: mondo, gerarchia dei tipi, relazioni,
azioni, regole, scene, dialoghi e vocabolario. Non dovrà ricostruirli analizzando
il testo sorgente in JavaScript.

## Strategia di test ricavata

Per ogni capacità LOCUS continuerà a richiedere specifica, esempio, caso positivo,
caso negativo e riferimento. Il corpus verrà esteso con:

- test di compilazione dei blocchi del manuale;
- transcript di soluzione e di tentativi errati;
- casi di collisione del vocabolario e disambiguazione a più turni;
- test di proprietà per grafi, containment e transazioni;
- test di conformità condivisi fra CLI, Studio e release;
- test di migrazione per IR, salvataggi e progetti;
- corpus italiano con accenti, apostrofi, genere, numero e forme irregolari.

Il numero di test di Inform è un'indicazione di ampiezza, non un obiettivo da
imitare. La misura utile è coprire ogni contratto pubblico e ogni regressione.

## Piano di adozione per LOCUS

| Ordine | Pacchetto | Risultato verificabile |
| --- | --- | --- |
| 1 | gerarchia di tipi e azioni autore | nuovi tipi e azioni tipate senza dipendenza IF nel core |
| 2 | grammatica italiana dei comandi | forme `Comprendi` con token tipati e ambiguità esplicite |
| 3 | relazioni dinamiche, visibilità e scenario implementati fino all'IR 13 | passaggio segreto reale, oggetto nascosto e mappa coerente con lo stato |
| 4 | elenchi e tabelle tipate con effetti implementati nell'IR 15 | indizi, cronologie e registri modificati transazionalmente |
| 5 | persone e dialoghi strutturati implementati nell'IR 16 | conversazione ramificata con trace e test dei nodi |
| 6 | scene, tempo e punteggio implementati nell'IR 17 | eventi temporali e premi registrati e riproducibili |
| 7 | veicoli implementati nell'IR 18 | movimento atomico di conducente e veicolo, con mappa aggiornata |
| 8 | valuta e acquisto implementati nell'IR 19 | pagamento atomico con unità, prezzo, fondi e possesso verificati |
| 9 | mercanti e vendita implementati nell'IR 20 | scorta, incasso, rivendita e insolvenza verificati nello stesso snapshot |
| 10 | risorse multimediali implementate nell'IR 21 | manifest validato ed export web autosufficiente |
| 11 | manuale e indici completi | corso e ricettario ricercabili con esempi sempre compilati |

Ogni pacchetto richiede una specifica e, se modifica i confini del sistema, un
ADR prima dell'implementazione. Le capacità verranno aggiunte in questo ordine
solo quando la precedente mantiene verdi CLI, Studio, release e test non-IF.

## Scelte esplicitamente escluse

- copiare sorgenti, esempi o testo del manuale Inform;
- tradurre parola per parola la grammatica inglese;
- incorporare l'intero compilatore o i suoi runtime;
- promettere compatibilità con estensioni, story file o progetti Inform;
- far dipendere il nucleo da servizi NLP o dizionari remoti;
- aggiungere una capacità solo nell'interfaccia senza semantica nell'IR.

Questi limiti consentono a LOCUS di apprendere dall'esperienza di Inform e
restare un linguaggio originale, italiano, deterministico e verificabile.
