# Disambiguazione a più turni

Il risolutore cerca soltanto entità raggiungibili. Prova nell'ordine un nome
completo, un sinonimo dichiarato con `Comprendi`, quindi le parole parziali. Se
rimane una sola candidata, il comando continua; se ne rimangono più di una,
LOCUS le numera e sospende l'azione.

```text
> prendi chiave
Quale intendi? 1) chiave di rame; 2) chiave di ferro. Rispondi con il numero o il nome, oppure scrivi «annulla».
> ferro
Hai preso: chiave di ferro.
```

La risposta può essere `1`, `2`, il nome completo, una parte univoca del nome o
un sinonimo dell'oggetto. Vale anche per il secondo oggetto:

```text
> metti gemma nella scatola
Quale intendi? 1) scatola rossa; 2) scatola blu. Rispondi con il numero o il nome, oppure scrivi «annulla».
> blu
Hai messo gemma dentro scatola blu.
```

Una risposta che non seleziona una sola alternativa non modifica il mondo e
lascia aperta la domanda. `annulla` la chiude. Qualsiasi altro comando completo e
riconosciuto, per esempio `guarda`, chiude la domanda e viene eseguito.

Il chiarimento non consuma un turno finché l'azione non riesce o produce un esito
ordinario. Le candidate sono conservate come identificatori nell'oggetto
`Session`; prima di eseguire l'azione, il runtime verifica di nuovo che la scelta
sia raggiungibile. CLI, Studio e release web usano `parse_session_command`, così
la semantica è identica nei tre ambienti.

Limiti attuali: non sono ancora supportati pronomi e clitici come `prendila`; il
chiarimento riguarda una sola posizione dell'argomento alla volta.

