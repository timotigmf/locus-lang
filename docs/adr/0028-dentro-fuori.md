# ADR 0028 — navigazione dentro/fuori distinta dal contenimento

Stato: accettato, 2026-09-29.

## Contesto

Edifici, tende, grotte e stanze annidate richiedono i comandi direzionali
`dentro` e `fuori`. LOCUS possiede già `mondo.dentro`, ma quella relazione indica
la posizione di cose, persone e veicoli in una stanza o in un contenitore. Usarla
anche per collegare due luoghi confonderebbe posizione e navigazione, con
cardinalità e invarianti differenti.

## Decisione

La stdlib registra la coppia mutabile `dentro`/`fuori` con gli identificatori
distinti `mondo.interno` e `mondo.esterno`. Il verbo relazionale `racchiude`
permette la frase naturale `La Villa racchiude l'Atrio.`: il collegamento va
dalla Villa verso l'Atrio e l'inversa riporta all'esterno.

Il parser del giocatore produce gli intenti `inward` e `outward`. `dentro`,
`interno`, `in` e `inside` percorrono il primo; `fuori`, `esterno`, `out` e
`outside` percorrono il secondo. `esci` continua a terminare la partita. `Entra`
e `enter` restano disponibili per i veicoli o per azioni definite dall'autore,
così una nuova direzione non cambia il significato dei sorgenti esistenti.

Porte, veicoli e relazioni create dalle regole usano gli stessi controlli
transazionali delle altre direzioni. Lo Studio esporta un solo arco `dentro` e
lo disegna con una linea puntinata etichettata `dentro / fuori`. L'IR 21 non
cambia.

## Alternative considerate

- Riutilizzare `mondo.dentro`: scartato perché romperebbe il contratto del
  contenimento e la posizione univoca degli oggetti.
- Riservare anche `entra` alla direzione: scartato perché renderebbe incompatibili
  azioni dell'autore già valide e il comando per salire su un veicolo.
- Dedurre automaticamente l'interno dai nomi dei luoghi: scartato perché i nomi
  non codificano una topologia affidabile.

## Conseguenze

Il grafo distingue chiaramente collocazione e passaggi. Ogni stanza ha al
massimo una destinazione `dentro` e una `fuori`; collegamenti multipli richiedono
direzioni nominate diverse. I percorsi a senso unico e le regioni con più
entrate restano contratti successivi.
