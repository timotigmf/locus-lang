# Roadmap verificabile

## S0 — questa sessione

Documenti fondanti, ADR, packaging, strumenti, CI e una pipeline per dichiarazioni.
Criterio: da una frase a token/AST/IR/mondo, errori italiani e test indipendenti
dal dominio. Nessun comando di gioco, motore di regole o editor.

## M1 — prima storia giocabile (versione 0.1)

Dichiarazioni, riferimenti in avanti, containment, nord/sud e inversioni esplicite.
Parser giocatore separato con guarda/prendi/inventario/nord/sud. Runtime di
transizioni ridotto, sostituibile dal futuro dispatcher; niente mini-rule-engine
ad hoc. Accettazione: transcript da Cucina a Corridoio e ritorno, presa una sola
volta, inventario corretto, direzione impossibile e oggetti assenti diagnosticati;
IR priva di stringhe da reinterpretare. Test non-IF preservati.

## M2 — oggetti e azioni parametrizzate

Schemi di proprietà, porte, chiavi, contenitori, stati aperto/chiuso, oggetto
diretto e indiretto. Accettazione: chiave errata, contenitore chiuso, doppie
posizioni e cicli rifiutati; invarianti del mondo testate su ogni transizione.

## M3 — regole

ADR su ordine/esiti/effetti, rulebook, condizioni, tracing, sostituzioni limitate.
Accettazione: ordine stabile, esiti distinti, loop diagnosticati, replay di una
sessione e trace verificabile. Migrazione delle azioni M1/M2 senza cambiarne
silenziosamente la semantica.

## Dopo M3 — senza promesse di data

Moduli e vocabolari; valori, funzioni, liste, tabelle ed enumerazioni; tempo,
eventi, scene; persone, gruppi, regioni e conversazioni. Parser permissivo con
sinonimi, pronomi, clitici e disambiguazione. Save/restore e solution tests prima
di esplorazione automatica. LSP/editor dopo stabilizzazione delle diagnosi.

Browser: confrontare runtime Python in WebAssembly e runtime autonomo dell'IR
con le stesse suite di conformità, misurando avvio e dimensioni. NLP opzionale
solo come produttore di candidati; nessuna dipendenza del nucleo.

## Prossimi cinque task

1. Precisare AST/IR delle relazioni S1 e i conflitti fra nomi e delimitatori.
2. Implementare risoluzione in due passaggi, riferimenti in avanti e relative diagnosi.
3. Implementare relazioni del mondo con vincoli e policy nord/sud nella stdlib.
4. Introdurre intenti del giocatore e transizioni M1 con transcript di accettazione.
5. Completare CLI `gioca`, esempi eseguibili e verifiche dei pacchetti sui quattro sistemi.
