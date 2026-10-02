# ADR 0042 — aiuto contestuale in partita

Stato: accettato, 2026-10-02.

## Contesto

Il giocatore poteva scoprire i comandi soltanto provocando un errore oppure
consultando il manuale fuori dalla partita. Questo era particolarmente scomodo
nello Studio e nelle release web, dove una storia può aggiungere azioni proprie.

## Decisione

La stdlib riserva `aiuto`, `comandi`, `help` e `?` come alias dello stesso
metacomando `help`. Il comando non accetta argomenti, non attraversa il
rulebook e non fa avanzare il turno. La resa elenca il nucleo comune e aggiunge
le categorie disponibili nel mondo corrente: dialoghi, scene, veicoli,
commercio e forme iniziali delle azioni dichiarate dall'autore.

L'aiuto resta disponibile durante un dialogo o un chiarimento e non li
interrompe. Il formato IR 21 non cambia: il catalogo contestuale deriva dal
`World` già compilato. Le forme alfabetiche sono riservate; `?` non appartiene
alla grammatica delle forme dichiarabili dall'autore.

## Alternative considerate

- Un testo fisso nello Studio: non avrebbe aiutato CLI e release esportate e
  non avrebbe potuto mostrare le azioni della storia.
- Argomenti come `aiuto movimento`: richiederebbero un catalogo di argomenti e
  nuove regole di navigazione; sono rinviati a un manuale in partita più ampio.
- Generare l'elenco dal testo sorgente: avrebbe duplicato il compilatore e
  violato il confine con il runtime.

## Conseguenze e verifica

Gli alias sono comandi standard riservati. Test di parser, runtime, collisione
autore, Studio, browser e tutorial verificano contenuto contestuale, assenza di
avanzamento temporale e rifiuto degli argomenti non supportati.
