# ADR 0013 — forme di comando esplicite nell'IR

Stato: accettato.

## Contesto

L'IR 8 conservava un solo comando e un solo separatore per azione. Deducendo
automaticamente un imperativo dall'infinito si introdurrebbero errori con verbi
irregolari, pronominali e forme scelte dall'autore. Un dizionario globale non può
decidere quali parole debbano attivare una particolare azione della storia.

## Decisione

L'autore dichiara una forma principale, zero o più sinonimi e, per le azioni a
due oggetti, uno o più separatori. L'IR 9 conserva le tuple ordinate `commands`
e `separators` in `ActionIR`. Il compilatore garantisce che ogni comando sia
univoco nell'intero progetto e non occupi una forma standard. Il parser giocatore
risolve una forma direttamente nell'ID dell'azione e riconosce le articolazioni
italiane di alcune preposizioni di base.

## Alternative considerate

- Generare forme flesse dall'infinito: scartato perché non deterministico senza
  un lessico morfologico e comunque incapace di scegliere sinonimi narrativi.
- Applicare sostituzioni testuali prima del parser: scartato perché perderebbe
  ruoli degli argomenti, collisioni e diagnostica strutturata.
- Incorporare subito pattern arbitrari: rinviato finché forme, separatori e
  disambiguazione non hanno un corpus di conformità sufficiente.

## Conseguenze

Gli autori controllano il vocabolario accettato e tutte le interfacce eseguono
lo stesso catalogo. La dichiarazione è più verbosa quando contiene molte forme,
ma resta verificabile e copiabile. L'aggiunta di pattern multiparola richiederà
un'estensione successiva dell'IR, senza cambiare gli ID delle azioni o le regole.
