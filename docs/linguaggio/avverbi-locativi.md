# Avverbi locativi contestuali

In un comando `metti`, le parole finali `lì` e `là` richiamano l'ultimo secondo
oggetto di un'azione riuscita:

```text
> prendi bussola
Hai preso: bussola.
> metti bussola nel baule
Hai messo bussola dentro baule.
> prendi sestante
Hai preso: sestante.
> metti il sestante lì
Hai messo sestante dentro baule.
```

`lì` e `là` hanno la stessa semantica locativa. Devono comparire come ultima
parola non quotata del comando; il nome precedente resta l'oggetto diretto e usa
la normale risoluzione di articoli, sinonimi, frammenti e ambiguità.

Il referente locativo è `Session.indirect_pronoun_id`, condiviso con `mettici`,
`metticelo` e `metticela`. Se manca, LOCUS produce l'evento
`no_indirect_referent`, non consuma un turno e non modifica il mondo. `metti lì`
segnala invece che manca l'oggetto diretto.

Una frase che contiene sia `lì`/`là` sia una destinazione introdotta da `in`,
`nel`, `nella`, `nello` o `nell'` è contraddittoria e viene rifiutata. Gli
avverbi non indicano automaticamente la stanza corrente e non vengono estesi ad
altri verbi in questo incremento.
