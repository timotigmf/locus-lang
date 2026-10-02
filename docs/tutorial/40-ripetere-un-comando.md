# 40. Ripetere un comando

Apri `examples/tutorial/40_ripetere_comando.locus` nello Studio e premi
**Compila e prova**. La storia contiene una campana, un'azione dell'autore e una
scena temporale.

```locus
La Torre è una stanza.
La campana è una cosa nella Torre.

Azione "suonare" su una cosa con comando "suona".
Regola "rintocco" per suonare "campana" nella fase invece:
    dì "La campana risponde con un rintocco profondo.";
Fine regola.
```

## Prova guidata

1. Appena avviata la storia, scrivi `g`: non esiste ancora un comando riuscito.
2. Scrivi `suona campana`, poi `ancora`: senti due rintocchi distinti.
3. Scrivi `attendi`, poi `ripeti`: trascorrono due turni e la scena avanza.
4. Prova anche `again` e `g` dopo `esamina campana`.

## Caso negativo

Dopo `esamina campana`, scrivi un comando inesistente come `vola`, poi `g`.
L'errore non cancella il ricordo: LOCUS esamina di nuovo la campana.

## Esercizio

Aggiungi una seconda campana, provoca un chiarimento con `esamina campana` e
scegli l'alternativa `2`. Verifica che `g` ripeta l'esame dell'oggetto scelto,
senza chiedere nuovamente quale campana intendi.

Il [riferimento sulla ripetizione](../linguaggio/ripetere-comando.md) spiega
quali intenti vengono ricordati e come interagiscono con turni e regole.
