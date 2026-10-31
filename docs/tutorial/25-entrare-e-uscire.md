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
`dentro` sia bloccato, apri la porta e riprova. Per sperimentare la rimozione dinamica del
collegamento, usa invece una variante senza porta: le stanze di una porta
devono restare collegate, secondo gli invarianti del mondo.

Il [riferimento dentro/fuori](../linguaggio/dentro-fuori.md) descrive alias,
semantica, porte, veicoli e relazioni dinamiche.

## Esercizio risolto: una porta sul percorso interno

Apri `examples/tutorial/25b_porta_interna.locus` oppure copia:

```locus
Titolo: "La porta della lanterna".
Autore: "Esempio LOCUS".

La Terrazza è una stanza.
La Lanterna è una stanza.
La Terrazza racchiude la Lanterna.
Inizia nella Terrazza.
Il portello è una porta.
Il portello collega la Terrazza alla Lanterna.
Il portello ha stato "chiuso".
Comprendi "porta" come "portello".
La lente è uno scenario nella Lanterna.
La lente ha descrizione "Gli anelli di vetro raccolgono la luce.".
```

| Comando | Risultato |
| --- | --- |
| `dentro` | Il portello chiuso impedisce di passare |
| `apri porta` | Apre il portello tramite il sinonimo |
| `in` | Entri nella Lanterna |
| `x lente` | Leggi la descrizione dello scenario |
| `chiudi porta` | Lo stesso portello viene chiuso dal lato interno |
| `fuori` | La porta chiusa impedisce anche il ritorno |
| `apri portello`, `out` | Torni sulla Terrazza |

Il portello è una sola entità, con uno stato condiviso dai due lati:
non dichiarare una seconda porta per il ritorno. `porta` funziona perché
il sorgente lo dichiara come sinonimo; il nome originale resta `portello`.

**Prova negativa.** Sulla Terrazza `x lente` non trova lo scenario della
stanza interna, neppure con la porta aperta. Un’uscita aperta permette il
movimento, non rende automaticamente raggiungibili gli oggetti di un’altra
stanza. `out` dalla Terrazza è una direzione valida senza passaggio.
