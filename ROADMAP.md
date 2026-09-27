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
2. Estendere i comandi a grammatiche italiane con sinonimi, forme flesse e
   disambiguazione a più turni.
3. Introdurre relazioni dinamiche e visibilità, con un passaggio segreto reale
   come criterio di accettazione.
4. Aggiungere liste, tabelle ed effetti transazionali sulle collezioni.
5. Costruire persone e dialoghi strutturati prima di scene, veicoli e commercio.

Scene/tempo/punteggio, veicoli, valuta/commercio, multimedia e indici completi
seguono in pacchetti separati. Non si importeranno codice o testi Inform.

## Studio M5 — 0.5.0a1

Editor web, progetto virtuale, diagnostica con manuale, gioco, mappa SVG/JSON,
indice, trace, copioni verificabili e release web con runtime incluso. Restano
fuori scope collaborazione cloud, breakpoint, salvataggi del gioco ed eseguibili nativi.

Estensione compatibile completata: quattro direzioni cardinali, abbreviazioni
classiche, nomi parziali non ambigui e disambiguazione esplicita. Diagonali,
alto/basso, dentro/fuori e dialogo di chiarimento a più turni restano futuri.
