# Roadmap verificabile

## S0 — completato

Documenti fondanti, ADR, packaging, strumenti, CI e una pipeline per dichiarazioni.
Criterio: da una frase a token/AST/IR/mondo, errori italiani e test indipendenti
dal dominio. Nessun comando di gioco, motore di regole o editor.

## M1 — implementato in 0.1.0a2, verifica CI remota separata

Dichiarazioni, riferimenti in avanti, containment, nord/sud e inversioni esplicite.
Parser giocatore separato con guarda/prendi/inventario/nord/sud. Runtime di
transizioni ridotto, sostituibile dal futuro dispatcher; niente mini-rule-engine
ad hoc. Accettazione: transcript da Cucina a Corridoio e ritorno, presa una sola
volta, inventario corretto, direzione impossibile e oggetti assenti diagnosticati;
IR priva di stringhe da reinterpretare. Test non-IF preservati.

## M2 — implementato in 0.2.0a1

Schemi di proprietà, porte, chiavi, contenitori, stati aperto/chiuso, oggetto
diretto e indiretto. Accettazione: chiave errata, contenitore chiuso, doppie
posizioni e cicli rifiutati; invarianti del mondo testate su ogni transizione.

## M3 — implementato in 0.3.0a1

ADR su ordine/esiti/effetti, rulebook, condizioni, tracing, sostituzioni limitate.
Accettazione: ordine stabile, esiti distinti, loop diagnosticati, replay di una
sessione e trace verificabile. Migrazione delle azioni M1/M2 senza cambiarne
silenziosamente la semantica.

## M4 — implementato in 0.4.0a1

Composizione di file con `Includi`, riferimenti fra moduli, diagnostica sorgente,
deduplicazione e cicli. Punto iniziale esplicito. Namespace e tipi autore rinviati.

## Dopo M4 — senza promesse di data

Moduli e vocabolari; valori, funzioni, liste, tabelle ed enumerazioni; tempo,
eventi, scene; persone, gruppi, regioni e conversazioni. Parser permissivo con
sinonimi, pronomi, clitici e disambiguazione. Save/restore e solution tests prima
di esplorazione automatica. LSP/editor dopo stabilizzazione delle diagnosi.

Browser: confrontare runtime Python in WebAssembly e runtime autonomo dell'IR
con le stesse suite di conformità, misurando avvio e dimensioni. NLP opzionale
solo come produttore di candidati; nessuna dipendenza del nucleo.

## Prossimi pacchetti dopo l'analisi Inform 7

L'[analisi architetturale](docs/architettura/audit-inform7.md) motiva l'ordine.
Ogni pacchetto conserva il core indipendente dalla narrativa interattiva.

1. Gerarchia dei tipi e azioni dell'autore implementate in IR 8.
2. Sinonimi, locuzioni iniziali e separatori multiparola implementati in IR 11;
   disambiguazione a più turni, pronomi singolari, clitici standard e doppio
   clitico locativo implementati nella sessione; pattern liberi restano da completare.
3. Relazioni dinamiche direzionali, passaggio segreto, visibilità esplicita e
   oggetti di scenario implementati fino all'IR 13. Luce, trasparenza e punti di
   vista multipli restano pacchetti separati.
4. Elenchi e tabelle tipate con effetti transazionali implementati nell'IR 15;
   query per colonna e accesso avanzato alle collezioni restano da completare.
5. Persone e grafi di dialogo multi-turno implementati nell'IR 16; condizioni,
   effetti e conoscenze dei personaggi restano estensioni successive.
6. Scene temporali, turni e registro del punteggio implementati nell'IR 17;
   condizioni, effetti e ricorrenza delle scene restano estensioni successive.
7. Veicoli, salita/discesa e movimento atomico del conducente implementati
   nell'IR 18; passeggeri, carico e percorsi tipati restano estensioni successive.
8. Valuta tipata, saldo, merci, prezzi e acquisto atomico implementati nell'IR 19;
   più valute restano un'estensione successiva.
9. Mercanti, scorte, cassa e rivendita atomica implementati nell'IR 20;
   quantità, cataloghi generativi, contrattazione e mercanti itineranti restano
   estensioni successive.
