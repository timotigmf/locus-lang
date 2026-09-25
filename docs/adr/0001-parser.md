# ADR 0001 — parsing deterministico sostituibile

Stato: accettato per S0, 2026-09-25.

## Contesto e alternative

| Opzione | Vantaggi | Costi / rischi |
| --- | --- | --- |
| Lexer + discesa ricorsiva originali | controllo su span/diagnosi; zero dipendenze | grammatica e implementazione possono divergere; manutenzione manuale |
| Lark LALR | grammatica dichiarativa, parsing efficiente | traduzione errori e albero esterno; conflitti da gestire |
| Lark Earley | utile per analizzare ambiguità di grammatiche | ambiguità da risolvere semanticamente e prestazioni da misurare |
| ANTLR | grammatica e generazione per diversi target | toolchain di generazione Java e runtime Python; versioni da coordinare |
| pyparsing | composizione in Python, prototipi leggibili | rischio di accoppiare parsing e azioni semantiche; grammatica meno indipendente |
| PEG/packrat | scelta ordinata e parsing deterministico | ordine delle alternative può nascondere ambiguità; memoria e diagnosi |

Lark (MIT), ANTLR (BSD-3-Clause), pyparsing (MIT) sono candidati maturi con
implementazioni utilizzabili in Python. Nessuno è selezionato solo per comodità.
Non sono stati eseguiti benchmark comparativi: non si deducono prestazioni reali
sull'italiano da esempi JSON o dalle sole classi di complessità.

## Decisione

S0 ha una sola produzione di dichiarazione: implementazione originale di lexer
e parser predittivo, senza regex semantiche. Un unico ingresso `parse` e AST
indipendente rendono sostituibile il frontend. Il parser non consulta il catalogo
dei tipi. I token mantengono gli offset dell'originale, NFC solo nel confronto.

## Conseguenze e revisione

Zero runtime dependency; test di conformità indispensabili. Non estendere questo
parser indefinitamente per inerzia. Prima di introdurre regole/espressioni o
risoluzione sintattica dipendente dai simboli, prototipare la stessa grammatica
in Lark LALR ed Earley e confrontare corpus positivo/negativo, diagnosi e tempi.
Favorire LALR se la grammatica rimane non ambigua; Earley come strumento di
analisi, non permesso di indovinare. Cambiare motore non deve cambiare l'AST.
