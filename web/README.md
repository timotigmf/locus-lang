# LOCUS Studio web

Interfaccia statica, compilatore Python in Pyodide e editor CodeMirror. Nessun
backend di compilazione. Per l'uso vedere [il manuale](../docs/studio/README.md).

## Sviluppo e build

Node 22, Python 3.11+ per il server locale:

```sh
cd web
npm ci
npm run build
python3 -m http.server 8765 --bind 127.0.0.1 --directory site
```

Apri http://127.0.0.1:8765. Il risultato è in `web/site`, ignorato da Git.
Tutti gli asset del runtime sono copiati da Pyodide npm e serviti localmente.
Non caricare le cartelle sorgente o node_modules sul sito: pubblica solo `site`.
I file di progetto degli autori restano nel loro browser e nei loro backup.

## Verifiche

Con il server in esecuzione: `npm test`. In locale la configurazione usa Chrome
installato su macOS; in CI usa Chromium di Playwright (`npx playwright install
--with-deps chromium`). La suite controlla anche uno ZIP esportato, estratto e
servito in un'altra cartella con richieste esterne bloccate. Il workflow Studio
web produce l'artefatto scaricabile `locus-studio-sito-statico`.

Le dipendenze sono bloccate nel lockfile; `LICENZE.txt` viene generato nella build.
Pyodide è MPL-2.0, Python usa la licenza PSF e relative attribuzioni, CodeMirror è MIT.
Le licenze complete delle altre librerie sono incluse; non è una scelta di licenza
per il codice originale LOCUS. Sorgente del runtime Pyodide: 
https://github.com/pyodide/pyodide/tree/314.0.7 ; sorgente Python:
https://github.com/python/cpython/tree/v3.14.2 . Distribuiamo questi componenti senza
modificarli. Il runtime include componenti del progetto CPython; si conservano le
attribuzioni nel relativo testo di licenza. Il testo PSF archiviato è quello della
release 3.14.0; il runtime Pyodide dichiara Python 3.14.2.
