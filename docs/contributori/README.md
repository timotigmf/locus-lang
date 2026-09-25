# Strategia di testing

Test unitari: lessico, EOF, intervalli, Unicode composto/decomposto, articoli,
nomi composti e sintassi negativa; duplicati e tipi sconosciuti nella semantica.
Test integrazione: sorgente → AST → IR → mondo, catalogo non-IF, CLI e JSON.
Regressioni: forme apostrofate, separatori, assenza di punto e collisioni canoniche.
I blocchi Markdown `ita` e gli esempi `.ita` sono compilati automaticamente.

Test architetturali verificano gli import vietati: compilatore senza stdlib/runtime,
runtime senza frontend. Sono guardrail di dipendenze statiche, non prove formali.
Determinismo: compilazioni ripetute e indipendenza delle istanze. Packaging:
build wheel/sdist e comando installato fuori dal repository.

M1 aggiungerà transcript di soluzioni, errori del giocatore e invarianti di
posizione; M2 test generativi per grafi e containment; M3 trace ed esiti dei
rulebook, replay e budget eventi. Non imporre una percentuale di coverage come
sostituto dei casi semantici. Aggiungere benchmark solo con carichi significativi.

La CI copre Python 3.11–3.14 su Linux e smoke/test 3.11 su Windows e sui due macOS.
Solo le verifiche eseguite sul runner reale certificano quella combinazione.
