# 29. Ricordare anche la destinazione

Apri `examples/tutorial/29_clitici_doppi.locus` nello Studio e premi
**Compila e prova**.

## Stabilire i due referenti

```text
> prendi gemma
Hai preso: gemma.
> metti gemma nella scatola
Hai messo gemma dentro scatola.
```

Il secondo comando riuscito ricorda due ruoli: la gemma come oggetto diretto e
la scatola come destinazione.

## Cambiare soltanto l'oggetto

```text
> prendi moneta
Hai preso: moneta.
> metticela
Hai messo moneta dentro scatola.
```

`prendi moneta` sostituisce il referente diretto senza cancellare la
destinazione. In `metticela`, `la` indica la moneta e `ci` indica la scatola.
`metticelo` è la variante maschile equivalente.

## Prova negativa

Riavvia la storia, prendi subito la moneta e digita `metticela`. LOCUS non
indovina un contenitore dalla stanza: spiega che manca una destinazione per
`ci`. Il comando non consuma un turno e non sposta la moneta.

## Esercizio

Aggiungi una seconda scatola aperta. Usa una forma estesa per collocare il primo
oggetto nella nuova scatola, poi prendi l'altro e verifica che `metticelo` usi
proprio l'ultima destinazione riuscita.
