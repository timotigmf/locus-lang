# Pronomi distinti per ruolo

Quando una frase contiene un pronome sia come oggetto diretto sia come secondo
oggetto, LOCUS usa due memorie separate della sessione:

```text
> prendi chiave
Hai preso: chiave di bronzo.
> apri cofano con chiave
Hai aperto: cofano.
> chiudilo
Hai chiuso: cofano.
> aprilo con essa
Hai aperto: cofano.
```

Nell'ultimo comando `lo` richiama il cofano, conservato in `pronoun_id`; `essa`
occupa invece il ruolo dello strumento e richiama la chiave, conservata in
`indirect_pronoun_id`. La forma estesa equivalente è `apri cofano con chiave`.

I pronomi riconosciuti restano `esso`, `essa`, `questo`, `questa`, `quello`,
`quella` e `it`. Nel ruolo diretto usano sempre l'ultimo referente diretto. Nel
ruolo indiretto preferiscono l'ultimo secondo oggetto; se questo non è mai stato
stabilito, mantengono la compatibilità con le sessioni semplici e usano il
referente diretto. Per esempio, dopo `esamina scatola`, `metti gemma in essa`
continua a indicare la scatola.

Soltanto un'azione riuscita aggiorna i referenti. Gli ID risolti entrano
nell'intento prima della transizione, quindi chiarimenti, controllo dei tipi,
chiavi e rollback restano gli stessi delle forme nominali complete.

Il sistema non deduce ancora genere e numero: la scelta fra `esso` ed `essa` non
filtra i candidati. I pronomi plurali richiedono un modello separato.
