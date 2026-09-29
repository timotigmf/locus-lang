# 23. La rosa dei venti

Apri `examples/tutorial/23_direzioni_diagonali.locus` nello Studio e premi
**Compila e prova**. La Piazza collega quattro luoghi lungo le diagonali della
mappa.

```locus
La Piazza è una stanza.
La Vedetta è una stanza.
La Darsena è una stanza.
La Forgia è una stanza.
Il Giardino è una stanza.

La Vedetta è a nordest della Piazza.
La Darsena è a sudest della Piazza.
La Forgia è a sudovest della Piazza.
Il Giardino è a nordovest della Piazza.

Inizia nella "Piazza".
```

## Prova guidata

1. Scrivi `ne`: raggiungi la Vedetta.
2. Scrivi `so`: torni alla Piazza grazie all'inversa automatica.
3. Prova allo stesso modo `se`/`no` e `so`/`ne`.
4. Scrivi `nord`: il comando è riconosciuto, ma ricevi «Non c'è alcun passaggio
   in quella direzione.».
5. Apri **Mappa**: le quattro linee seguono i rispettivi quadranti.

Sono valide anche le forme complete italiane e, per i giocatori abituati ai
parser classici, `northeast`, `southeast`, `southwest`, `northwest` e `nw`.

## Caso negativo

Queste due frasi assegnano due mete diverse allo stesso arco e producono `E106`:

```text
La Vedetta è a nordest della Piazza.
Il Giardino è a nordest della Piazza.
```

LOCUS non sceglie una destinazione in base all'ordine. Correggi la seconda
direzione oppure collega il Giardino da un'altra stanza.

## Esercizio

Aggiungi una stanza a sudest della Vedetta. Verifica prima il percorso `ne`,
`se`, poi usa le inverse per tornare alla Piazza. Controlla infine nell'Indice
del mondo che ogni collegamento abbia il proprio arco inverso.

Il [riferimento delle direzioni](../linguaggio/direzioni-diagonali.md) elenca
forme, semantica, diagnostica e limiti.
