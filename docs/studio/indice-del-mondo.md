# Indice completo del mondo

Stato: implementato nello Studio LOCUS 0.5.0a1 sul contratto IR 21.

L'Indice del mondo è una proiezione del programma compilato. Non analizza il
testo nell'editor e non inventa informazioni: legge soltanto l'IR restituita dal
compilatore e lo snapshot corrente per proprietà, relazioni e tabelle mutabili.

## Sezioni

- **Progetto compilato**: titolo, autore, versione IR, punto iniziale e conteggi.
- **Gerarchia dei tipi**: tipi standard e dell'autore, genitore e ID tecnico.
- **Entità e proprietà**: tipo completo e valori correnti.
- **Relazioni**: sorgente, predicato e destinazione, comprese le inverse generate.
- **Schemi delle proprietà**: tipo del valore, proprietari ammessi e predefinito.
- **Vocabolario**: sinonimi nominali e rispettiva entità.
- **Risorse, veicoli e commercio**: manifest, posizione e dati specializzati.
- **Tabelle, dialoghi e scene**: struttura compilata e stato osservabile.
- **Azioni e regole**: forme dei comandi, selettori, fase, priorità, effetti e origine.

## Ricerca ed esportazione

Il campo **Filtra tipi, entità, relazioni, regole…** nasconde le righe che non
contengono il testo cercato e mostra il numero di risultati. La ricerca non
modifica il progetto o la sessione. Una ricerca senza corrispondenze produce un
messaggio esplicito, non una tabella apparentemente vuota.

**Scarica JSON** esporta `indice-mondo-locus.json`: è l'IR completa della
compilazione corrente, utile per ispezione e strumenti sperimentali. Il formato
IR è ancora versionato e non è promesso come formato stabile di salvataggio o
come file eseguibile.

## Limiti

L'indice non è un debugger: condizioni ed effetti sono riassunti, mentre il
pannello **Regole e trace** mostra quali regole sono state considerate
nell'ultima azione. La ricerca opera sui valori visualizzati e non interpreta
sinonimi o query del linguaggio.
