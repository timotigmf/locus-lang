# ADR 0023 — valuta tipata e acquisto atomico

Stato: accettato, 28 settembre 2026.

## Contesto

Una proprietà numerica chiamata `denaro` non distingue punti, peso e valuta e
non permette al runtime di verificare in modo uniforme un acquisto. Servono
identità della valuta, saldo, prezzo, possesso e una transazione che non lasci
stati intermedi quando i fondi sono insufficienti.

## Decisione

La stdlib introduce `mondo.valuta`, esposto nel sorgente come `valuta`, e
`mondo.merce`, esposto come `prodotto` e sottotipo trasportabile di `mondo.cosa`.
Le proprietà numeriche
standard `commercio.saldo` e `commercio.prezzo` conservano quantità intere. Una
storia IR 19 dichiara al massimo una valuta; ogni merce richiede un prezzo
strettamente positivo e il saldo non può essere negativo.

La sessione conserva gli ID delle merci acquistate. `compra` verifica in ordine
raggiungibilità, tipo, possesso precedente e fondi; soltanto dopo sposta la merce
nell'inventario, registra il possesso e diminuisce il saldo nello stesso nuovo
snapshot. `prendi` non permette di aggirare il prezzo, ma una merce acquistata,
lasciata e ripresa non viene pagata di nuovo.

`comprare` è un'azione standard tipata e partecipa alle regole. Il metacomando
`denaro` osserva il saldo senza far avanzare il tempo. Compilatore e IR restano
generici: tipi, proprietà e azioni sono forniti dalla stdlib.

## Alternative considerate

- Usare soltanto una proprietà numerica del giocatore: scartato perché perde
  unità, identità e ispezionabilità della valuta.
- Rappresentare ogni moneta come oggetto: rinviato; è utile per denaro fisico,
  ma non sostituisce quantità e pagamenti aggregati.
- Implementare subito venditori con due inventari: rinviato perché richiede
  possesso dei personaggi, scorte, incasso e regole di capacità.
- Accettare più valute con un unico `prezzo`: scartato perché il numero sarebbe
  ambiguo; servirà associare ogni prezzo a una valuta.

## Conseguenze

Gli acquisti falliti non cambiano saldo, posizione o possesso. Mappa, Indice del
mondo, regole e release web leggono le stesse proprietà dinamiche. Il primo
contratto non comprende vendita, resto fisico, più valute, credito negativo,
merci gratuite, scorte dei venditori o contrattazione.