10. Manifest multimediale validato e release web autosufficiente implementati
    nell'IR 21; video, media condizionali e controllo audio da regole restano
    estensioni successive.

11. Indice completo derivato dall'IR, ricerca locale ed esportazione JSON
    implementati nello Studio; viste incrociate e debugger restano pacchetti
    successivi.

12. Otto direzioni della rosa dei venti implementate nella stdlib, nel runtime e
    nell'atlante.

13. Livelli verticali `su`/`giù`, dichiarazione naturale con `sovrasta` e resa
    distinta nell'atlante implementati.

14. Navigazione `dentro`/`fuori`, dichiarazione naturale con `racchiude` e resa
    distinta dal contenimento implementate; i percorsi a senso unico sono ora
    dichiarabili con origine e destinazione esplicite e visibili nell'atlante.

15. Disambiguazione a più turni implementata per oggetto diretto e indiretto,
    con scelta per numero, nome o sinonimo, annullamento e stato condiviso fra
    CLI, Studio e release web.

16. Referente pronominale di sessione e clitici singolari standard implementati;
    accordo grammaticale, plurali e forme doppie non locative restano pacchetti
    separati.

17. Clitici diretti con complemento esplicito implementati per mettere, aprire e
    bloccare; il secondo oggetto conserva risoluzione, sinonimi e chiarimenti.

18. Clitici doppi locativi `metticelo`/`metticela` implementati con referenti
    diretto e indiretto separati nella sessione e diagnostica del ruolo assente.

19. Clitico locativo `mettici OGGETTO` implementato per conservare il nome
    diretto esplicito e richiamare la destinazione già risolta.

20. Avverbi locativi contestuali `lì`/`là` implementati in posizione finale di
    `metti`, con rifiuto delle destinazioni duplicate.

21. Pronomi risolti per ruolo implementati: l'oggetto diretto usa il referente
    diretto e il secondo oggetto preferisce il referente indiretto disponibile.

22. Passaggi a senso unico implementati per tutte le direzioni della stdlib,
    con assenza strutturale dell'inversa e freccia dedicata nell'atlante.

23. Creazione e rimozione dinamica di un singolo arco implementate con la
    qualificazione `a senso unico`, alias verticali e rollback transazionale.

24. Frasi naturali di movimento implementate con verbi italiani, preposizioni
    facoltative, forme classiche inglesi e correzioni direzionali precise.

25. Ritorno al luogo precedente implementato nella sessione con `indietro`,
    rispetto di porte, veicoli e archi a senso unico, senza cambiare l'IR.

26. Azione standard `attendere` implementata con alias italiani e classici,
    passaggio nel rulebook e avanzamento dell'orologio delle scene.

27. `guarda NOME`, `osserva`, `ispeziona` e `controlla` implementati come forme
    strutturate di `esaminare`, con compatibilità `look at` e disambiguazione comune.

28. Aiuto contestuale in partita implementato con `aiuto`, `comandi`, `help` e
    `?`, categorie abilitate dal mondo e azioni dell'autore, senza avanzare il turno.

29. Ripetizione dell'ultimo intento riuscito implementata con `ancora`, `ripeti`,
    `again` e `g`, conservando disambiguazione, rollback e avanzamento temporale.

Non si importeranno codice o testi Inform.

## Studio M5 — 0.5.0a1

Editor web, progetto virtuale, diagnostica con manuale, gioco, mappa SVG/JSON,
indice, trace, copioni verificabili e release web con runtime incluso. Restano
fuori scope collaborazione cloud, breakpoint, salvataggi del gioco ed eseguibili nativi.

Estensione compatibile completata: dodici direzioni, incluse rosa dei venti,
livelli e dentro/fuori, abbreviazioni classiche, nomi parziali e dialogo di
chiarimento a più turni, pronomi singolari e clitici standard. Plurali, accordo
grammaticale e forme doppie non locative restano futuri; i clitici diretti possono conservare un
complemento esplicito; `metticelo`, `metticela` e `mettici OGGETTO` riusano una
destinazione ricordata, disponibile anche come `lì` o `là` dopo `metti`.

