# Stato e verifiche dello Studio 0.5

## Funzioni reali

Editor CodeMirror con sintassi LOCUS, file e punto d'ingresso, salvataggio locale,
backup/importazione JSON, compilazione con il motore Python originale, gioco e
riavvio, test separati con confronto dei transcript, mappa SVG/JSON, indice delle
entità, trace delle regole e diagnosi navigabili con riferimenti al manuale.
Esportazione ZIP del giocatore statico con sorgente della storia e runtime inclusi.

## Controlli eseguiti

- 705 test Python passati, incluse rosa dei venti, direzioni verticali e
  dentro/fuori, alias classici, nomi parziali, sinonimi dichiarati, metadati,
  chiarimenti a più turni, pronomi, clitici singolari, complementi espliciti e
  clitici doppi locativi, tutorial,
  regole transazionali, adapter Studio e confine del progetto virtuale.
- Ruff, controllo formato e mypy strict passati.
- Build wheel e sdist 0.5.0a1 riuscita; build web statica riuscita.
- Sedici test browser reali passati in Chrome su macOS: flusso compilazione/gioco,
  sorgente unico con titolo/autore, `e`/`o` senza uscita, `x scatola` tramite
  sinonimo, `prendi chiave`, manuale con copia, copione verificato, mappa
  esportata, ZIP estratto e giocato su un percorso diverso;
  diagnosi E102 con file originale e manuale, persistenza, gestione file e backup,
  test negativo, migrazione non distruttiva del vecchio esempio modulare, menu
  mobile e assenza di overflow orizzontale; azioni tipate; passaggio segreto con
  navigazione inversa e mappa aggiornata durante la sessione; scenario non
  trasportabile e rivelazione di un oggetto inizialmente invisibile; elenchi,
  tabelle, dialoghi, scene, veicoli, acquisti e mercanti. Il flusso principale
  percorre una diagonale, un livello verticale e un passaggio interno, torna
  tramite le inverse e controlla etichette, tratteggio e linea puntinata nell'SVG.
  Un test dedicato verifica la domanda ambigua e la risposta successiva tramite
  un sinonimo nello stesso runtime della release, quindi richiama l'oggetto con
  `esaminala`, lo colloca con `mettila nella scatola` e riusa la destinazione con
  `metticela` per un secondo oggetto.
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

Il 26 settembre 2026 la repository è stata resa pubblica con autorizzazione
esplicita dell'autore. Prima del cambio sono stati controllati i 250 blob della
cronologia disponibile: nessuna corrispondenza per i formati di credenziali cercati
né file con nomi da segreti o documenti PDF/DOCX. È un controllo mirato, non una
garanzia assoluta di assenza di informazioni riservate.

GitHub Pages è abilitato con GitHub Actions. Il workflow `Studio web` pubblica
il ramo `codex/studio-web` solo dopo build, controlli di formato e test browser.
Le pull request non pubblicano. Indirizzo configurato:
https://timotigmf.github.io/locus-lang/ . Controllare l'esito del job `deploy`
prima di considerare disponibile una nuova versione.

Il precedente tentativo su Sites non ha prodotto una distribuzione: il servizio
ha restituito HTTP 500 durante il trasferimento. Il sito registrato ha identificativo
`appgprj_6ab7b99c5a2481918493e8c5c9d48a91`; non crearne un duplicato.
I checkout locali `hosting/studio` e `hosting/studio-source` restano esclusi da Git.
GitHub Pages è ora la destinazione di pubblicazione; Sites non è utilizzato.

## Limiti dichiarati

Prima diagnosi soltanto, niente correzioni automatiche o breakpoint; niente
collaborazione/sincronizzazione cloud. I progetti sono locali al browser e richiedono
backup per trasferimento o conservazione. La release richiede HTTP/HTTPS e un
browser moderno con WebAssembly; non è un installer nativo né un HTML da aprire
con doppio clic. Il runtime è circa 15 MB prima della compressione di trasporto.
Le versioni Python/IR restano sperimentali.
