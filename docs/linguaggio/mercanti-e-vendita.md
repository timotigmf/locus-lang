# Mercanti, scorte e vendita

Stato: implementato nell'IR 20.

## Dichiarare un mercante

Un `mercante` è una persona collocabile e non trasportabile. `cassa` indica
quante unità della valuta globale può spendere o ha incassato:

```locus
La Bottega è una stanza.
Il credito portuale è una valuta.
Il credito portuale ha saldo 20.

La Ada è una mercante nella Bottega.
La Ada ha cassa 25.
```

Il saldo e la cassa non possono essere negativi. Una storia con mercanti deve
dichiarare la valuta unica già prevista da IR 19.

## Costruire la scorta

Ogni prodotto non posseduto deve avere un venditore e trovarsi direttamente
nella sua stessa stanza:

```locus
La Bottega è una stanza.
Il credito portuale è una valuta.
Il credito portuale ha saldo 20.
La Ada è una mercante nella Bottega.
La Ada ha cassa 25.
La bussola è un prodotto nella Bottega.
La bussola ha prezzo 7.
La bussola ha prezzo di rivendita 3.
La Ada vende la bussola.
```

`prezzo` è l'addebito al giocatore. `prezzo di rivendita` è il ricavo quando il
giocatore restituisce la merce a un mercante; zero significa che nessun mercante
la ricompra. Prezzo di acquisto e rivendita sono dichiarati separatamente: LOCUS
non inventa sconti o percentuali.

## Comprare e vendere

Sono equivalenti `compra bussola`, `compra bussola da Ada`, `acquista`, `buy` e
`purchase`. Se la frase indica un mercante diverso dal venditore, l'azione viene
rifiutata. Un acquisto riuscito:

1. verifica merce, venditore raggiungibile e fondi del giocatore;
2. rimuove la relazione di scorta;
3. trasferisce la merce all'inventario e registra il possesso;
4. sottrae il prezzo dal saldo e lo aggiunge alla cassa.

`vendi bussola a Ada`, `vendere bussola alla Ada` e `sell bussola to Ada`
eseguono il percorso inverso. Il mercante deve avere abbastanza cassa. Se nella
stanza c'è un solo mercante si può scrivere `vendi bussola`; con più mercanti
LOCUS chiede quale si intende.

Una vendita riuscita toglie la merce dall'inventario e dal registro del possesso,
la colloca nella stanza, la aggiunge alla scorta scelta, accredita il giocatore e
addebita la cassa. La merce può quindi essere ricomprata.

## Regole e rollback

`comprare` e `vendere` sono azioni standard a uno o due oggetti. Nelle regole il
secondo oggetto usa la forma generale `con`:

```locus
La Bottega è una stanza.
Il credito portuale è una valuta.
Il credito portuale ha saldo 20.
La Ada è una mercante nella Bottega.
La Ada ha cassa 25.
La bussola è un prodotto nella Bottega.
La bussola ha prezzo 7.
La bussola ha prezzo di rivendita 3.
La Ada vende la bussola.

Regola "ricevuta" per vendere "bussola" con "Ada" nella fase dopo:
    dì "Ada firma la ricevuta.";
Fine regola.
```

`cassa`, `prezzo` e `prezzo di rivendita` sono proprietà numeriche leggibili e
modificabili dalle regole. Se un effetto produce cassa negativa, scorta doppia,
merce posseduta ancora in vendita o collocazioni incompatibili, la transazione
viene annullata insieme a tutti gli altri effetti.

## Diagnostica e limiti

`E125` segnala mercanti senza valuta, casse o rivendite negative, merci senza
venditore e scorte in stanze incoerenti. Lo Studio collega la diagnosi a questa
pagina e mostra venditore, cassa, prezzi e posizione nell'Indice del mondo.

IR 20 conserva una sola valuta e una singola copia per entità. Quantità, cataloghi
che generano copie, più valute, cambio, credito, contrattazione, tasse e mercanti
itineranti richiedono incrementi successivi.

La [soluzione con due mercanti](../tutorial/20-la-bottegaia-del-faro.md)
verifica il trasferimento di una merce da una scorta all'altra tramite
acquisto e rivendita. Venditore sbagliato e cassa insufficiente non modificano
saldi o possesso; il prezzo di riacquisto resta quello dichiarato sul prodotto.
