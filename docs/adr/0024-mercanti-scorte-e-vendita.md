# ADR 0024 — mercanti, scorte e vendita atomica

Stato: accettato, 28 settembre 2026.

## Contesto

IR 19 può acquistare una merce direttamente dalla stanza, ma non identifica chi
la vende, chi incassa o chi può ricomprarla. Affidare questi significati ai nomi
degli oggetti o a testi delle regole impedirebbe al runtime di controllare scorte,
fondi e passaggi di proprietà.

## Decisione

La stdlib introduce `mondo.mercante`, esposto come `mercante` e sottotipo di
`persona`. La frase `La Ada vende la bussola.` produce la relazione mutabile
`commercio.vende` dalla merce al mercante. Questa direzione permette a un
mercante di offrire molte merci e assegna ogni merce a un solo venditore.

`commercio.cassa` registra i fondi del mercante nella valuta unica della storia;
`commercio.rivendita` registra quanto il giocatore riceve vendendo la merce. Un
valore di rivendita zero significa che il mercante non la ricompra.

`compra MERCE da MERCANTE` rimuove la merce dalla scorta, la trasferisce
all'inventario, registra il possesso, addebita il giocatore e accredita la cassa.
`vendi MERCE a MERCANTE` compie il percorso inverso. Oggetto, relazione di
scorta, proprietà e saldi cambiano nello stesso snapshot validato. Il nome del
mercante può essere omesso quando nella stanza ce n'è uno solo.

Le storie IR 19 senza mercanti conservano l'acquisto diretto. Quando esiste
almeno un mercante, ogni merce non posseduta deve appartenere a una scorta e
trovarsi direttamente nella stessa stanza del venditore. `E125` segnala violazioni
di questo contratto.

## Alternative considerate

- Contenere fisicamente le merci nel personaggio: scartato perché `persona` non
  è un contenitore e renderebbe ambiguo il campo d'azione.
- Usare una tabella autore per le scorte: scartato perché il runtime non potrebbe
  garantire posizione, unicità e passaggio di proprietà.
- Usare un unico saldo condiviso: scartato perché non rappresenta l'incasso né
  l'insolvenza del mercante.
- Calcolare sempre metà prezzo: scartato perché impone una politica economica
  non dichiarata e rende impossibili pegni, rarità e merci non ricomprate.

## Conseguenze

Mappa, Indice del mondo, regole e release web leggono la stessa relazione di
scorta e gli stessi saldi. IR 20 resta limitato a una valuta e non comprende
quantità impilate, più copie generate da un catalogo, contrattazione, credito,
tasse, cambio o mercanti itineranti.
