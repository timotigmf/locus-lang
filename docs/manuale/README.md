# Prima storia giocabile

Salvare come `storia.locus` in UTF-8 senza BOM:

```locus
La Cucina è una stanza.
Il Corridoio è una stanza.
Il Corridoio è a nord della Cucina.
La chiave è una cosa nella Cucina.
```

Eseguire `locus gioca storia.locus`. Una copia è in `examples/prima_storia.locus`.
La prima stanza dichiarata è l'inizio; la posizione nord genera automaticamente
l'uscita sud nel senso opposto. Nomi e riferimenti possono precedere le dichiarazioni.

```text
Cucina
Vedi: chiave.
> prendi la chiave
Hai preso: chiave.
> inventario
Inventario: chiave.
> nord
Corridoio
Vedi: nessun oggetto.
> sud
Cucina
Vedi: nessun oggetto.
> esci
A presto.
```

`guarda` ripete la descrizione; prendere due volte non duplica l'oggetto; un'uscita
inesistente lascia invariata la posizione. Oggetti in un'altra stanza non sono
raggiungibili. Gli oggetti privi di collocazione compilano ma non sono visibili.
`locus ast` e `locus ir` consentono di ispezionare la compilazione.
Il transcript di soluzione è verificato automaticamente da test di sessione e CLI.
