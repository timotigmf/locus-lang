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

## Esercizio risolto: la terrazza sopra la lanterna

Apri `examples/tutorial/35b_terrazza_della_lanterna.locus` oppure copia:

```locus
Titolo: "La terrazza sopra la lanterna".
Autore: "Esempio LOCUS".

La Banchina è una stanza.
La Lanterna è una stanza.
La Terrazza è una stanza.
La Lanterna è a nord della Banchina.
La Terrazza sovrasta la Lanterna.
Inizia nella Banchina.

La Banchina ha descrizione "A nord si trova la lanterna.".
La Lanterna ha descrizione "La banchina è a sud; una scala sale alla terrazza.".
La Terrazza ha descrizione "La scala scende alla lanterna. Il parapetto impedisce altre uscite.".
```

| Comando | Luogo o risposta |
| --- | --- |
| `vai a nord` | Lanterna |
| `muoviti in alto` | Terrazza |
| `e` | Nessun passaggio; resti sulla Terrazza |
| `o` | Nessun passaggio; resti sulla Terrazza |
| `dirigiti all'esterno` | Direzione riconosciuta, uscita assente |
| `procedi giù` | Lanterna |
| `cammina verso sud` | Banchina |

`sovrasta` crea un collegamento verticale percorribile in entrambi i sensi.
Il testo delle descrizioni spiega il percorso, ma sono le dichiarazioni di
relazione a renderlo utilizzabile. La frase sul parapetto non crea da sola
un vincolo: le altre uscite mancano perché non sono state dichiarate.

**Tre errori diversi.** `vai` richiede una direzione; `vai alla terrazza`
non è una direzione ammessa; `vai a est` è una frase valida, ma qui non esiste
un passaggio a est. Nessuno dei tre errori sposta il giocatore. I nomi di stanze
non attivano una ricerca automatica del percorso.

**Confronto con le abbreviazioni.** Riparti e usa `n`, `u`, `d`, `s`:
devi attraversare gli stessi luoghi. La forma inglese `w` e quella italiana
`o` indicano entrambe ovest. Non vengono create stanze per completare una
direzione senza uscita.
