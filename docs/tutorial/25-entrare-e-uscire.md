# 25. Entrare e uscire dalla lanterna

Apri `examples/tutorial/25_dentro_fuori.locus` nello Studio e premi
**Compila e prova**. La storia parte sulla Terrazza, davanti alla camera della
lanterna.

```locus
La Terrazza è una stanza.
La Lanterna è una stanza.
La Terrazza racchiude la Lanterna.

Inizia nella "Terrazza".
```

## Prova guidata

1. Scrivi `dentro` oppure `in`: raggiungi la Lanterna.
2. Scrivi `x lente`: esamini lo scenario nella camera.
3. Scrivi `fuori`: torni sulla Terrazza.
4. Prova `out` dalla Terrazza: LOCUS spiega che non c'è un passaggio.
5. Apri **Mappa**: il collegamento puntinato mostra `dentro / fuori`.

Le forme `interno`, `inside`, `esterno` e `outside` sono equivalenti. `esci`
conserva invece il suo significato di conclusione della sessione; `entra` resta
disponibile per i veicoli e per le azioni definite dall'autore.

## Caso negativo

Queste frasi assegnano due destinazioni interne alla stessa Terrazza e producono
`E106`:

```text
La Terrazza racchiude la Lanterna.
La Terrazza racchiude il Magazzino.
```

LOCUS non sceglie silenziosamente fra due uscite con la stessa direzione.

## Esercizio

Aggiungi una porta fra Terrazza e Lanterna, inizialmente chiusa. Verifica che
`dentro` sia bloccato, apri la porta e riprova. Poi crea una regola che rimuove la
relazione `dentro` e osserva l'aggiornamento dell'atlante.

Il [riferimento dentro/fuori](../linguaggio/dentro-fuori.md) descrive alias,
semantica, porte, veicoli e relazioni dinamiche.
