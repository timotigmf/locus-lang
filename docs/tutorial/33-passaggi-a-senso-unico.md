# 33. Scendere senza ritorno

Apri `examples/tutorial/33_senso_unico.locus` nello Studio e premi
**Compila e prova**. La storia parte sulla Terrazza, sopra una scala che conduce
alla Cripta in una sola direzione.

```locus
La Terrazza è una stanza.
La Cripta è una stanza.

Dalla Terrazza si va giù verso la Cripta.

Inizia nella "Terrazza".
```

## Prova guidata

1. Apri **Mappa**: il collegamento ha una freccia e l'etichetta
   `giù (solo andata)`.
2. Scrivi `giù` oppure `d`: raggiungi la Cripta.
3. Scrivi `su` oppure `u`: LOCUS risponde che non esiste alcun passaggio.

La frase inizia sempre con l'origine e termina con la destinazione. Funziona
anche con le direzioni cardinali, diagonali e `dentro`/`fuori`:

```text
Dalla Sala si va a nord verso la Galleria.
Dal Molo si va a nordest verso il Faro.
Dall'Atrio si va fuori verso il Cortile.
```

## Caso negativo

Una direzione non registrata conserva la diagnostica `E104`:

```text
Dalla Terrazza si va a sottovento verso la Cripta.
```

LOCUS non inventa un significato per `sottovento`. Usa una delle dodici
direzioni disponibili oppure dichiara una normale relazione prevista dal
catalogo dell'host.

## Esercizio

Aggiungi una stanza a est della Cripta con un collegamento normale e verifica
che quel secondo tratto sia percorribile in entrambe le direzioni. Poi prova a
proteggere il passaggio a senso unico con una porta.

Il [riferimento sui passaggi a senso unico](../linguaggio/passaggi-senso-unico.md)
descrive grammatica, IR, porte, veicoli e rappresentazione nell'atlante.
