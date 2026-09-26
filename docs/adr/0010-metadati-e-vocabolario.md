# ADR 0010 — metadati nel sorgente e vocabolario dichiarativo

Stato: accettato.

## Contesto

Lo Studio mostrava un titolo modificabile fuori dal sorgente e l'esempio
principale introduceva subito `Includi`. Inoltre i nomi parziali aiutavano il
giocatore, ma l'autore non poteva indicare che “scatola” e “custodia” designano
lo stesso oggetto. Inserire un intero dizionario italiano nel runtime non risolve
la polisemia e renderebbe i risultati dipendenti da una risorsa esterna.

## Decisione

Il sorgente ammette `Titolo:`, `Autore:` e direttive ripetibili
`Comprendi "alias" come "entità".`. Titolo e autore sono unici nel progetto.
Gli alias sono risolti in analisi semantica, memorizzati nell'IR 6 come coppie
alias/ID e applicati dal risolutore degli oggetti soltanto alle entità
raggiungibili.

La priorità è nome esatto, alias esatto, corrispondenza parziale. Ogni risultato
plurimo resta ambiguo e viene mostrato al giocatore. Il progetto iniziale dello
Studio e il faro distribuito usano un solo file; le inclusioni restano disponibili
come tecnica successiva.

## Alternative considerate

- Titolo solo nell'interfaccia: scartato perché export, CLI e sorgente avrebbero
  identità diverse.
- Riscrittura testuale prima del parser: scartata perché perderebbe span e
  potrebbe modificare parole non nominali.
- Dizionario italiano globale: scartato perché sinonimia, flessione e polisemia
  dipendono dal contesto della storia e non garantiscono una scelta deterministica.
- Alias risolti nel frontend: scartato perché CLI e release divergerebbero.

## Conseguenze

Gli esempi sono autoidentificanti e copiabili in un singolo file. Gli autori
possono ampliare il lessico senza cambiare il parser dei comandi. L'IR cambia da
5 a 6 e resta sperimentale. I sinonimi dei verbi, la morfologia, i pronomi e le
relazioni dinamiche richiedono decisioni separate.

## Criterio di revisione

Rivedere la decisione quando verranno progettati verbi definiti dall'autore,
flessione morfologica o namespace dei moduli; preservare diagnostica deterministica
e parità fra CLI, Studio e release.

