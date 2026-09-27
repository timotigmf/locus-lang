# Linguaggio M2 — proprietà e mondo

Implementato in `0.2.0a1`; la sintassi M1 rimane disponibile. Tutte le parole
chiave sorgente e i comandi del giocatore sono italiani. API Python e campi IR
sono contratti tecnici interni, non parole del linguaggio autore.

## Proprietà

```locus
La Sala è una stanza.
La moneta è una cosa nella Sala.
Il valore è una proprietà numerica.
La rarità è una proprietà logica.
La provenienza è una proprietà testuale.
La moneta ha valore 12.
La moneta ha rarità vero.
La moneta ha provenienza "Antica zecca.".
```

`numerica` = intero con segno, default 0; `testuale` = stringa, default vuota;
`logica` = vero/falso, default falso. Niente conversione implicita (vero non è 1).
Dichiarazioni di proprietà e riferimenti possono seguire il loro utilizzo.
Proprietà autore applicabili a tutte le entità; duplicati e assegnazioni ripetute
sono errori, anche se identici. Ogni valore e schema sono presenti nell'IR.
Numeri limitati a 1000 cifre per letterale; decimali ed espressioni non implementati.

La stdlib offre `descrizione` testuale su tutti i tipi, `stato` su contenitori e
porte e, dall'IR 13, `visibile` logica su cose e scenari. I valori di stato sono esattamente "aperto", "chiuso", "bloccato";
il default è "chiuso". Un solo valore evita aperto e bloccato simultanei. La
visibilità predefinita è `vero`; la specifica estesa è in
[visibilità e scenario](visibilita-scenario.md).

## Contenitori, porte e chiavi

```locus
La Cucina è una stanza.
Il Corridoio è una stanza.
Il Corridoio è a nord della Cucina.
Lo scrigno è un contenitore nella Cucina.
La chiave è una chiave nello scrigno.
La porta rossa è una porta.
La porta rossa collega la Cucina al Corridoio.
La porta rossa ha stato "bloccato".
La chiave apre la porta rossa.
```

`apre` qui dichiara una relazione fra chiave e serratura: non apre la porta durante
la compilazione. Ogni chiave ha al massimo una destinazione M2; più chiavi possono
abilitare lo stesso oggetto. Un contenitore può essere bloccato con la stessa
semantica della porta. Le porte non sono oggetti trasportabili o collocabili.
Devono collegare due stanze distinte già collegate da una direzione; una sola
porta per coppia di stanze. I collegamenti direzionali sono nord/sud ed est/ovest,
con inverso generato automaticamente.

Una cosa, una chiave o un contenitore può essere dentro stanza o contenitore.
Si accettano `nella`, `nel`, `nello`, `nell'` e la forma tipografica dell'apostrofo.
Gli accordi di genere non sono ancora verificati. La posizione può anche essere
asserita separatamente: `La chiave è nello scrigno.`. Doppie posizioni e cicli,
anche indiretti, sono errori. Oggetti senza posizione restano fuori scena.

## Nomi quotati e stringhe

Nomi tra virgolette doppie consentono cifre, apostrofi e parole riservate:

```locus
La "sala della torre" è una stanza.
La "chiave 2" è una cosa nella "sala della torre".
La "chiave 2" ha descrizione "Un'incisione dice: \"nord\".".
```

Stringhe e nomi quotati accettano escape `\"`, `\\` e `\n`; un nome non può essere
vuoto né contenere un ritorno a capo. Stringhe sorgente su una sola riga fisica.
Le parole non quotate riservate comprendono è, ha, collega, le preposizioni di
collocazione/genitivo e i verbi registrati (nella stdlib: apre). I delimitatori
al/alla/allo/all'/a sono contestuali alla costruzione collega.

## Grammatica incrementale

```ebnf
proprieta = articolo nome "è" indefinito "proprietà" categoria "." ;
categoria = "numerica" | "testuale" | "logica" ;
assegnazione = articolo nome "ha" nome_proprieta valore "." ;
valore = intero | stringa | "vero" | "falso" ;
posizione = articolo nome "è" preposizione_in nome "." ;
collega = articolo nome "collega" articolo nome preposizione_a nome "." ;
relazione_verbale = articolo nome verbo_registrato articolo nome "." ;
```

`a` non articolata è seguita da articolo (`a la Sala`); preferire `alla Sala`.
La forma generica `è a predicato della entità` resta disponibile anche per
cataloghi non narrativi. La registrazione di verbi è un'API Python esplicita,
non ancora un sistema di moduli autore.

## Comandi giocatore

Oltre a M1: esamina, apri, chiudi, blocca … con …, metti … nel …, lascia.
Esempi: `apri scrigno`, `prendi chiave`, `apri porta rossa con chiave`,
`chiudi porta rossa`, `blocca porta rossa con chiave`, `metti chiave nello scrigno`.
Il nome completo ha priorità. Se non esiste una corrispondenza esatta, le parole
digitate possono identificare un solo oggetto raggiungibile: `prendi chiave`
seleziona `chiave di rame` quando è l'unica chiave nel campo d'azione. Più
corrispondenze producono una domanda con le alternative e non modificano lo stato.
Articoli iniziali opzionali; virgolette per nomi che contengono delimitatori.
Esempio: `metti "libro con note" nella scatola`.

Compatibilità comandi del giocatore: `l`/`look`, `x`/`examine`,
`i`/`inv`/`inventory`, `n`/`north`, `s`/`south`, `e`/`east`,
`o`/`w`/`west`, `q`/`quit`, `get`/`take` e le
forme inglesi di apri, chiudi, lascia, metti e blocca. Sono alias d'ingresso;
la sintassi autore, la narrazione e la documentazione restano italiane.

Usare una chiave richiede possesso e accessibilità. Una chiave in una borsa
trasportata ma chiusa non è utilizzabile. Metti richiede oggetto posseduto e
contenitore aperto. Contenitori trasportati mantengono i figli. Un fallimento non
muta la sessione. Chiudere non blocca automaticamente; aprire con la chiave corretta
sblocca e apre in un'unica transizione. Bloccare richiede oggetto già chiuso.

Apostrofi ASCII e tipografici sono equivalenti nel confronto dei nomi; la grafia
originale resta nella presentazione. Il parser giocatore accetta escape di virgolette
e backslash nei nomi quotati, ma non sequenze di escape arbitrarie.
