# Studio LOCUS — scrivere, provare e pubblicare

Lo Studio è l'ambiente web di LOCUS 0.5.0a1. Compilatore e gioco girano nel browser,
in un processo di lavoro separato dall'editor. Non occorre installare Python per
usare il sito. I sorgenti non vengono inviati a un servizio di compilazione.

Apri [LOCUS Studio online](https://timotigmf.github.io/locus-lang/).

## Primo progetto

All'apertura trovi il faro di Selce completo in `storia.locus`. Il sorgente
comincia con `Titolo:` e `Autore:`, poi descrive direttamente il mondo; `Includi`
compare soltanto nel capitolo avanzato sui progetti. A sinistra scegli un file,
al centro scrivi, a destra provi la storia. **Compila** verifica
il progetto; **Compila e prova** avvia una nuova sessione. Puoi usare anche
Ctrl+Invio o Cmd+Invio nell'editor. **Interrompi** riavvia il motore conservando
il sorgente: ricompila prima di continuare.

L'editor offre colori per la sintassi LOCUS, numeri di riga, rientri, annulla/ripeti,
completamento delle parole chiave e ricerca/sostituzione (Ctrl/Cmd+F). Il controllo
semantico avviene quando compili, non continuamente mentre scrivi.

**Nuovo progetto** crea titolo, autore e stanza iniziale. Il pulsante **＋** aggiunge file;
puoi rinominarli o eliminarli. Dopo una rinomina aggiorna le direttive `Includi`:
non è un refactoring automatico. Il selettore del file principale stabilisce
quale sorgente avvia il caricamento. Su schermi stretti apri il menu **Progetto**.

## Salvare e importare

Le modifiche vengono salvate nel browser, su questo dispositivo e per questo
indirizzo del sito. Non c'è sincronizzazione cloud o con GitHub. La cancellazione
dei dati del browser può rimuoverle. **Scarica progetto** crea un backup JSON
con file, titolo e copioni; **Importa progetto / file** riapre il JSON o aggiunge
sorgenti `.locus`. Per conservare le cartelle usa il backup JSON; l'importazione
di singoli file usa i loro nomi, senza ricostruire le directory originarie.

Limiti attuali: 256 file e 2 MB complessivi di sorgenti. I file devono restare
nel progetto virtuale; un'inclusione che ne esce viene rifiutata. Non sono eseguiti
sorgenti Python arbitrari: l'editor accetta il linguaggio LOCUS.

## Errori e manuale

Il pannello **Diagnostica** mostra codice stabile, categoria, spiegazione,
file, riga e colonna, con suggerimento e collegamento al capitolo pertinente.
Cliccando la posizione si apre il file e si porta il cursore al punto segnalato;
il tratto interessato è sottolineato nell'editor. I riferimenti hanno origine
nel compilatore, non sono deduzioni di un modello generativo.

Il compilatore si ferma al **primo errore**. Correggilo e ricompila per trovare
il successivo. Non promettiamo correzioni automatiche della semantica. Gli span
di alcune diagnosi coprono un'intera dichiarazione/regola, come nella CLI.
Il manuale incorporato è ricercabile per capitolo; la guida dell'autore è la
pagina iniziale e ogni blocco di codice offre **Copia codice**. Comprende un corso
in ventisei lezioni, specifiche e tutorial. L'Indice del mondo mostra anche
dialoghi, scene, veicoli, mercanti e commercio compilati e aggiorna proprietà,
righe delle tabelle, posizione dei mezzi, saldo, cassa e scorte dopo ogni comando.

Quando modifichi il sorgente, il gioco precedente viene disabilitato e mappa e
indice sono da ricompilare. Non si mescolano una versione vecchia della storia e
un sorgente nuovo. **Ricomincia** resetta la sessione del progetto compilato.

## Mappa e indice

**Mappa** mostra luoghi, rosa dei venti, livelli verticali, dentro/fuori, porte,
veicoli e punto iniziale. I
passaggi dinamici compaiono o scompaiono subito dopo il comando che li modifica. Puoi
allargare/ridurre la vista ed esportare SVG o dati JSON. L'SVG è un file vettoriale
riutilizzabile e stampabile. È uno schema logico dello stato corrente, non una
mappa delle posizioni del giocatore né un impaginatore geografico: collegamenti
ciclici o complessi possono avere linee incrociate.

**Indice del mondo** elenca metadati, gerarchie dei tipi, entità, proprietà,
relazioni, vocabolario, azioni, regole, tabelle, dialoghi, scene e risorse
compilati. Per ogni dialogo mostra persona, numero di nodi e nodo iniziale; per
ogni scena mostra turni e punti; per ogni veicolo tipo e stanza corrente; per il
commercio mostra valuta, saldo, mercanti, cassa, prezzi, rivendita, posizione e
venditore corrente. Il filtro cerca in tutte le righe e **Scarica JSON** esporta
l'IR completa. Consulta il [riferimento dell'Indice](indice-del-mondo.md).
**Regole e trace**
mostra le regole considerate nell'ultima azione, con esito e collegamento alla
riga del sorgente, il percorso del dialogo e gli eventi temporali con variazione
del punteggio. Non è ancora un debugger a passi con breakpoint.

