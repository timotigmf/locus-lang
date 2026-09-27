# LOCUS — specifiche incrementali

## Stato attuale

Versione corrente `0.5.0a1`, IR versione 14. Le specifiche M2, M3 e M4
estendono e, dove indicato, sostituiscono i limiti M1 sotto.
La [specifica M2](docs/linguaggio/milestone-2.md) è normativa per proprietà,
stringhe, nomi quotati, preposizioni, contenitori, porte e chiavi.
La stdlib corrente estende inoltre i collegamenti cardinali a nord/sud ed
est/ovest; le coppie inverse sono generate automaticamente.
La specifica di [metadati e vocabolario](docs/linguaggio/metadati-vocabolario.md)
definisce titolo, autore e sinonimi nominali dichiarati dall'autore.
La specifica dei [tipi definiti dall'autore](docs/linguaggio/tipi-autore.md)
definisce la gerarchia nominale a ereditarietà singola.
La specifica delle [azioni dell'autore](docs/linguaggio/azioni-autore.md)
definisce comandi con zero, uno o due oggetti tipati.
La specifica di [sinonimi e separatori](docs/linguaggio/grammatica-comandi-autore.md)
definisce più forme italiane per la stessa azione.
La specifica dei [comandi multiparola](docs/linguaggio/comandi-multiparola.md)
definisce locuzioni iniziali prive di collisioni di prefisso.
La specifica dei [separatori multiparola](docs/linguaggio/separatori-multiparola.md)
definisce locuzioni deterministiche fra i due oggetti.
La specifica delle [relazioni dinamiche](docs/linguaggio/relazioni-dinamiche.md)
definisce passaggi cardinali creati o rimossi da effetti transazionali.
La specifica di [visibilità e scenario](docs/linguaggio/visibilita-scenario.md)
definisce oggetti nascosti e dettagli ambientali non trasportabili.
La specifica degli [elenchi tipati](docs/linguaggio/liste-tipate.md) definisce
collezioni omogenee, appartenenza ed effetti transazionali.
Le sezioni S0/S1 seguenti descrivono il nucleo storico, non l'intera versione.

## Dichiarazioni (S0, mantenute in 0.1.0a2)

```ebnf
programma      = { dichiarazione } EOF ;
dichiarazione  = articolo nome "è" indefinito nome_tipo "." ;
articolo       = "il" | "lo" | "la" | "l'" ;
indefinito     = "un" | "uno" | "una" | "un'" ;
nome           = parola { parola } ;
nome_tipo      = parola { parola } ;
```

Keyword senza distinzione di maiuscole. `è`, `nella` e `della` sono riservate e delimitano i nomi.
`parola` inizia con una lettera Unicode e continua con lettere o segni combinanti;
apostrofi ASCII/tipografici sono token distinti e ammessi solo negli articoli.
Nomi composti come `chiave di ottone` sono ammessi; `sala d'armi`, numeri, trattini,
stringhe, commenti, plurali e altre costruzioni sono rinviati. Non si fanno
correzioni automatiche di accenti: `e` non sostituisce `è`.

Spazi, tab, LF e CRLF separano i token; righe non significative, punto obbligatorio.
Input UTF-8 senza BOM. Nessuna normalizzazione distruttiva del sorgente: NFC viene
applicato al confronto dei token, conservando gli offset originali. Programma
vuoto valido, mondo vuoto. Gli articoli sono accettati sintatticamente: non si
verifica ancora l'accordo e non ne viene dedotto il genere dell'entità.

La stdlib predefinita offre `stanza` e `cosa`. Un tipo sconosciuto è un errore
semantico. Dichiarazioni duplicate, anche con maiuscole o spazi diversi, sono errori.
Nessuna entità viene creata implicitamente. Nessuna posizione iniziale in S0.

```ita
La Cucina è una stanza.
Il Corridoio è una stanza.
La chiave di ottone è una cosa.
```

## Relazioni S1: implementate in 0.1.0a2

```ebnf
istruzione = dichiarazione | posizione_iniziale | collegamento ;
posizione_iniziale = articolo nome "è" indefinito nome_tipo "nella" nome "." ;
collegamento = articolo nome "è" "a" predicato "della" nome "." ;
predicato = parola { parola } ;
```

In S1 `nella` e `della` delimitano i nomi nei rispettivi contesti. Prima di
estendere a tutti gli articoli articolati, introdurre una produzione di sintagma
nominale con test sulle collisioni; non una catena di sostituzioni. La possibilità
di nomi quotati è aperta per evitare parole riservate ambigue.

```locus
La Cucina è una stanza.
Il Corridoio è una stanza.
Il Corridoio è a nord della Cucina.
La chiave è una cosa nella Cucina.
```

Semantica implementata: riferimenti in avanti permessi; collegamenti solo fra stanze;
reciproco sud generato dalla stdlib, conflitti diagnosticati; cosa contenuta in una
stanza; prima stanza dichiarata come inizio M1, da sostituire con una dichiarazione
esplicita prima di pubblicare il linguaggio. Nessuna creazione implicita del
Corridoio dal solo collegamento: l'esempio orientativo della visione va reso
esplicito per evitare errori di battitura che creano oggetti.

Comandi giocatore M1: `guarda`, `prendi [la] chiave`, `inventario`, `nord`, `sud`.
Il parser giocatore produce intenzioni tipate senza riusare questa grammatica.
Ambiguità, oggetto assente, oggetto già posseduto e uscita assente sono esiti distinti.
`esci` termina la sessione. Questa limitazione storica è sostituita dalla
[specifica M2 corrente](docs/linguaggio/milestone-2.md): sono disponibili alias
classici e nomi parziali non ambigui. Clitici e pronomi restano esclusi.

## Diagnostica M1

Codici stabili, messaggi italiani, sorgente/riga/colonna; arresto al primo errore.
`E001` carattere non ammesso; `E002` costruzione inattesa/incompleta;
`E101` nome duplicato; `E102` tipo sconosciuto; `E103` entità non dichiarata;
`E104` relazione sconosciuta; `E105` tipi incompatibili; `E106` destinazioni in
conflitto; `E107` relazione riflessiva vietata. Errori di catalogo sono errori API
(`ValueError`), non del sorgente. La CLI distingue uso scorretto (2),
compilazione/lettura fallita (1), successo (0).

Regole, verbi definiti dall'autore, proprietà, liste, tabelle, enumerazioni,
funzioni, costanti e moduli non appartengono a S0/S1. La loro grammatica richiederà
specifiche incrementali e casi negativi prima dell'implementazione.

## Contratto delle relazioni

Il parser riconosce predicati generici; la stdlib M1 registra soltanto `nord`,
`sud` e `nella`. Senza uno schema la relazione è errore E104. Tipi di estremità,
inversi e orientamento sono definiti dal catalogo passato al compilatore.

Ogni predicato ha al massimo una destinazione per soggetto. Ripetere lo stesso
collegamento è idempotente; dichiarare inversi coerenti è valido; due uscite
in conflitto, anche generate da inversi, sono rifiutate. Auto-collegamenti vietati.
`cosa nella stanza` non permette contenitori annidati: cicli di containment non
sono rappresentabili con i tipi M1. Oggetti non collocati compilano ma non sono
raggiungibili. Dopo `prendi`, l'oggetto è nell'inventario e non più nella stanza.
Compilare un mondo senza stanze è valido; `gioca` richiede almeno una stanza.

L'IR ha versione 2; versione 1 non accettata dal runtime. Nessun formato persistente
stabile. Gli ID dipendono dall'ordine delle dichiarazioni, non dall'ordine delle
relazioni; l'ordine di queste nell'IR segue le asserzioni sorgente e gli inversi.

## Diagnostica aggiunta in M2

E003 stringa/escape non valido; E004 intero troppo lungo; E108 ciclo di relazione;
E109 proprietà duplicata; E110 proprietà sconosciuta; E111 valore o destinatario
incompatibile; E112 assegnazione ripetuta; E201 vincolo narrativo (porta) non valido.
E201 punta alla dichiarazione della porta; gli altri errori conservano lo span
dell'istruzione interessata. Cataloghi API malformati producono ValueError.

E313 segnala un uso di `contiene`, `aggiungi` o `rimuovi` con una proprietà non
elenco o un elemento del tipo sbagliato.

## Estensione M3

La [specifica normativa M3](docs/linguaggio/milestone-3.md) aggiunge regole, condizioni
e azioni transazionali. IR corrente: versione 4; le versioni precedenti non sono accettate.

## Estensione M4

La [specifica normativa M4](docs/linguaggio/milestone-4.md) aggiunge inclusioni
da file e punto iniziale esplicito. IR corrente versione 5.

## Metadati e vocabolario

`Titolo: "…".` e `Autore: "…".` identificano la storia direttamente nel
sorgente. `Comprendi "alias" come "entità".` aggiunge un nome alternativo per i
comandi del giocatore. Metadati duplicati producono `E408`; alias in conflitto
producono `E409`. Questi campi sono stati introdotti con l'IR 6 e restano
presenti nell'IR 14.

## Tipi definiti dall'autore

`Un tesoro è un tipo di cosa.` introduce un tipo nominale. I riferimenti in
avanti sono ammessi e ogni tipo ha al massimo un genitore. I sottotipi sono
compatibili con proprietà, relazioni e capacità degli antenati. Ridefinizioni
producono `E113`; cicli nella gerarchia producono `E114`. La specifica completa
è in [tipi definiti dall'autore](docs/linguaggio/tipi-autore.md). La tabella dei
tipi è stata introdotta nell'IR 7 e resta presente nell'IR 14.

## Azioni e comandi definiti dall'autore

`Azione "salutare" su una persona con comando "saluta".` registra un'azione
tipata invocabile dal giocatore e dalle regole. Le forme con zero e due oggetti
sono descritte nella [specifica delle azioni](docs/linguaggio/azioni-autore.md).
Nomi duplicati producono `E310`; comandi non validi o in conflitto producono
`E311`. `e sinonimo "riverisci"` aggiunge una forma equivalente; più clausole
`e separatore` definiscono le locuzioni fra gli oggetti di un'azione a due
oggetti. Comandi e separatori possono contenere fino a quattro parole e non
possono avere prefissi ambigui. L'IR corrente è la versione 14.

## Relazioni dinamiche

Le regole possono usare `crea relazione "nord" da "Sala" a "Cripta";` e
`rimuovi relazione ...;` per modificare i collegamenti cardinali. Il compilatore
risolve gli ID, controlla tipi e mutabilità e incorpora le inverse nello stesso
effetto. Il runtime applica il cambiamento nella transazione della regola. Gli
usi non validi producono `E312`; si veda la
[specifica completa](docs/linguaggio/relazioni-dinamiche.md). Questa estensione
introduce l'IR 12 ed è conservata nell'IR 14.

## Visibilità e scenario

La proprietà standard `visibile` controlla se cose, contenitori, chiavi e
scenari entrano nel campo d'azione del giocatore. Il nuovo tipo `scenario` è
collocabile ed esaminabile, ma non trasportabile. Le regole cambiano la visibilità
con `imposta`; il rollback resta quello degli altri effetti. La
[specifica completa](docs/linguaggio/visibilita-scenario.md) introduce l'IR 13.

## Elenchi tipati

`La indizi è una proprietà elenco di testi.` dichiara una collezione omogenea
inizialmente vuota. Sono disponibili anche elenchi di numeri e di logici. Le
regole usano `aggiungi VALORE a "proprietà" di "entità"`, `rimuovi VALORE da
...` e la condizione `"proprietà" di "entità" contiene VALORE`. Il compilatore
controlla il tipo dell'elemento; le mutazioni rispettano il rollback dell'azione.
La [specifica completa](docs/linguaggio/liste-tipate.md) introduce l'IR 14.
