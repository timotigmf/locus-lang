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
