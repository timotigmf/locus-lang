# Clitici doppi con destinazione ricordata

LOCUS conserva separatamente l'ultimo oggetto diretto e l'ultimo secondo oggetto
di un'azione riuscita. Le forme `metticelo` e `metticela` possono quindi omettere
sia la cosa trasportata sia il contenitore:

```text
> prendi gemma
Hai preso: gemma.
> metti gemma nella scatola
Hai messo gemma dentro scatola.
> prendi moneta
Hai preso: moneta.
> metticela
Hai messo moneta dentro scatola.
```

Nell'ultimo comando `la` richiama la moneta e `ci` richiama la scatola. Le due
identità restano campi distinti della sessione; il runtime riceve lo stesso
intento tipato prodotto da `metti moneta nella scatola`.

Una riuscita con due oggetti aggiorna entrambi i referenti. Una successiva
azione riuscita con il solo oggetto diretto aggiorna quest'ultimo e conserva il
secondo. Errori e azioni fallite non cambiano nessuno dei due.

Se manca l'oggetto diretto, LOCUS risponde che non esiste ancora un referente
pronominale. Se esiste l'oggetto ma non è mai riuscita un'azione con un secondo
oggetto, risponde:

```text
Non c'è ancora una destinazione a cui riferire il clitico «ci».
```

Il secondo referente può provenire da qualunque azione a due oggetti. Il comando
`metticela` applica poi i normali controlli del contenitore: se il referente è
una chiave o un altro oggetto incompatibile, l'azione fallisce come la forma
estesa. `metticelo` e `metticela` non applicano ancora l'accordo grammaticale;
plurali e clitici delle azioni definite dall'autore restano fuori da questo
incremento.

La forma complementare `mettici la moneta`, che sottintende soltanto il
contenitore, è descritta nella specifica del [clitico locativo](clitico-locativo.md).
