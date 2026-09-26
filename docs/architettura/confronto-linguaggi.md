# Riferimenti pubblici e obiettivi misurabili

Consultazioni del 25–27 settembre 2026. Non è un audit riga per riga, un benchmark o una
prova di superiorità di LOCUS. Nessun codice esterno incorporato. «Dialogo» viene
qui interpretato come **Dialog**, il linguaggio IF; altri progetti omonimi non
sono stati identificati né assimilati automaticamente.

## Favella 1

Repository pubblica [Pitz72/FAVELLA1](https://github.com/Pitz72/FAVELLA1), revisione
`f1cc7e7e870b53cc2d6fe5fa218d0254c2e8fd8d`.
[Licenza MIT](https://github.com/Pitz72/FAVELLA1/blob/f1cc7e7e870b53cc2d6fe5fa218d0254c2e8fd8d/LICENSE).
Esaminati l'inizio di [compilatore.py](https://github.com/Pitz72/FAVELLA1/blob/f1cc7e7e870b53cc2d6fe5fa218d0254c2e8fd8d/compilatore.py)
e strutture/operandi in [strutture.py](https://github.com/Pitz72/FAVELLA1/blob/f1cc7e7e870b53cc2d6fe5fa218d0254c2e8fd8d/strutture.py).

Il frontend descrive una pipeline Lark con raccolta di nomi prima del parsing
successivo; gli operandi sono oggetti distinti e la casualità del mondo è seedata.
Indicazioni per LOCUS: confrontare una grammatica dichiarativa prima delle regole,
conservare valori strutturati e prevedere una sorgente casuale riproducibile.
LOCUS oggi sceglie nomi quotati per collisioni sintattiche e tipi rigidi senza
coercizioni implicite. Non viene riprodotto l'algoritmo di Favella.

## Dialog

Repository pubblica [Dialog-IF/dialog](https://github.com/Dialog-IF/dialog), revisione
`3fbdbef41b259de44fbde98dfcc033b6bbbb514a`.
[Licenza](https://github.com/Dialog-IF/dialog/blob/3fbdbef41b259de44fbde98dfcc033b6bbbb514a/license.txt):
BSD a due clausole per compilatore/debugger/librerie, con alternativa che aggiunge
un'eccezione per porzioni incorporate nell'output; componenti terzi hanno condizioni
specifiche nello stesso file.

Esaminate le sezioni porte e accesso in
[stdlib.dg](https://github.com/Dialog-IF/dialog/blob/3fbdbef41b259de44fbde98dfcc033b6bbbb514a/stdlib.dg).
Il blocco del passaggio e i limiti di visibilità/raggiungibilità sono distinti.
Indicazione per LOCUS: non basta trovare un nome per autorizzare un'azione;
verificare gli antenati del containment e lo stato della porta. M2 usa contenitori
opachi; illuminazione e trasparenza rimangono future. Nessun predicato copiato.

## Inform 7

Repository pubblica [ganelson/inform](https://github.com/ganelson/inform), revisione
`5c7ba42b74db69b93b1290453c65189fa60cfc67`.
[Licenza principale Artistic 2.0](https://github.com/ganelson/inform/blob/5c7ba42b74db69b93b1290453c65189fa60cfc67/LICENSE),
salvo componenti con licenze proprie, come segnala il README.
Sono stati inventariati l'intero sottoprogetto `inform7`, test e documentazione;
letti gli indici di tutti i moduli e campioni mirati dei contratti principali.
Metodi, risultati e limiti sono registrati nell’[analisi architetturale
completa](audit-inform7.md). Non si afferma una revisione riga per riga.

La distribuzione distingue compilatore generico, conoscenza, strato IF, runtime,
grammatica dei comandi, test e documentazione. Questo sostiene un piano concreto
per tipi, azioni, lessico italiano, relazioni dinamiche, dialogo, scene, veicoli e
commercio; non implica che l'IR di LOCUS sia equivalente a Inter né più potente.
LOCUS mantiene il proprio formato strutturato e nessuna compatibilità binaria o
riuso di codice Inform.

## Cosa significa migliorare LOCUS

| Capacità | Evidenza attuale | Passo necessario |
| --- | --- | --- |
| Sorgente italiano | esempi M1/M2 compilati nei test | ampliare sintassi con corpus positivo/negativo |
| Tipi e valori | proprietà intere/testuali/logiche, niente coercizioni | espressioni, funzioni, collezioni |
| Indipendenza da IF | cataloghi e verbi di un dominio non narrativo nei test | moduli dichiarativi |
| Mondo coerente | cicli, doppie posizioni, visibilità e porte verificati | supporti, persone, regioni, ereditarietà |
| Regole ispezionabili | architettura proposta | M3 con priorità, esiti, trace |
| Portabilità | Python puro, CI su quattro piattaforme | conformità di un backend browser |
| Italiano del giocatore | due oggetti, articoli, nomi quotati | sinonimi, anafore, clitici e disambiguazione interattiva |

Questa tabella è una lista di prove per LOCUS, non una classifica dei concorrenti.
Le capacità avanzate dei riferimenti non vengono date per implementate in LOCUS.
