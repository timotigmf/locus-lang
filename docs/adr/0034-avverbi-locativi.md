# ADR 0034 — avverbi locativi contestuali

Stato: accettato, 2026-10-01.

## Contesto

Dopo aver stabilito una destinazione, l'italiano permette di dire sia `mettici
la moneta` sia `metti la moneta lì`. La seconda forma non è un sinonimo nominale:
`lì` dipende dal contesto della sessione e occupa il ruolo della destinazione.

## Decisione

Il parser riconosce `lì` e `là` soltanto in posizione finale di un comando
standard `metti`. Produce un intento `put` con il nome diretto esplicito e il
marcatore locativo `ci` nel ruolo indiretto. Il parser di sessione risolve quel
ruolo mediante `indirect_pronoun_id`.

Una preposizione di destinazione e un avverbio locativo non possono comparire
nella stessa frase. Le parole quotate `"lì"` e `"là"` restano nomi letterali e
non attivano questa grammatica.

## Alternative considerate

- Interpretare `lì` come stanza corrente: sorprenderebbe quando il contesto è un
  contenitore e confonderebbe collocazione narrativa e comando.
- Aggiungere `lì` al dizionario dei sinonimi: il referente cambierebbe fra
  sessioni e non può essere compilato verso un ID fisso.
- Accettarlo in qualunque posizione: renderebbe ambigui nomi composti e frasi
  con destinazione esplicita.

## Conseguenze e verifica

Le nuove forme attraversano invariati risoluzione nominale, chiarimenti e
controlli di `metti`. Test parser, runtime, CLI, Studio, tutorial e browser
coprono `lì`, `là`, referente assente, oggetto assente e doppia destinazione.
L'IR resta alla versione 21.
