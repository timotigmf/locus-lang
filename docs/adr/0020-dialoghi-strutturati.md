# ADR 0020 — persone e grafi di dialogo strutturati

Stato: accettato, 27 settembre 2026.

## Contesto

Le azioni definite dall'autore possono simulare una singola battuta, ma non
rappresentano identità dei nodi, scelte, collegamenti, memoria di visita o una
conversazione che prosegue per più turni. Codificare tutto in testi o tabelle
convenzionali costringerebbe il runtime a reinterpretare stringhe.

## Decisione

La libreria narrativa aggiunge il tipo `persona`, collocabile ma non
trasportabile. Il compilatore riceve dall'host i tipi ammessi come partecipanti;
non contiene l'identificatore narrativo `mondo.persona`.

L'AST e l'IR rappresentano dialoghi, nodi e scelte con record immutabili. Il
lowering risolve persona e destinazioni, assegna ID e rifiuta duplicati, limiti e
nodi irraggiungibili. I cicli restano validi. Il runtime generico verifica il
grafo ai confini dell'IR; la stdlib applica il vincolo `persona` e gestisce i
comandi del giocatore.

La sessione conserva dialogo e nodo attivi e l'ordine dei nodi visitati. Un
passaggio espone un trace strutturato separato dal trace delle regole. I comandi
di conversazione sono riservati soltanto quando il progetto dichiara almeno un
dialogo, per non sottrarre `parla` alle azioni autore esistenti. L'IR sale alla
versione 16.

## Alternative considerate

- Una tabella di battute interpretata dalla stdlib: scartata perché riferimenti
  e raggiungibilità resterebbero stringhe controllate soltanto in esecuzione.
- Regole autonome per ogni battuta: scartate perché lo stato conversazionale e
  le scelte non avrebbero identità comune.
- Condizioni ed effetti già nel primo incremento: rinviati per definire come una
  scelta partecipa alla transazione del rulebook e come si presenta una scelta
  disabilitata.
- Un parser linguistico libero degli argomenti: rinviato; le scelte numerate o
  nominate sono deterministiche e diagnosticabili.

## Conseguenze

Studio, CLI e release condividono lo stesso grafo e lo stesso stato multi-turno.
I nodi finali e le scelte terminali hanno comportamento esplicito. Questo primo
contratto supporta dialoghi ramificati e ciclici, ma le battute restano statiche
finché condizioni, effetti e conoscenze non ricevono un'estensione dedicata.
