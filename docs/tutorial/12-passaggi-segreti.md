# 12. Passaggi segreti e mappa dinamica

Apri `examples/tutorial/12_passaggio_segreto.locus` oppure copialo nello Studio.
All'inizio Anticamera e Cripta esistono entrambe, ma non sono collegate: `nord`
risponde che non c'è alcun passaggio e la mappa mostra due luoghi senza linea.

La regola decisiva contiene:

```locus
La Anticamera è una stanza.
La Cripta è una stanza.
La leva è una cosa nella Anticamera.
La rivelato è una proprietà logica.

Regola "rivela il passaggio" per esaminare "leva" nella fase dopo
quando "rivelato" di "leva" è falso:
    crea relazione "nord" da "Anticamera" a "Cripta";
    imposta "rivelato" di "leva" a vero;
    dì "La leva scatta: la parete scorre e rivela un passaggio a nord.";
Fine regola.
```

Prova questi comandi:

| Comando | Cosa verificare |
| --- | --- |
| `nord` | Il passaggio non esiste ancora |
| `esamina leva` oppure `x leva` | Compare l'uscita e la mappa aggiunge la linea |
| `nord` | Si entra nella Cripta |
| `sud` | L'inversa è stata creata automaticamente |
| `esamina leva` | La seconda regola evita una nuova modifica |
| `nascondi passaggio` | Entrambe le direzioni vengono rimosse |

La proprietà `rivelato` serve alla logica narrativa e alle condizioni. Il grafo
resta la fonte della navigazione: una frase nella descrizione non crea mai da
sola un'uscita.

Per richiudere il varco l'esempio usa l'effetto complementare:

```locus
La Anticamera è una stanza.
La Cripta è una stanza.
La leva è una cosa nella Anticamera.

Regola "richiudi" per esaminare "leva" nella fase dopo:
    rimuovi relazione "nord" da "Anticamera" a "Cripta";
Fine regola.
```

Se nello stesso corpo aggiungi subito dopo `fallisci "Il meccanismo cede.";`,
la relazione viene ripristinata. Questo permette enigmi complessi senza lasciare
il mondo in uno stato parziale.

**Esercizio.** Sposta il passaggio a est.

**Soluzione.** Sostituisci `"nord"` con `"est"` in entrambe le istruzioni e
aggiorna i testi. Il ritorno sarà `ovest`.

La sintassi completa e le diagnosi sono nel riferimento sulle
[relazioni dinamiche](../linguaggio/relazioni-dinamiche.md).

Per aprire un passaggio dal quale non si può tornare, continua con
[Passaggio segreto senza ritorno](34-passaggio-segreto-senza-ritorno.md).

## Prima scoperta e visite successive

Nell'esempio completo la regola che racconta lo stato già scoperto ha
`priorità 10`; quella che effettua la scoperta mantiene la priorità predefinita
0. Le priorità maggiori vengono valutate per prime. Così, alla prima azione,
il messaggio «già aperto» non compare insieme all'annuncio della scoperta.
Alle azioni successive compare soltanto il messaggio di stato già noto.

Le condizioni leggono lo stato corrente prima di ogni regola: due condizioni
opposte non formano automaticamente un «se/altrimenti». Senza questa priorità,
la prima regola può cambiare il flag e rendere applicabile la seconda nella
stessa azione.

**Prova negativa:** avvia una nuova partita, esamina il dettaglio, poi ripeti
l'esame e usa `g`. La scoperta deve essere raccontata una sola volta; il testo
per le visite successive deve apparire soltanto dal secondo esame.
