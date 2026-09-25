# ADR 0005 — proprietà tipate e mondo M2

Stato: accettato per M2; sostituisce i limiti di posizione e proprietà di ADR 0004.

Proprietà autore: `La massa è una proprietà numerica.`, `La chiave ha massa 2.`.
Tre domini iniziali: numerica (intero), testuale (stringa), logica (vero/falso).
I valori sono tipati esplicitamente: nessuna coercizione fra booleani e interi.
Proprietà definite dall'autore applicabili a tutte le entità, con default 0/""/falso.
La stdlib registra descrizione e stato; stato ha valori aperto/chiuso/bloccato.
Cataloghi e valori attraversano l'IR senza dipendere dalla sintassi narrativa.

Gli schemi di relazione ammettono insiemi di tipi e vincolo aciclico. Containment
è funzionale e aciclico; gli estremi possono essere cose/chiavi/contenitori e
stanze/contenitori. Il compilatore verifica i cicli, senza conoscere il dominio.
La stdlib verifica anche la topologia delle porte: due stanze distinte già
collegate, al massimo una porta per passaggio, estremi completi.

Sintassi `X collega A a B`: due relazioni generiche (collega da/collega a).
Verbi binari come `apre` vengono registrati dalla stdlib nel frontend: non sono
nomi di azioni eseguite dal compilatore. Nomi quotati consentono delimitatori
senza indovinare; verbi registrati sono riservati nei nomi non quotati.

Sessioni: mondo immutabile aggiornato per ogni transizione più inventario delle
entità direttamente possedute. Un contenitore trasportato mantiene i figli;
visibilità e possesso seguono la catena di containment. Gli antenati chiusi
impediscono l'accesso, anche nell'inventario. Nessuna doppia sorgente autorevole:
una cosa è contenuta, nell'inventario, oppure fuori scena. Ogni transizione riuscita
è validata; quelle fallite lasciano lo stato identico. Porte non trasportabili.

Alternative scartate: aggiungere booleani indipendenti aperto/bloccato (stati
contraddittori), mutare il programma compilato, eseguire testo sorgente nel runtime,
introdurre un rule engine improvvisato. M3 rimane dedicato alle regole.

Conseguenze: IR versione 3, API Python sperimentali estese; la sintassi M1 rimane
supportata. M2 non implementa ereditarietà, aritmetica, funzioni o tipi definiti
dall'autore. Gli interi non implicano ancora espressioni: dichiarazioni e valori
vengono prima del sistema di calcolo. Prima di espressioni/regole resta valido
il confronto con un parser dichiarativo richiesto dall'ADR 0001.