Verifica didattica: il premio della lezione 6 è protetto anche dopo aver
lasciato e ripreso il tesoro; tutorial e regressione coprono la sequenza.

Verifica didattica: le lezioni 12, 13 e 34 distinguono il messaggio di prima
scoperta da quello delle visite successive tramite priorità esplicite.

Didattica: soluzione completa della seconda osservazione nella lezione 13,
con contatore locale, indizio progressivo e rivelazione unica verificati.

Dialoghi: una risposta errata ripresenta le scelte del nodo corrente,
conservando stato e turno; casi numerici e testuali verificati nella lezione 16.

Robustezza del giocatore: numeri molto lunghi nei dialoghi e nei chiarimenti
non interrompono la partita; zeri iniziali e cifre decimali Unicode preservati.

Chiarimenti: una risposta errata ripresenta nomi e numeri delle candidate,
con recupero verificato per risposta vuota, ambigua, assente e fuori intervallo.

Aiuto: le azioni dell'autore mostrano ora argomenti e separatori accettati,
con alias e forme a zero, uno o due oggetti derivati dal catalogo compilato.

Aiuto contestuale: durante chiarimenti e dialoghi ripresenta le alternative
attive con numerazione stabile e istruzioni per rispondere o annullare.

Chiarimenti: risposte esplicite `scegli NUMERO/NOME` supportate anche nei
mondi con dialoghi, senza perdere la domanda su risposte incomplete o ambigue.

Dialoghi: testo delle scelte accettato senza prefisso quando non coincide
con un comando; errori e ambiguità ripresentano le alternative correnti.

Chiarimenti: articoli e nomi quotati condividono le regole nominali dei comandi,
con conservazione della domanda per articoli isolati o nomi ancora ambigui.

Esame naturale: aggiunti i clitici di guarda, osserva, ispeziona e controlla,
con referente diretto condiviso e collisioni autore diagnosticate.

Didattica: esercizio delle due campane completato con sorgente copiabile,
copione e verifica di entrambe le scelte; chiarita la precedenza dei nomi esatti.

Didattica: laboratorio completo del contrappeso con fallimento transazionale,
confronto con chiusura riuscita e verifiche di grafo, proprietà e messaggi.

Dialoghi: risposte dirette fra virgolette supportate anche per etichette
che coincidono con comandi; articoli conservati e virgolette incomplete gestite.

Dialoghi: corretta la precedenza delle etichette con articolo dopo `scegli`,
senza perdere la compatibilità con risposte parziali come `la tempesta`.

Dialoghi: selezione parziale tollerante alla punteggiatura e agli apostrofi,
con precedenza delle etichette esatte e rifiuto delle risposte ambigue.

Didattica: laboratorio dialogo e tempo con errori senza consumo di turno,
scena conclusa durante la conversazione e premio temporale non duplicabile.

Consultazioni: tempo, punteggio e saldo disponibili durante dialoghi e
chiarimenti, senza perdere la domanda né avanzare l'orologio.

Didattica: soluzione con due mercanti, chiarimento del compratore, trasferimento
di scorta e rifiuti atomici per venditore sbagliato o fondi insufficienti.

Sintassi autore: punto iniziale esprimibile con `nel`, `nello` e `nell'`,
oltre a `nella`, con invariati controlli di unicità e destinazione.

Sintassi autore: `Inizia nel Mercato Coperto.` accetta nomi non quotati,
riusando le dichiarazioni nominali senza modificare i percorsi di inclusione.

Didattica: laboratorio della lezione 4 con testi separati, sorgenti copiabili,
copione invariato e diagnosi localizzate per modulo assente o nome errato.

Didattica: soluzione completa della lezione 18 con due veicoli, cambio controllato,
parcheggio persistente e percorso negativo senza uscite.

Didattica: soluzione completa della mappa già pagata nella lezione 19,
con saldo progressivo, recupero senza addebito e rifiuti atomici verificati.

Didattica: laboratorio di due scene sovrapposte con tabella dei turni,
premio zero e regressioni su stato indipendente e conclusioni non ripetute.

Correzione didattica: il taccuino non dichiara più un indizio già annotato
durante la prima raccolta; priorità e regressioni coprono orma e fibra.
