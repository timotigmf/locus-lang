# ADR 0039 — ritorno al luogo precedente

Stato: accettato, 2026-10-02.

## Contesto

Nelle avventure testuali `indietro` e `back` evitano di ricordare la direzione
appena percorsa. LOCUS deve rispettare porte e archi a senso unico senza
trasformare il comando in teletrasporto o ricerca automatica di un itinerario.

## Decisione

La sessione conserva un solo `previous_room_id`, aggiornato esclusivamente da
un movimento direzionale riuscito. `indietro` cerca un arco uscente verso quel
luogo e delega alla normale transizione direzionale. Il ritorno riuscito scambia
luogo corrente e precedente; l'assenza di memoria e l'assenza dell'arco inverso
producono eventi distinti.

La memoria appartiene alla sessione, non all'IR o al mondo. Il formato IR 21
resta invariato. Lo Studio espone l'identificatore precedente per rendere
verificabili test e debugger futuri.

## Alternative considerate

- Conservare una pila completa: aggiunge una cronologia e politiche di limite
  non necessarie per il singolo comando.
- Muovere direttamente all'ID ricordato: aggirerebbe porte, veicoli e passaggi
  a senso unico.
- Calcolare un percorso alternativo: cambierebbe un ritorno di un passo in una
  funzione di navigazione automatica.

## Conseguenze e verifica

Il comando alterna fra due stanze collegate e fallisce dopo una caduta senza
ritorno. Le stesse verifiche coprono forme italiane e inglesi, veicoli, Studio,
browser e tutorial.
