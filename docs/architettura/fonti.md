# Fonti e provenienza

Consultate dal 2026-09-25 al 2026-09-27. Implementazione originale; nessun frammento di codice
preso dai sistemi sotto. Licenze indicate per i candidati parser, non come
licenza di questo repository. Riverificare versione e licenza prima del riuso.

| Fonte primaria | Licenza / stato | Idea ricavata | Codice riusato |
| --- | --- | --- | --- |
| [Lark parser](https://lark-parser.readthedocs.io/en/stable/parsers.html), [licenza](https://github.com/lark-parser/lark/blob/master/LICENSE) | MIT | confronto LALR/Earley e gestione ambiguità | nessuno |
| [ANTLR target Python](https://www.antlr.org/api/JavaTool/org/antlr/v4/codegen/target/Python3Target.html), [download](https://www.antlr.org/download.html), [licenza](https://www.antlr.org/license.html) | BSD-3-Clause | generazione e runtime distinti | nessuno |
| [pyparsing](https://pyparsing-docs.readthedocs.io/en/latest/), [licenza](https://github.com/pyparsing/pyparsing/blob/master/LICENSE) | MIT | combinatori in Python | nessuno |
| [argparse](https://docs.python.org/3/library/argparse.html) | stdlib Python, PSF | CLI standard con subcomandi | libreria usata, nessun codice copiato |
| [Click](https://click.palletsprojects.com/en/stable/) | candidato non incorporato | alternativa CLI | nessuno |
| [PEP 621](https://peps.python.org/pep-0621/), [guida PyPA](https://packaging.python.org/en/latest/tutorials/packaging-projects/), [Hatch](https://hatch.pypa.io/latest/) | specifiche/documentazione; backend solo build | metadata dichiarativi e wheel | nessuno |
| [Inform 7](https://github.com/ganelson/inform/tree/5c7ba42b74db69b93b1290453c65189fa60cfc67/inform7) | Artistic-2.0 principale; componenti terzi separati | moduli, passaggi semantici, grammatica tipata, test e manuale/ricettario | nessuno |

Non si rivendica una revisione riga per riga del codice Inform né superiorità
tecnica dimostrata. Il confronto è architetturale, non una misurazione prestazionale.

CI: label e architetture verificate nel [registro ufficiale dei runner GitHub](https://github.com/actions/runner-images).
`macos-15` indica ARM64; `macos-15-intel` indica x64. Nessun codice riusato.

## Studio M2 dei riferimenti IF

Consultate licenze e sezioni mirate di Favella 1, Dialog e Inform 7:
[revisione, file, licenze e idee ricavate](confronto-linguaggi.md).
L'[analisi Inform 7](audit-inform7.md) inventaria l'intero sottoprogetto e studia
in modo mirato i contratti principali. Non è una revisione riga per riga.
Codice riutilizzato: nessuno, per tutti e tre i progetti.
