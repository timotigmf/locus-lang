# ADR 0007 — composizione dei sorgenti e ingresso esplicito

Stato: accettato per M4.

## Contesto e decisione

Le regole M3 rendono utile separare mondo, oggetti e comportamento. Prima di
namespace e pacchetti serve un caricatore prevedibile con diagnosi originali.
Introduciamo `Includi "percorso".` e `Inizia nella "nome".`. Il frontend riconosce
le direttive senza I/O; `project.load_project` risolve il grafo dei file e produce
un Program espanso. Il compilatore puro rifiuta inclusioni non risolte.

Visita in profondità, postordine e deduplicazione dei percorsi canonici. Tutte
le dipendenze precedono il chiamante, indipendentemente dalla posizione delle
direttive. Priorità delle regole invariate; pareggi seguono l'ordine espanso.
Span originali conservati e ordine dei file esplicito, anche per ordinare relazioni
con offset locali che ripartono da zero. Errori ciclici diagnosticati prima della
deduplicazione. File e profondità limitati per invocazione, nessuna cache globale.

La stdlib valida l'ingresso come stanza; il core conosce solo un ID opzionale.
IR versione 5. Nessun percorso entra nell'IR come istruzione eseguibile; le origini
delle regole restano metadati diagnostici. Il runtime rimane privo di file I/O.

## Alternative

Concatenare stringhe distruggerebbe le posizioni sorgente; scartato. Includere nel
punto esatto della direttiva richiederebbe un AST uniforme ordinato e introdurrebbe
una semantica da preprocessore; rimandato. Namespace completi ora aumenterebbero
scope e regole di risoluzione senza casi d'uso sufficienti; rinviati a una specifica.
Avvio implicito solamente: conservato come compatibilità, ma insufficiente quando
le dipendenze dichiarano stanze prima della storia principale.

## Conseguenze e revisione

Un solo spazio dei nomi; collisioni fra moduli sono errori. Include condivisi non
eseguono due volte regole. Il caricatore legge file locali indicati dall'autore,
anche fuori dalla directory tramite `..`/symlink: non è un sandbox. Percorsi assoluti,
URL e sintassi specifica Windows rifiutati per portabilità. Revisione prima di
namespace, package manager, caricamento remoto, editor incrementale o filesystem virtuale.
