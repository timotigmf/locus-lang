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
   clitici, pattern liberi e disambiguazione a più turni restano da completare.
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
    distinta dal contenimento implementate; i percorsi a senso unico restano un
    pacchetto separato.

Non si importeranno codice o testi Inform.

## Studio M5 — 0.5.0a1

Editor web, progetto virtuale, diagnostica con manuale, gioco, mappa SVG/JSON,
indice, trace, copioni verificabili e release web con runtime incluso. Restano
fuori scope collaborazione cloud, breakpoint, salvataggi del gioco ed eseguibili nativi.

Estensione compatibile completata: dodici direzioni, incluse rosa dei venti,
livelli e dentro/fuori, abbreviazioni classiche, nomi parziali non ambigui e
disambiguazione esplicita. Il dialogo di chiarimento a più turni resta futuro.
