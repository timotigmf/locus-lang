# ADR 0006 — regole M3 e confronto del parser

Stato: accettato per M3. Integra ADR 0001 e 0005.

## Decisione

Regole nominate con blocco esplicito, catalogo di azioni iniettato, condizioni
booleane tipate e sei fasi. Priorità decrescente, ordine sorgente a parità.
La [specifica](../linguaggio/milestone-3.md) definisce esattamente gli esiti.
Il motore generico usa un Host di lettura/scrittura/esecuzione e non importa
parser, AST, CLI o dominio IF. L'adattatore narrativo preserva le azioni M2.

Una transazione comprende fasi e sostituzioni. Fallimenti annullano stato e output,
conservando trace e motivo; interruzione e risultato conservano gli effetti.
Oggetti immutabili ai confini. Massimo otto azioni concatenate e rilevamento di cicli
identici; niente effetti esterni nel nucleo. Gli host personalizzati devono essere
puri: il motore non può annullare I/O eseguito da un host arbitrario.
IR versione 4: regole con riferimenti risolti e origine sorgente, nessun eval.

## Esperimento richiesto da ADR 0001

`tools/rule_probe.lark` e `tools/probe_parsers.py` confrontano Lark LALR, Earley e
parser di produzione su quattro frammenti validi e quattro malformati. Comando:
`python -m pip install -e '.[parser-research]'`, poi `python tools/probe_parsers.py`.
Lark è una dipendenza opzionale solo per ricerca, mai richiesta dal runtime.

Misura locale Python 3.14.5, macOS Apple Silicon, Lark 1.3.1:

| Parser | Costruzione ms | 400 parsing ms | Accettati/rifiutati |
| --- | ---: | ---: | --- |
| LALR | 19,48 | 33,78 | 4 / 4 |
| Earley | 10,36 | 414,24 | 4 / 4 |
| Produzione | non misurata | 19,37 | 4 / 4 |

Posizioni degli errori coincidenti salvo EOF: LALR segnala l'ultimo token,
Earley restituisce -1/-1, produzione la posizione EOF. Non è un benchmark generale:
il corpus è minuscolo, la grammatica sperimentale copre soltanto regole, non tutte
le dichiarazioni né i limiti semantici/Unicode del frontend. Produzione costruisce
AST, Lark produce alberi; i tempi non confrontano pipeline equivalenti.

Manteniamo il parser attuale per M3: grammatica controllata senza ambiguità intenzionale,
riuso degli span e diagnostica italiana esistente, nessuna nuova dipendenza runtime.
Non deduciamo superiorità dal tempo misurato. Rivalutare LALR con corpus completo,
trasformazione AST e diagnostica quando arriveranno funzioni/moduli o sintassi più libera.

## Alternative e conseguenze

Indentazione significativa e frasi molto libere richiedono più disambiguazione:
rinviate. Effetti immediati non annullabili renderebbero i fallimenti parziali: scartati.
Sostituzioni senza limite: scartate. Rendere IF parte del motore impedirebbe host
non narrativi: scartato e coperto da un test con stato numerico.
La sintassi è più esplicita della visione finale; ID e formato IR restano sperimentali.
