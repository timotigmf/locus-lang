# Stato e verifiche dello Studio 0.5

## Funzioni reali

Editor CodeMirror con sintassi LOCUS, file e punto d'ingresso, salvataggio locale,
backup/importazione JSON, compilazione con il motore Python originale, gioco e
riavvio, test separati con confronto dei transcript, mappa SVG/JSON, indice delle
entità, trace delle regole e diagnosi navigabili con riferimenti al manuale.
Esportazione ZIP del giocatore statico con sorgente della storia e runtime inclusi.

## Controlli eseguiti

- 294 test Python passati, inclusi adapter Studio e confine del progetto virtuale.
- Ruff, controllo formato e mypy strict passati.
- Build wheel e sdist 0.5.0a1 riuscita; build web statica riuscita.
- Quattro test browser reali passati in Chrome su macOS: flusso compilazione/gioco,
  copione verificato, mappa esportata, ZIP estratto e giocato su un percorso diverso;
  diagnosi E102 con file originale e manuale, persistenza, gestione file e backup,
  test negativo, menu mobile e assenza di overflow orizzontale.
- Release provata bloccando tutte le richieste diverse dall'hosting locale:
  nessun CDN necessario al giocatore.
- Audit npm dopo aggiornamento delle dipendenze: zero vulnerabilità note segnalate.
- Formattazione JavaScript/CSS/HTML con Prettier verificata.

I test locali non costituiscono una certificazione di tutti i browser: Safari,
Firefox, dispositivi mobili fisici e tecnologie assistive richiedono verifiche
ulteriori. Il workflow Studio web è predisposto per Chromium in CI; l'esito remoto
va verificato sul commit pubblicato. I test controllano lo schermo mobile in Chrome,
non un dispositivo iOS o Android reale.

## Pubblicazione

GitHub Pages ha restituito HTTP 422: il piano attuale non supporta Pages per questa
repository privata. Non è stata cambiata la visibilità del repository.
La distribuzione statica pronta è in `web/site`; si può pubblicare su hosting
statico o su Pages quando abilitato. Finché un hosting non è configurato e verificato,
non va presentato un URL pubblico come funzionante.

## Limiti dichiarati

Prima diagnosi soltanto, niente correzioni automatiche o breakpoint; niente
collaborazione/sincronizzazione cloud. I progetti sono locali al browser e richiedono
backup per trasferimento o conservazione. La release richiede HTTP/HTTPS e un
browser moderno con WebAssembly; non è un installer nativo né un HTML da aprire
con doppio clic. Il runtime è circa 15 MB prima della compressione di trasporto.
Le versioni Python/IR restano sperimentali.
