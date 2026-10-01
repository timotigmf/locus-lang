# ADR 0036 — dichiarazioni di passaggi a senso unico

Stato: accettato, 2026-10-01.

## Contesto

Le relazioni direzionali della stdlib generano sempre l'arco inverso. Questo
contratto rende concise le mappe ordinarie, ma non può descrivere cadute,
botole richiuse, scivoli e altri percorsi che non consentono il ritorno.

## Decisione

La dichiarazione `Dalla ORIGINE si va a DIREZIONE verso la DESTINAZIONE.`
produce un fatto relazionale marcato come unidirezionale nell'AST. Il lowering
usa gli operandi nell'ordine espresso e omette l'inversa prevista dallo schema.
L'IR continua a contenere normali `RelationIR`: la direzionalità deriva
dall'assenza dell'arco opposto e non richiede una nuova versione.

Il compilatore core conserva un solo indicatore sintattico generico; nomi,
tipi, ID e inverse delle direzioni restano forniti dal catalogo. Lo Studio
riconosce l'assenza dell'inversa, esporta `oneWay: true` e disegna una freccia.

## Alternative considerate

- Aggiungere dodici nuovi ID di relazione: duplicherebbe catalogo, dispatcher e
  atlante senza aggiungere semantica all'IR.
- Usare una proprietà testuale sul luogo: sposterebbe la topologia fuori dalle
  relazioni strutturate e richiederebbe interpretazione nel runtime.
- Disattivare globalmente le inverse: renderebbe prolisse tutte le mappe
  esistenti e cambierebbe il contratto delle dichiarazioni ordinarie.

## Conseguenze e verifica

La nuova frase è esplicita sull'ordine origine-destinazione e coesiste con la
sintassi relazionale esistente. I controlli `E104`–`E107` restano applicabili.
Test di parser, compilatore, runtime, Studio, tutorial e browser verificano
l'assenza dell'inversa e la freccia della mappa. Le mutazioni dinamiche restano
bidirezionali e sono documentate come limite.
