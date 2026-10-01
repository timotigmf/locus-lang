# 35. Muoversi con frasi naturali

Apri `examples/tutorial/35_comandi_naturali_movimento.locus` nello Studio e
premi **Compila e prova**. La stessa uscita può essere percorsa con una forma
breve o con una frase più discorsiva.

```locus
La Banchina è una stanza.
La Lanterna è una stanza.
La Lanterna è a nord della Banchina.

Inizia nella "Banchina".
```

## Prova guidata

1. Scrivi `vai a nord`: raggiungi la Lanterna.
2. Scrivi `cammina verso sud`: torni alla Banchina.
3. Scrivi `go north`: funziona come il comando classico `nord`.
4. Scrivi `vai`: LOCUS chiede una direzione senza consumare un turno.
5. Scrivi `vai alla cambusa`: LOCUS spiega quali direzioni sono ammesse.

Il parser trasforma tutte le forme riuscite nello stesso intento direzionale.
Una storia non deve quindi duplicare stanze, relazioni o regole per accettare
uno stile di comando più naturale.

## Caso negativo

`vai a sottovento` non inventa una nuova direzione e non cerca un oggetto con
quel nome. La correzione elenca le famiglie disponibili e lascia invariata la
sessione.

## Esercizio

Aggiungi una Terrazza sopra la Lanterna. Raggiungila con `muoviti in alto` e
torna con `procedi giù`. Prova poi `dirigiti all'esterno` in un luogo privo di
un'uscita: la frase viene capita, ma il mondo risponde che da quella parte non
c'è alcun passaggio.

Il [riferimento sui comandi di movimento](../linguaggio/comandi-movimento.md)
elenca verbi, preposizioni, correzioni e limiti.
