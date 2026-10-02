# ADR 0041 — guardare un oggetto

Stato: accettato, 2026-10-02.

## Contesto

In italiano `guarda` può descrivere il luogo oppure introdurre l'oggetto da
esaminare. LOCUS riconosceva soltanto la prima forma: `guarda custodia` diventava
un comando sconosciuto, anche se `esamina custodia` e `x custodia` funzionavano.

## Decisione

Il parser del giocatore distingue le forme per arità. `guarda` e `look` senza
oggetto conservano l'azione `look`; con un nome producono l'intento strutturato
`examine`. Anche `osserva`, `ispeziona`, `controlla`, `inspect` e la forma
classica `look at` producono `examine`.

Gli articoli continuano a essere rimossi dal normale parser nominale. Gli alias
sono comandi standard riservati e non cambiano il formato IR 21. Risoluzione,
sinonimi, nomi parziali, disambiguazione e pronomi restano quelli dell'azione
`esaminare` già esistente.

## Alternative considerate

- Aggiungere una seconda azione `guardare oggetto`: avrebbe duplicato
  raggiungibilità, regole e resa di `esaminare`.
- Trattare sempre `guarda` come `examine`: avrebbe rotto il comando senza
  argomenti che descrive il luogo.
- Riscrivere il testo in `esamina`: avrebbe violato il confine fra parsing e
  semantica strutturata.

## Conseguenze e verifica

Le regole `per esaminare` intercettano tutte le forme senza conoscere l'alias
digitato. Test di parser, runtime, diagnostica, tutorial e browser verificano la
distinzione tra `guarda` e `guarda NOME`.
