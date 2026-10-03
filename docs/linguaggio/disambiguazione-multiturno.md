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

Pronomi e clitici singolari sono descritti nella
[specifica dedicata](pronomi-e-clitici.md). Il chiarimento riguarda una sola
posizione dell'argomento alla volta.

## Robustezza delle risposte numeriche

Le risposte decimali sono confrontate con il numero delle alternative senza
convertire l'intera stringa in un intero illimitato. Anche un numero incollato
molto lungo produce il normale errore di scelta e conserva la sessione. Zero
non seleziona alcuna alternativa; gli zeri iniziali sono ammessi (`0001` vale
`1`), anche con cifre decimali Unicode.

La presentazione di `invalid_clarification` include nuovamente le candidate
nello stesso ordine e con gli stessi numeri della domanda. Il messaggio
distingue la risposta non valida dalla domanda iniziale e ricorda il comando
`annulla`. Questa presentazione non modifica lo stato né consuma un turno.

## Risposta esplicita con «scegli»

Durante una domanda aperta, `scegli 2`, `scegli ferro` e `scegli scura`
equivalgono al numero, nome parziale o sinonimo senza prefisso. La risposta
viene assegnata al chiarimento anche se la storia contiene dialoghi.
`scegli` senza argomento, un numero fuori intervallo o un nome ambiguo
conservano la domanda e producono `invalid_clarification`.

Questa precedenza è limitata al chiarimento attivo: fuori da esso, `scegli`
conserva il comportamento del parser ordinario, incluse le scelte di dialogo
e le eventuali azioni dell'autore. Non viene aggiunta una parola riservata
al compilatore e l'IR resta invariata.
