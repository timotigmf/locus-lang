# Clitico locativo con oggetto esplicito

La forma `mettici OGGETTO` conserva scritto l'oggetto diretto e richiama con
`ci` l'ultimo secondo oggetto di un'azione riuscita:

```text
> prendi gettone rosso
Hai preso: gettone rosso.
> metti gettone rosso nella cassetta
Hai messo gettone rosso dentro cassetta.
> prendi gettone blu
Hai preso: gettone blu.
> mettici il gettone blu
Hai messo gettone blu dentro cassetta.
```

La forma è equivalente a `metti il gettone blu nella cassetta`: il nome
esplicito passa attraverso la normale risoluzione per articoli, sinonimi, nomi
parziali e ambiguità. `ci` viene invece risolto direttamente nell'identità
conservata da `Session.indirect_pronoun_id`.

`mettici` senza oggetto richiede un nome. `mettici OGGETTO nella DESTINAZIONE`
è rifiutato perché combina due destinazioni. Se nessuna azione riuscita ha
ancora stabilito il secondo referente, LOCUS segnala la destinazione mancante e
non consuma un turno.

Il comando usa i normali controlli di `metti`: l'oggetto deve essere trasportato,
la destinazione deve essere un contenitore raggiungibile e aperto, e i cicli di
contenimento restano vietati. La forma non introduce inferenze grammaticali né
un significato generale di `ci` per altri verbi.
