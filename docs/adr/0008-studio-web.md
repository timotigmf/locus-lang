# ADR 0008 — Studio statico con compilatore Python nel browser

Stato: accettato per M5, Studio 0.5.

La richiesta richiede editor, compilazione, gioco, test, diagnostica, manuale,
mappa ed esportazione web. Il compilatore esistente è Python senza dipendenze
runtime. Duplicarne la semantica in JavaScript introdurrebbe due implementazioni
di regole/rollback da mantenere conformi. Un backend di compilazione imporrebbe
hosting, isolamento e invio dei sorgenti al server.

Decisione: Pyodide 314.0.7 in module worker, con lo stesso pacchetto LOCUS usato
dalla CLI. `studio.Studio` adatta JSON, progetti temporanei, diagnosi e sessioni;
il dominio e il compilatore non dipendono dall'interfaccia. Le inclusioni nella
versione Studio sono limitate alla radice virtuale. La CLI conserva il contratto M4.
Il worker accetta soltanto operazioni definite; non esegue Python inserito dall'utente.
Ogni compilazione fallita invalida lo stato precedente. Ogni test ha una sessione nuova.

CodeMirror 6 per editor e segnali di errore; span Python convertiti da code point
a offset UTF-16 prima di sottolineare. Marked e DOMPurify per manuali incorporati.
Dati di storia resi come testo, SVG con etichette escapate. Nessun CDN a runtime:
asset Pyodide distribuiti insieme al sito e alla release.

La release ZIP contiene sorgenti, giocatore web e motore: compila all'avvio, non
carica l'IR JSON sperimentale da input arbitrario. Richiede HTTP/HTTPS; la portable
release non significa eseguibile nativo universale. Il costo è un runtime più
pesante di un giocatore JavaScript dedicato. Un backend alternativo richiederà
la stessa suite di conformità prima di sostituire questa soluzione.

Salvataggio locale nel browser e backup JSON, senza autenticazione o cloud sync.
Timeout di 120 secondi e pulsante di interruzione terminano il worker. Limiti
progetto e copioni sono espliciti; non si promette isolamento da file ostili di
qualsiasi dimensione. Una richiesta di hosting pubblico si realizza su GitHub Pages
con sito statico generato e verifica browser; niente chiavi o token negli asset.

Fonti primarie consultate:
- [Pyodide: distribuzione](https://pyodide.org/en/stable/usage/downloading-and-deploying.html).
- [Pyodide: module worker](https://pyodide.org/en/stable/usage/webworker.html).
- [CodeMirror: editor](https://codemirror.net/examples/basic/).
- [CodeMirror: diagnostica](https://codemirror.net/examples/lint/).

Revisione prima di salvataggi persistenti delle sessioni, multiutente, LSP,
compilatore JavaScript autonomo o installatori nativi.
