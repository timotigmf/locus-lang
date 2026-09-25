# ADR 0004 — relazioni e sessione del primo milestone

Stato: accettato, 2026-09-25. Implementa M1, non M2/M3.

## Decisioni

AST: dichiarazioni con collocazione opzionale e asserzioni di relazione separate.
`nella` delimita il tipo nella dichiarazione; `a PREDICATO della` introduce una
relazione. Il parser non ha un elenco di direzioni. `è`, `nella`, `della` sono
parole riservate nei nomi non quotati: le collisioni producono un errore esplicito.

Il compilatore riceve schemi di relazione insieme ai tipi. Ogni schema dichiara
ID, tipi ammessi agli estremi, eventuale inversione degli operandi sintattici e
ID della relazione inversa. Le relazioni M1 sono funzionali per sorgente e
irriflessive. Si raccolgono prima tutte le entità, poi si risolvono i riferimenti.
Non esiste creazione implicita. Una relazione ripetuta identica è idempotente;
un'altra destinazione per lo stesso soggetto/predicato è un conflitto.

La stdlib specifica `nella` (cosa → stanza) e nord/sud (stanza → stanza).
«B è a nord della A» diventa `A --nord--> B` e `B --sud--> A`.
Questa convenzione normalizzata permette al runtime di seguire archi senza
reinterpretare italiano. IR versione 2: relazioni esplicite con ID risolti.
Nessun loader JSON o compatibilità IR v1: formato ancora sperimentale.

Il mondo generale resta immutabile e indipendente da IF. La sessione narrativa
nella stdlib aggiunge stanza corrente e inventario immutabile. Containment IR è
lo stato iniziale; una cosa presa è posseduta dal giocatore e non più visibile
nella stanza. Una transizione restituisce nuova sessione ed evento strutturato.
Il renderer produce testo italiano separatamente. Non introduciamo un falso
motore di regole: questa tabella di azioni M1 sarà sostituita in M3.

Prima stanza dichiarata = punto iniziale provvisorio. Compilare un mondo senza
stanze è valido; avviare una sessione IF senza stanze è errore di gioco. Oggetti
senza collocazione sono validi ma non raggiungibili. Queste policy sono nella
stdlib, non nel compilatore.

## Alternative e conseguenze

Tipi IF hardcoded nel compilatore: rifiutati. Parser che esegue direttamente
azioni: rifiutato. Framework di plugin o regole completo: prematuro.
Schemi espliciti sono più piccoli e verificabili; la firma mantiene il catalogo
tipi esistente e aggiunge `relations=` keyword-only. Senza schemi, il compilatore
accetta dichiarazioni S0 ma rifiuta relazioni con E104.

Parser giocatore indipendente: comandi esatti, articoli opzionali per `prendi`,
nessuna inferenza anaforica. Intenti riconosciuti non garantiscono che l'oggetto
sia presente: la sessione verifica visibilità, portabilità e possesso. M1 non
implementa containment arbitrario, clitici, porte o contenitori.

Prima di M2 progettare proprietà e schemi più espressivi; prima di save/restore
stabilire identità persistenti e validazione dei dati esterni. Prima di release
stabile sostituire la prima stanza implicita con una dichiarazione di avvio.
