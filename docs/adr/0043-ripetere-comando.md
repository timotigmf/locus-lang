# ADR 0043 — ripetere l'ultimo comando riuscito

Stato: accettato, 2026-10-02.

## Contesto

Le avventure testuali usano spesso `again` o `g` per ripetere un'azione. LOCUS
non conservava il comando precedente, quindi il giocatore doveva riscrivere
anche frasi lunghe o una scelta appena chiarita.

## Decisione

La sessione conserva l'ultimo `Intent` concluso con successo. `ancora`,
`ripeti`, `again` e `g` rieseguono quell'intento attraverso lo stesso dispatcher
e lo stesso rulebook. Non viene riscritto né rianalizzato il testo originario.

Comandi sconosciuti, azioni fallite e metacomandi come `aiuto`, `turno` o
`punteggio` non sostituiscono il ricordo. La descrizione automatica iniziale,
eseguita dall'host senza avanzare il tempo, non viene memorizzata. Se manca un
comando riuscito, la ripetizione produce un esito specifico e non consuma il
turno.

Dopo un chiarimento, l'intento ricordato include l'identificatore dell'oggetto
scelto. Durante un chiarimento ancora aperto, ripetere ripropone invece la stessa
azione ambigua. Il formato IR 21 non cambia.

## Alternative considerate

- Conservare il testo digitato: avrebbe richiesto una seconda analisi e avrebbe
  potuto risolvere un oggetto diverso dopo un chiarimento.
- Conservare anche i fallimenti: un errore di battitura avrebbe cancellato un
  comando utile e reso meno prevedibile `ancora`.
- Implementare la cronologia nei frontend: CLI, Studio e release avrebbero
  mantenuto stati diversi.

## Conseguenze e verifica

`Session.last_intent` fa parte dello stato immutabile. Ogni ripetizione riuscita
consuma un turno come il comando originale e può far avanzare scene o regole.
Test di parser, rollback, chiarimento, scene, Studio, browser e tutorial
verificano il contratto.
