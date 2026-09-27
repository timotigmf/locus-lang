# ADR 0018 — elenchi tipati e mutazioni transazionali

Stato: accettato, 27 settembre 2026.

## Contesto

Indizi raccolti, memoria dei dialoghi, cronologie e inventari astratti richiedono
più valori omogenei. Modellare ogni elemento con una proprietà logica produce
schemi rigidi e non consente di conservare ordine o ripetizioni.

## Decisione

`Value` ammette tuple immutabili omogenee di testi, interi o valori logici. Tre
nuovi `ValueKind` distinguono gli elenchi e ogni proprietà autore di questo tipo
ha la tupla vuota come valore iniziale. Il parser aggiunge le dichiarazioni
`proprietà elenco di ...`, la condizione `contiene` e gli effetti `aggiungi` e
`rimuovi`.

Il lowering convalida il tipo di ogni elemento e conserva nell'IR un riferimento
di proprietà già risolto. Il runtime aggiunge in coda e rimuove la prima
occorrenza; costruisce sempre una nuova tupla. Il motore applica queste modifiche
nella transazione dell'azione e le annulla in caso di fallimento. L'IR sale alla
versione 14.

## Alternative considerate

- Liste non tipate: scartate perché sposterebbero errori dell'autore al runtime.
- Insiemi senza duplicati: scartati perché perderebbero ordine e conteggio delle
  ripetizioni; l'autore può ottenere unicità con `non ... contiene`.
- Letterali e assegnazione completa nel primo incremento: rinviati per non
  introdurre insieme delimitatori, inferenza e collezioni annidate.
- Tabelle trattate come liste di righe: rinviate perché colonne, chiavi e accesso
  richiedono un contratto specifico.

## Conseguenze

Il core resta indipendente dalla narrativa e dagli oggetti standard. Host e
validatori accettano un'unione di valori più ampia; cataloghi e IR controllano
l'omogeneità. La serializzazione JSON rappresenta le tuple come array, mentre i
confini Python rimangono immutabili. Indicizzazione, lunghezza, iterazione,
tabelle e interpolazione restano estensioni successive.
