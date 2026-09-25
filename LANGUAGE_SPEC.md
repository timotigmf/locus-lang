# Linguaggio 0.1 — bozza e sottoinsieme eseguibile

## S0: grammatica implementata in 0.1.0a1

```ebnf
programma      = { dichiarazione } EOF ;
dichiarazione  = articolo nome "è" indefinito nome_tipo "." ;
articolo       = "il" | "lo" | "la" | "l'" ;
indefinito     = "un" | "uno" | "una" | "un'" ;
nome           = parola { parola } ;
nome_tipo      = parola { parola } ;
```

Keyword senza distinzione di maiuscole. `è` è riservato e termina il nome.
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

## S1: grammatica minima proposta per il primo milestone (NON implementata)

```ebnf
istruzione = dichiarazione | posizione_iniziale | collegamento ;
posizione_iniziale = articolo nome "è" indefinito nome_tipo "nella" nome "." ;
collegamento = articolo nome "è" "a" direzione "della" nome "." ;
direzione = "nord" | "sud" ;
```

In S1 `nella` e `della` delimitano i nomi nei rispettivi contesti. Prima di
estendere a tutti gli articoli articolati, introdurre una produzione di sintagma
nominale con test sulle collisioni; non una catena di sostituzioni. La possibilità
di nomi quotati è aperta per evitare parole riservate ambigue.

```ita-proposta
La Cucina è una stanza.
Il Corridoio è una stanza.
Il Corridoio è a nord della Cucina.
La chiave è una cosa nella Cucina.
```

Semantica proposta: riferimenti in avanti permessi; collegamenti solo fra stanze;
reciproco sud generato dalla stdlib, conflitti diagnosticati; cosa contenuta in una
stanza; prima stanza dichiarata come inizio M1, da sostituire con una dichiarazione
esplicita prima di pubblicare il linguaggio. Nessuna creazione implicita del
Corridoio dal solo collegamento: l'esempio orientativo della visione va reso
esplicito per evitare errori di battitura che creano oggetti.

Comandi giocatore M1: `guarda`, `prendi [la] chiave`, `inventario`, `nord`, `sud`.
Il parser giocatore produrrà intenzioni tipate, senza riusare questa grammatica.
Ambiguità, oggetto assente e uscita assente dovranno essere esiti distinti.

## Diagnostica S0

Codici stabili, messaggi italiani, sorgente/riga/colonna; arresto al primo errore.
`E001` carattere non ammesso; `E002` costruzione inattesa/incompleta;
`E101` nome duplicato; `E102` tipo sconosciuto. Errori di catalogo sono errori API
(`ValueError`), non del sorgente. La CLI distingue uso scorretto (2),
compilazione/lettura fallita (1), successo (0).

Regole, verbi definiti dall'autore, proprietà, liste, tabelle, enumerazioni,
funzioni, costanti e moduli non appartengono a S0/S1. La loro grammatica richiederà
specifiche incrementali e casi negativi prima dell'implementazione.
