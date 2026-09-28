# Linguaggio

La [specifica normativa M1](../../LANGUAGE_SPEC.md) distingue funzioni eseguibili
da funzionalità future. Il suffisso alpha non autorizza ambiguità silenziose:
un cambiamento di semantica deve aggiornare specifica e test. Per la morfologia
italiana si partirà da articoli e sintagmi nominali; accordi, pronomi e clitici
richiederanno decisioni separate nei due parser.

La versione attuale è descritta nelle specifiche [M2](milestone-2.md),
[M3](milestone-3.md), [M4](milestone-4.md) e in
[Metadati e vocabolario](metadati-vocabolario.md). I
[tipi definiti dall'autore](tipi-autore.md) aggiungono una gerarchia nominale a
ereditarietà singola, usata in modo uniforme dal compilatore e dal runtime.
Le [azioni definite dall'autore](azioni-autore.md) collegano comandi italiani,
argomenti tipati e regole senza interpretazione testuale nel runtime.
La [grammatica dei comandi dell'autore](grammatica-comandi-autore.md) aggiunge
sinonimi espliciti, separatori alternativi e preposizioni articolate nell'IR 9.
Le [forme multiparola](comandi-multiparola.md) aggiungono locuzioni iniziali
deterministiche e diagnostica delle collisioni di prefisso nell'IR 10.
I [separatori multiparola](separatori-multiparola.md) aggiungono locuzioni fisse
fra due oggetti e articolazione dell'ultima preposizione nell'IR 11.
Le [relazioni dinamiche](relazioni-dinamiche.md) permettono alle regole di creare
o rimuovere passaggi cardinali transazionali nell'IR 12.
La [visibilità esplicita](visibilita-scenario.md) aggiunge oggetti nascosti e il
tipo ambientale non trasportabile `scenario` nell'IR 13.
Gli [elenchi tipati](liste-tipate.md) aggiungono collezioni omogenee, condizioni
di appartenenza ed effetti transazionali nell'IR 14.
Le [tabelle tipate](tabelle-tipate.md) aggiungono colonne nominate, righe
eterogenee e mutazioni atomiche nell'IR 15.
I [dialoghi strutturati](dialoghi-strutturati.md) aggiungono persone, nodi,
scelte e conversazioni multi-turno nell'IR 16.
Le [scene temporali](scene-tempo-punteggio.md) aggiungono turni, ciclo di vita,
punteggio e registro dei premi nell'IR 17.
I [veicoli](veicoli.md) aggiungono un tipo standard, salita, discesa e movimento
congiunto del conducente nell'IR 18.
