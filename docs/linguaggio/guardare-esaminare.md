# Guardare il luogo ed esaminare un oggetto

Stato: implementato nella stdlib di LOCUS 0.5.0a1, senza modifica dell'IR 21.

`guarda` senza argomenti descrive nuovamente il luogo corrente:

```text
> guarda
Archivio
Vedi: custodia.
```

Quando segue un nome, lo stesso verbo esamina quell'oggetto:

```text
> guarda custodia
custodia
Una custodia di cuoio consumato.
Stato: chiuso.
```

Sono equivalenti:

```text
esamina custodia
x custodia
osserva la custodia
ispeziona custodia
controlla custodia
look at the custodia
inspect custodia
```

Tutte le forme producono l'intento `examine`. Usano quindi gli stessi nomi
parziali, sinonimi, chiarimenti a più turni e referenti pronominali. Una regola
`per esaminare` si applica a ogni alias.

## Errori precisi

`osserva` o `ispeziona` senza nome richiedono un oggetto. `guarda`, invece,
resta completo senza nome perché descrive il luogo. Un nome assente dal campo
d'azione produce «Non trovi qui quell'oggetto»; più oggetti compatibili aprono
il normale chiarimento.

## Limiti

Le forme sono alias dichiarati dalla stdlib, non sinonimi ricavati da un
dizionario esterno. Questo mantiene lo stesso risultato in CLI, Studio e release
web. L'autore può estendere i nomi degli oggetti con `Sinonimo`, mentre futuri
pacchetti lessicali potranno aggiungere forme versionate senza servizi cloud.
