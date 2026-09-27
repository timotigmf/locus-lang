# Tabelle tipate

Stato: implementato nell'IR 15.

## Dichiarare schema e righe

Una tabella ha un nome, da una a 64 colonne nominate e fino a 10000 righe. Le
colonne possono essere testuali, numeriche o logiche:

```locus
Tabella "reperti":
    Colonna "nome" testuale.
    Colonna "valore" numerica.
    Colonna "esposto" logica.
    Riga "astrolabio" 40 falso.
    Riga "maschera" 25 vero.
Fine tabella.
```

L'ordine dei valori di ogni `Riga` è quello delle colonne. Il compilatore
rifiuta nomi di tabella duplicati con `E115`, schemi vuoti o colonne duplicate
con `E116`, righe di lunghezza o tipo errato con `E117`.

Le righe conservano ordine e duplicati. Una tabella senza righe è valida purché
abbia almeno una colonna.

## Condizioni sulle righe

Le regole possono verificare la presenza di una riga completa:

```locus
La Sala è una stanza.
Azione "consultare" senza oggetti con comando "consulta".
Tabella "reperti":
    Colonna "nome" testuale.
    Colonna "valore" numerica.
    Riga "astrolabio" 40.
Fine tabella.

Regola "trova astrolabio" per consultare nella fase invece
quando tabella "reperti" contiene riga "astrolabio" 40:
    dì "L'astrolabio è registrato.";
Fine regola.
```

`non`, `e`, `o` e le parentesi combinano questa condizione con le altre
condizioni LOCUS. Il confronto è esatto e non converte i tipi.

## Aggiungere e rimuovere righe

```locus
La Sala è una stanza.
Azione "trasferire" senza oggetti con comando "trasferisci".
Tabella "deposito":
    Colonna "nome" testuale.
    Colonna "valore" numerica.
    Riga "astrolabio" 40.
Fine tabella.
Tabella "mostra":
    Colonna "nome" testuale.
    Colonna "valore" numerica.
Fine tabella.

Regola "trasferisci astrolabio" per trasferire nella fase invece:
    rimuovi riga "astrolabio" 40 da tabella "deposito";
    aggiungi riga "astrolabio" 40 a tabella "mostra";
    dì "Il reperto è ora in mostra.";
Fine regola.
```

`aggiungi riga` inserisce in fondo e conserva i duplicati. `rimuovi riga`
elimina la prima occorrenza esatta; non fa nulla se la riga è assente. Le due
operazioni appartengono alla transazione dell'azione: un successivo `fallisci`
ripristina tutte le tabelle coinvolte. Sono vietate nella fase `verifica`.

Una tabella o una riga non compatibile usata dentro una regola produce `E314`.
Lo Studio mostra schema e righe nell'Indice del mondo e aggiorna la vista dopo
ogni comando.

## Limiti

Questa prima estensione lavora su righe complete. Non sono ancora disponibili
selezione per singola colonna, chiavi univoche, lettura di una cella, modifica
parziale, ordinamento, aggregazioni, cicli o importazione CSV. Le tabelle non
generano automaticamente testo per il giocatore: l'autore decide come narrarne
il contenuto mediante condizioni e regole.
