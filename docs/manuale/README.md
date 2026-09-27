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
direzioni con `n`, `s`, `e`, `o`; è accettato anche `w` per ovest.

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

Per iniziare da zero, segui le [tredici lezioni del faro](../tutorial/README.md),
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