Nel riquadro di gioco, una domanda su più oggetti resta attiva: rispondi con il
numero, il nome o un sinonimo. `annulla` la chiude; anche un nuovo comando completo
la sostituisce. La stessa sequenza funziona nei copioni e nelle release esportate.

## Test e transcript

Ogni copione ha nome, comandi (uno per riga) e uscita attesa facoltativa.
L'uscita include la descrizione iniziale e ogni risposta, separate da a capo,
senza prompt né comandi digitati; termina con un a capo. I test dell'esempio
mostrano il formato corretto.

**Esegui test** o **Esegui tutti** usa una sessione nuova, separata dal gioco
interattivo. Se l'uscita attesa è presente, il confronto è esatto (CRLF viene
normalizzato); il resoconto mostra la prima riga diversa. Senza atteso la prova
è **esplorativa**, non un test superato. Il comando `esci` termina il copione:
il resoconto indica quanti comandi sono stati eseguiti. Massimo 500 comandi per
copione. Puoi scaricare l'ultimo transcript e ispezionare il risultato completo.

## Esportare una release

**Esporta release** ricompila se necessario e produce uno ZIP con giocatore,
storia, motore LOCUS, runtime WebAssembly e licenze delle dipendenze. Non dipende
da CDN. I sorgenti della storia rimangono leggibili in `project.json`;
non è un formato cifrato né un compilatore verso eseguibili nativi.

1. Estrai lo ZIP.
2. Carica **tutti** i file su un hosting statico HTTP/HTTPS (anche una sottocartella).
3. Apri l'indirizzo di `index.html` nel browser.

Per una prova locale puoi usare `python -m http.server 8000` nella cartella
estratta e aprire `http://localhost:8000`. Python serve solo a fornire HTTP in
questo esempio: sul sito, chi gioca non deve installarlo. Il doppio clic sul file
HTML (`file://`) non è supportato. Puoi incorporare il giocatore sul tuo sito
tramite un iframe che punta all'indirizzo della release.

## Immagini e suoni

Il pulsante **＋** della sezione **Risorse** importa PNG, JPEG, WebP, GIF, MP3,
Ogg e WAV come `media/NOMEFILE`. Il sorgente li associa alle entità con
`immagine` o `suono`; `testo alternativo` descrive le immagini. Backup JSON e
release ZIP contengono i byte. Consulta il
[riferimento multimediale](../linguaggio/risorse-multimediali.md) per limiti e
diagnostica `E126`.

Il target è un browser moderno con WebAssembly e module worker su Windows,
macOS, Linux e dispositivi mobili compatibili. Non equivale a supportare ogni
sistema operativo o browser storico. Il primo caricamento trasferisce il runtime;
serve memoria sufficiente. La release non include salvataggi/restore del gioco,
installer nativi, app store o pubblicazione automatica sul sito dell'autore.

Lo Studio e le release sono un'anteprima verificata, non ancora una versione
stabile di Inform o un equivalente di tutte le sue funzionalità.
