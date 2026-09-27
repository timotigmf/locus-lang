# 7. Creare tipi propri

Il progetto completo è `examples/tutorial/07_tipi.locus`. In questa lezione una
cripta specializza una stanza, un reliquiario specializza un contenitore e una
reliquia passa attraverso due livelli di gerarchia.

```locus
Titolo: "Il reliquiario della cripta".
Autore: "Esempio LOCUS".

Un santuario è un tipo di stanza.
Un tesoro è un tipo di cosa.
Una reliquia è un tipo di tesoro.
Un reliquiario è un tipo di contenitore.
Una chiave rituale è un tipo di chiave.

La Cripta è un santuario.
Inizia nella "Cripta".
La Cripta ha descrizione "Una nicchia custodisce un antico cofano.".

Il cofano è un reliquiario nella Cripta.
Il cofano ha stato "bloccato".
La chiave di bronzo è una chiave rituale nella Cripta.
La chiave di bronzo apre il cofano.
Il rubino è una reliquia nel cofano.

Comprendi "scrigno" come "cofano".
Comprendi "gemma" come "rubino".

Regola "eco della reliquia" per prendere "rubino" nella fase dopo:
    imposta "descrizione" di "Cripta" a "Il cofano vuoto riverbera nella cripta.";
    dì "Il rubino accende riflessi rossi sulle pareti.";
Fine regola.
```

## Prova guidata

Esegui `guarda`, `prendi chiave`, `apri scrigno con chiave`, `prendi gemma` e
`guarda` e `inventario`. Il santuario appare nella mappa come luogo; il reliquiario conserva
stato e contenimento; la chiave rituale sblocca il cofano; la reliquia è
trasportabile perché discende da tesoro e quindi da cosa. La regola può modificare
la descrizione del santuario perché la proprietà della stanza vale anche per i
suoi sottotipi.

Apri **Indice del mondo** nello Studio. La colonna Tipo mostra l'intero percorso,
per esempio `cosa › tesoro › reliquia`, così puoi controllare la categoria
effettiva senza leggere gli ID interni.

## Caso negativo

Queste due dichiarazioni non possono compilare:

```text
Un cimelio è un tipo di reperto.
Un reperto è un tipo di cimelio.
```

LOCUS segnala `E114` perché la gerarchia contiene un ciclo. Anche un genitore mai
dichiarato è un errore; dichiararlo più avanti, invece, è valido.

## Esercizio

Definisci `Un amuleto è un tipo di reliquia.`, aggiungi un amuleto nel cofano e
prova a prenderlo. Poi crea una seconda gemma: il comando abbreviato `prendi
gemma` dovrà chiedere quale intendi finché i nomi restano ambigui.
