# ADR 0012 — azioni dell'autore come catalogo tipato

Stato: accettato.

## Contesto

Il motore di regole accettava azioni registrate dall'host, ma il sorgente non
poteva dichiararne. Aggiungere soltanto parole al parser del giocatore avrebbe
creato comandi senza contratto semantico; eseguire testo delle regole dal runtime
avrebbe invece unito parser, mondo e interfaccia.

## Decisione

Una dichiarazione `Azione` crea un record nominale con zero, uno o due argomenti
tipati, un comando e, per due argomenti, un separatore. Il compilatore unisce
questi record al catalogo `ActionSpec` iniettato dall'host e usa lo stesso
controllo di sottotipo delle relazioni e proprietà.

L'IR 8 conserva soltanto le azioni dell'autore in `ActionIR`. Il parser giocatore
riceve questi record dal mondo compilato e produce un `Intent` con l'ID già
risolto. Il dispatcher esegue il normale motore a fasi. L'azione di base è un
successo senza effetti; la fase `invece` permette all'autore di sostituirla.
Comandi standard e comandi dell'autore condividono uno spazio di nomi con
collisioni diagnosticate in compilazione.

## Alternative considerate

- Deducere l'imperativo italiano dall'infinito: scartato perché forme irregolari,
  ambigue e pronominali richiedono lessico esplicito.
- Memorizzare una stringa di regola da interpretare a runtime: scartato perché
  perderebbe controllo statico, span, sicurezza e parità fra frontend.
- Rendere ogni azione una funzione Python: scartato perché introdurrebbe codice
  nativo e dipendenza dall'host nelle storie esportate.
- Implementare subito pattern grammaticali arbitrari: rinviato per definire prima
  identità, arità, tipi, transazioni e collisioni.

## Conseguenze

Le storie possono introdurre verbi italiani propri mantenendo rollback, trace,
priorità e tipizzazione. CLI, Studio e release leggono lo stesso catalogo IR.
La prima grammatica è deliberatamente limitata a un comando di una parola e un
separatore; sinonimi, flessioni e riferimenti impliciti richiedono un'estensione
compatibile dell'IR e del risolutore.

## Criterio di revisione

Rivedere la forma dei comandi con il corpus italiano del prossimo pacchetto.
Qualunque pattern futuro dovrà dichiarare token e ruoli degli argomenti, rilevare
collisioni prima del runtime e produrre lo stesso `ActionCall` strutturato.
