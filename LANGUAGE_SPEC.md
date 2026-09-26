# LOCUS — specifiche incrementali

## Stato attuale

Versione corrente `0.4.0a1`, IR versione 5. Le specifiche M2, M3 e M4
estendono e, dove indicato, sostituiscono i limiti M1 sotto.
La [specifica M2](docs/linguaggio/milestone-2.md) è normativa per proprietà,
stringhe, nomi quotati, preposizioni, contenitori, porte e chiavi.
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
`esci` termina la sessione. Maiuscole e spazi sono normalizzati; nomi esatti,
nessuna abbreviazione, clitico o pronome. Gli articoli iniziali di `prendi` sono opzionali.

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

## Estensione M3

La [specifica normativa M3](docs/linguaggio/milestone-3.md) aggiunge regole, condizioni
e azioni transazionali. IR corrente: versione 4; le versioni precedenti non sono accettate.

## Estensione M4

La [specifica normativa M4](docs/linguaggio/milestone-4.md) aggiunge inclusioni
da file e punto iniziale esplicito. IR corrente versione 5.
