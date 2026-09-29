# ADR 0026 — diagonali nella libreria narrativa e nell'atlante

Stato: accettato, 2026-09-29.

## Contesto

L'ADR 0009 ha introdotto le quattro direzioni cardinali e ha richiesto una nuova
decisione prima di ampliare il piano. Dungeon, città e paesaggi richiedono però
percorsi diagonali reali: simularli nel testo produce descrizioni incoerenti con
navigazione, porte, regole dinamiche e mappa.

## Decisione

La stdlib registra le coppie inverse `nordest`/`sudovest` e
`sudest`/`nordovest` come `RelationSpec` mutabili fra stanze. Il compilatore
generico non conosce queste direzioni e continua a ricevere il catalogo dal
dominio. La forma dell'IR non cambia: gli archi usano nuovi ID della stdlib.

Il parser del giocatore produce quattro intenti distinti e accetta forme
italiane, abbreviazioni classiche e nomi inglesi. Il runtime usa lo stesso
percorso transazionale delle direzioni cardinali; porte, veicoli e regole
dell'autore osservano quindi gli stessi vincoli.

Lo Studio esporta soltanto `nordest` e `sudest` come rappresentanti delle coppie
inverse. L'atlante assegna a queste linee spostamenti diagonali e mostra entrambe
le direzioni nell'etichetta.

## Alternative considerate

- Trattare le diagonali come sinonimi delle cardinali: scartato perché perderebbe
  identità spaziale e creerebbe falsi conflitti.
- Aggiungere solo i comandi: scartato perché un comando riconosciuto deve poter
  corrispondere a una relazione dichiarabile.
- Introdurre insieme alto, basso, dentro e fuori: rinviato perché richiede livelli
  nella mappa e la distinzione fra movimento e contenimento.
- Codificare le direzioni nel compilatore: scartato perché il core deve restare
  indipendente dalla narrativa interattiva.

## Conseguenze

Le storie esistenti e la versione IR 21 restano valide. `no` è riservato come
comando completo per nordovest, mentre dentro una frase continua a essere una
parola ordinaria. Le collisioni del layout restano risolte visivamente senza
modificare il grafo. Una futura estensione verticale dovrà specificare livelli,
etichette e interazione con `mondo.dentro` prima dell'implementazione.
