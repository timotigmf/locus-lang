# ADR 0014 — forme multiparola prive di ambiguità di prefisso

Stato: accettato.

## Contesto

L'IR 9 accettava più forme per azione, ma ogni forma era una sola parola. Molte
espressioni italiane utili sono locuzioni: `fai silenzio`, `porta in vista`,
`rendi omaggio`. Trattare la prima parola come verbo e il resto come nome avrebbe
reso impossibile distinguerle dagli oggetti.

## Decisione

Una forma di comando contiene da uno a quattro token alfabetici fissi. Il parser
giocatore confronta l'intera sequenza iniziale e poi assegna i token restanti agli
oggetti. Il compilatore e il runtime rifiutano qualsiasi coppia in cui una forma
è prefisso token dell'altra, considerando anche i comandi standard. L'IR 10
mantiene `commands` come tuple di stringhe canoniche: cambia il contratto di
validazione e interpretazione, senza introdurre testo eseguibile.

## Alternative considerate

- Preferire sempre la forma più lunga: scartato perché il significato cambierebbe
  aggiungendo un nuovo sinonimo e un oggetto potrebbe diventare parola fissa.
- Preferire sempre la forma più corta: scartato perché renderebbe irraggiungibili
  le forme lunghe con lo stesso prefisso.
- Consentire pattern arbitrari fra gli oggetti: rinviato; richiede ruoli nominati,
  verifica dell'ambiguità e diagnostica più ampia.

## Conseguenze

Le locuzioni iniziali sono deterministiche e portabili fra CLI, Studio e release.
Alcune coppie linguisticamente plausibili devono essere rinominate, ma nessun
comando cambia interpretazione quando il catalogo cresce. Clitici, parole fisse
intermedie e disambiguazione a più turni restano decisioni separate.
