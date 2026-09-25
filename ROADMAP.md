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

1. Integrare M1 dopo revisione e CI, confermando la sintassi di avvio esplicito.
2. Specificare proprietà tipate e invarianti di containment per M2.
3. Modellare contenitori aperti/chiusi con test sulle transizioni.
4. Introdurre porte, chiavi e intenti con oggetto diretto/indiretto.
5. Progettare ordine, esiti ed effetti del rule engine M3 in un ADR dedicato.
