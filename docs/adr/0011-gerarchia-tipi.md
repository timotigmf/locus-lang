# ADR 0011 — gerarchia nominale a ereditarietà singola

Stato: accettato.

## Contesto

I cinque tipi della libreria erano categorie piatte. Un autore poteva chiamare
un oggetto “reliquia”, ma doveva dichiararlo come cosa e non poteva riusare quel
concetto in proprietà, relazioni, regole, mappa e runtime. Serviva una gerarchia
che conservasse l'indipendenza del compilatore dal dominio narrativo e che
permettesse riferimenti in avanti.

## Decisione

Il sorgente dichiara `Un X è un tipo di Y.`. L'analisi raccoglie prima tutti i
nomi, risolve poi i genitori e rifiuta duplicati, genitori assenti e cicli. Ogni
tipo ha zero o un genitore. L'IR 7 include la tabella completa dei tipi; entità,
schemi e regole continuano a riferirsi a ID.

Il catalogo host può fornire la propria relazione padre tramite
`kind_parents`. Il confronto di compatibilità è una funzione generica del core.
La stdlib dichiara contenitore e chiave come sottotipi di cosa e usa lo stesso
confronto nel gioco, nella validazione, nel renderer e nella mappa dello Studio.

## Alternative considerate

- Espandere ogni sottotipo negli schemi durante la compilazione: scartato perché
  duplicava informazione e rendeva incoerenti runtime e strumenti.
- Copiare proprietà e relazioni sull'entità: scartato perché perdeva l'identità
  nominale del tipo e complicava le diagnosi.
- Ereditarietà multipla immediata: rinviata perché richiede regole esplicite per
  conflitti, ordine di risoluzione e combinazione di capacità.
- Tipi codificati nella stdlib: scartato perché il compilatore deve funzionare
  anche con domini non narrativi.

## Conseguenze

Gli autori possono costruire tassonomie riutilizzabili e i sottotipi mantengono
le capacità degli antenati in tutti i frontend. Il runtime deve convalidare la
tabella dei tipi e ogni controllo di categoria deve percorrere la gerarchia.
L'IR passa da 6 a 7 e resta sperimentale. Tratti, proprietà limitate a un tipo e
mutazione del tipo richiedono decisioni successive.

## Criterio di revisione

Rivedere la decisione quando due capacità indipendenti richiederanno composizione
senza una relazione naturale padre-figlio. Qualunque estensione dovrà definire
conflitti, linearizzazione, diagnostica e compatibilità dell'IR.
