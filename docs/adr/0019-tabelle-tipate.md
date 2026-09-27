# ADR 0019 — tabelle con schema e righe transazionali

Stato: accettato, 27 settembre 2026.

## Contesto

Gli elenchi rappresentano sequenze omogenee, ma cataloghi, prezzi, registri e
stati di dialogo richiedono record con campi di tipo diverso. Una lista di testi
separati da delimitatori perderebbe tipi e struttura nel runtime.

## Decisione

L'IR introduce tabelle nominate con colonne ordinate e righe immutabili. Ogni
colonna ha nome e tipo scalare; il compilatore controlla numero e tipo di tutti i
valori. Le regole possono verificare una riga completa e aggiungerla o rimuoverla.
La rimozione interessa la prima occorrenza esatta, mentre l'aggiunta conserva i
duplicati e l'ordine.

Il rulebook delega lettura e modifica all'host tramite operazioni strutturate.
Ogni modifica produce un nuovo mondo e partecipa al rollback dell'azione. Il
runtime convalida schemi, condizioni ed effetti anche ai confini dell'IR. L'IR
sale alla versione 15.

## Alternative considerate

- Righe come dizionari dinamici: scartate perché ordine, campi mancanti e tipi
  sarebbero risolti soltanto durante l'esecuzione.
- Tabelle come proprietà di ogni entità: rinviate; il primo caso d'uso è un dato
  nominato del progetto, condiviso fra regole.
- Selezione e modifica per colonna nel primo incremento: rinviate per definire
  separatamente chiavi, molteplicità dei risultati e assenza di celle.
- Importazione CSV: rinviata perché codifica, intestazioni e provenienza dei file
  richiedono un contratto di progetto dedicato.

## Conseguenze

Il core conserva tabelle senza dipendere dalla narrativa. Lo Studio può
ispezionare lo snapshot corrente con intestazioni e righe tipate. Le operazioni
su righe complete sono deterministiche ma verbose; chiavi, query, celle,
aggregazioni e iterazione restano estensioni successive.
