# Prima storia giocabile

Per il percorso completo, gli esempi copiabili e l'indice per argomento, apri il
[Manuale dell'autore](guida-autore.md).

Salvare come `storia.locus` in UTF-8 senza BOM:

```locus
Titolo: "La prima storia".
Autore: "Il tuo nome".

La Cucina è una stanza.
Il Corridoio è una stanza.
Il Corridoio è a nord della Cucina.
La chiave è una cosa nella Cucina.
```

Eseguire `locus gioca storia.locus`. Una copia è in `examples/prima_storia.locus`.
La prima stanza dichiarata è l'inizio; la posizione nord genera automaticamente
l'uscita sud nel senso opposto. Allo stesso modo, est genera ovest. Nomi e
riferimenti possono precedere le dichiarazioni. Nel gioco puoi abbreviare le
direzioni con `n`, `s`, `e`, `o`; è accettato anche `w` per ovest. Le storie
possono inoltre dichiarare diagonali, livelli e passaggi `dentro`/`fuori`.

```text
Cucina
Vedi: chiave.
> prendi la chiave
Hai preso: chiave.
> inventario
Inventario: chiave.
> nord
Corridoio
Vedi: nessun oggetto.
> sud
Cucina
Vedi: nessun oggetto.
> esci
A presto.
```

`guarda` ripete la descrizione; prendere due volte non duplica l'oggetto; un'uscita
inesistente lascia invariata la posizione. Oggetti in un'altra stanza non sono
raggiungibili. Gli oggetti privi di collocazione compilano ma non sono visibili.
`locus ast` e `locus ir` consentono di ispezionare la compilazione.
Il transcript di soluzione è verificato automaticamente da test di sessione e CLI.

## Porte e contenitori

Avviare `locus gioca examples/porte_e_contenitori.locus`. Lo scrigno è chiuso:
aprirlo rende accessibile la chiave. Dopo averla presa, `apri porta rossa con
chiave di ottone` permette di andare a nord. La chiave di ferro non apre quella
porta. `esamina scrigno` mostra descrizione, stato e contenuto accessibile.

`metti chiave di ottone nello scrigno` richiede lo scrigno aperto; chiuderlo rende
la chiave inaccessibile. Vedi [sintassi e limiti M2](../linguaggio/milestone-2.md).

## Percorso guidato

Per iniziare da zero, segui le [trentadue lezioni del faro](../tutorial/README.md),
con prove di gioco e soluzioni.
La [quinta lezione](../tutorial/05-comandi-e-nomi.md) presenta le abbreviazioni
classiche delle avventure testuali e spiega quando un nome parziale è sufficiente.
La [sesta lezione](../tutorial/06-sotterraneo-enigma-punti.md) costruisce un
sotterraneo con enigma, sinonimi e punteggio.
La [settima lezione](../tutorial/07-tipi-autore.md) introduce categorie proprie
che ereditano il comportamento di stanza, cosa, contenitore e chiave.
L'[ottava lezione](../tutorial/08-azioni-autore.md) crea verbi italiani con
argomenti tipati e comportamento definito dalle regole.
La [nona lezione](../tutorial/09-sinonimi-azioni.md) assegna più forme e
preposizioni italiane alla stessa azione senza perdere il controllo statico.
La [decima lezione](../tutorial/10-comandi-multiparola.md) introduce forme come
`fai silenzio` e `porta in vista` con collisioni di prefisso diagnosticate.
L'[undicesima lezione](../tutorial/11-separatori-multiparola.md) collega due
oggetti con locuzioni come `in cambio di` e `a proposito di`.
La [dodicesima lezione](../tutorial/12-passaggi-segreti.md) crea e richiude un
varco, con navigazione e mappa aggiornate durante la partita.
La [tredicesima lezione](../tutorial/13-visibilita-scenario.md) distingue dettagli
ambientali, oggetti nascosti e cose trasportabili.
La [quattordicesima lezione](../tutorial/14-elenchi-indizi.md) usa un elenco
tipato come taccuino; la [quindicesima](../tutorial/15-tabelle-reperti.md) crea
un registro a colonne. La [sedicesima](../tutorial/16-dialogo-guardiana.md)
introduce persone e conversazioni ramificate con scelte numerate.
La [diciassettesima](../tutorial/17-tempesta-e-punteggio.md) pianifica una
tempesta a turni e registra il premio della sua conclusione.
La [diciottesima](../tutorial/18-bicicletta-in-movimento.md) introduce veicoli,
salita, discesa e movimento del mezzo insieme al conducente.
La [diciannovesima](../tutorial/19-il-mercato-del-faro.md) introduce valuta,
prezzi e acquisti che aggiornano saldo e inventario atomicamente.
La [ventesima](../tutorial/20-la-bottegaia-del-faro.md) aggiunge mercanti, cassa,
scorte e rivendita atomica.
La [ventunesima](../tutorial/21-il-faro-multimediale.md) associa immagini e suoni
locali alle entità e li conserva nella release web.
La [ventiduesima](../tutorial/22-leggere-indice-del-mondo.md) usa ricerca ed
esportazione dell'Indice per controllare l'intero modello compilato.
La [ventitreesima](../tutorial/23-la-rosa-dei-venti.md) completa la mappa con le
quattro diagonali, le abbreviazioni classiche e le inverse automatiche.
La [ventiquattresima](../tutorial/24-i-tre-livelli-del-faro.md) collega terrazze,
sale e sotterranei con `sovrasta`, `su` e `giù`.
La [venticinquesima](../tutorial/25-entrare-e-uscire.md) collega esterni e interni
con `racchiude`, `dentro` e `fuori` senza confonderli con i contenitori.
La [ventiseiesima](../tutorial/26-scegliere-tra-oggetti.md) mostra come chiarire
un nome ambiguo con numero, frammento univoco o sinonimo.
La [ventisettesima](../tutorial/27-pronomi-e-clitici.md) riusa l'ultimo oggetto
diretto con pronomi e forme come `prendila` ed `esaminalo`.
La [ventottesima](../tutorial/28-clitici-con-complemento.md) conserva contenitore
o chiave in forme come `mettila nella scatola` e `aprilo con chiave`.
La [ventinovesima](../tutorial/29-clitici-doppi.md) mantiene separati oggetto e
destinazione per forme come `metticela`.
La [trentesima](../tutorial/30-clitico-locativo.md) sottintende soltanto la
destinazione in forme come `mettici il gettone`.
La [trentunesima](../tutorial/31-avverbi-locativi.md) usa `lì` e `là` per
richiamare la stessa destinazione dopo il verbo `metti`.
La [trentaduesima](../tutorial/32-pronomi-per-ruolo.md) distingue il referente
diretto dallo strumento in `aprilo con essa`.
