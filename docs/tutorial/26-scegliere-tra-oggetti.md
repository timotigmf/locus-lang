# 26. Scegliere tra oggetti simili

Apri `examples/tutorial/26_chiarimenti.locus` nello Studio e premi **Compila e
prova**. L'esempio mette due chiavi raggiungibili nella stessa stanza.

## Prova guidata

```text
> prendi chiave
Quale intendi? 1) chiave di rame; 2) chiave di ferro. Rispondi con il numero o il nome, oppure scrivi «annulla».
> scura
Hai preso: chiave di ferro.
```

`scura` funziona perché la storia dichiara:

```locus
La Sala è una stanza.
La chiave di ferro è una chiave nella Sala.
Comprendi "scura" come "chiave di ferro".
```

Riavvia e rispondi `1`: LOCUS prende la chiave di rame. Riavvia ancora, scrivi
`prendi chiave` e poi `ferro`: un frammento univoco del nome basta.

## Prova negativa

Dopo la domanda rispondi `legno`. Nessuna candidata corrisponde e il sistema
chiede di scegliere ancora, senza consumare un turno. Scrivi `annulla` per
rinunciare oppure `guarda` per abbandonare il chiarimento ed eseguire un altro
comando.

## Esercizio

Aggiungi `Comprendi "vecchia" come "chiave di rame".` e verifica che `vecchia`
selezioni la prima chiave. Poi aggiungi lo stesso sinonimo alla chiave di ferro:
il compilatore rifiuta il vocabolario incoerente invece di introdurre una scelta
silenziosa.

Nel pannello **Test**, registra `prendi chiave` e `2`. Il transcript conserva sia
la domanda sia l'azione ripresa, quindi controlla anche le regressioni del dialogo.

## Correggere un numero fuori intervallo

Dopo `prendi chiave`, prova `0000` oppure un numero molto grande: la domanda
resta attiva. Rispondi `0001` per scegliere la prima chiave. Gli zeri iniziali
non cambiano il numero; una sequenza molto lunga incollata per errore non deve
interrompere la partita. Il copione `26_chiarimenti.comandi` contiene una prova
breve con errore, correzione e controllo dell'inventario.

## Ritrovare le alternative dopo un errore

Dopo `prendi chiave`, rispondi `chiave`, `oro` oppure `99`: LOCUS spiega che
la risposta non identifica un oggetto e ripresenta `1) chiave di rame;
2) chiave di ferro`. I numeri restano gli stessi della domanda iniziale.
Puoi quindi digitare `2` per prendere quella di ferro oppure `annulla` per
abbandonare il chiarimento. Anche una risposta vuota conserva la domanda.
Non occorre risalire nella trascrizione per ritrovare le alternative.

## Rispondere con una frase esplicita

Dopo `prendi chiave` puoi scrivere `scegli 2`, `scegli ferro` oppure
`scegli scura`: tutte e tre prendono la chiave di ferro dell'esempio.
Il prefisso funziona anche nelle storie che contengono conversazioni.
`scegli chiave` resta ambiguo; `scegli` da solo è incompleto: in entrambi
i casi la domanda rimane aperta e puoi correggerti con `scegli 2`.
