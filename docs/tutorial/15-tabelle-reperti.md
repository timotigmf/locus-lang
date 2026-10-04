# 15. Il registro dei reperti

Apri `examples/tutorial/15_tabelle_reperti.locus` nello Studio. Il deposito e
la mostra sono due tabelle con lo stesso schema. Un comando trasferisce una riga
da una all'altra in una sola transazione.

La struttura centrale è:

```locus
La Sala è una stanza.
Azione "trasferire" senza oggetti con comando "trasferisci".
Tabella "deposito":
    Colonna "nome" testuale.
    Colonna "valore" numerica.
    Colonna "fragile" logica.
    Riga "astrolabio" 40 vero.
Fine tabella.
Tabella "mostra":
    Colonna "nome" testuale.
    Colonna "valore" numerica.
    Colonna "fragile" logica.
Fine tabella.

Regola "trasferimento" per trasferire nella fase invece
quando tabella "deposito" contiene riga "astrolabio" 40 vero:
    rimuovi riga "astrolabio" 40 vero da tabella "deposito";
    aggiungi riga "astrolabio" 40 vero a tabella "mostra";
    dì "L'astrolabio è stato trasferito.";
Fine regola.
```

Prova questa sequenza:

| Passo | Risultato da controllare |
| --- | --- |
| Apri **Indice del mondo** | `deposito` contiene l'astrolabio; `mostra` è vuota |
| `consulta deposito` | La storia conferma che l'astrolabio è disponibile |
| `trasferisci astrolabio` | La riga passa dal deposito alla mostra |
| Apri di nuovo l'indice | Le due tabelle mostrano lo stato aggiornato |
| `consulta mostra` | La storia conferma che il reperto è esposto |
| `trasferisci astrolabio` | La regola di verifica impedisce un secondo trasferimento |

**Errore guidato.** Cambia `40` in `"quaranta"` dentro un effetto. La
compilazione si ferma con `E314`, perché la seconda colonna è numerica.

**Esercizio.** La tabella del file completo contiene già una maschera di valore
25. Trasferiscila con una seconda azione, senza duplicarne la riga.

**Soluzione.** La nuova riga deve avere tre valori nell'ordine `nome`, `valore`,
`fragile`. Copia la coppia rimozione/aggiunta e usa la stessa riga completa
nella condizione.

Consulta la [specifica delle tabelle](../linguaggio/tabelle-tipate.md) per
duplicati, limiti, rollback e funzioni ancora aperte.

## Soluzione completa: trasferire anche la maschera

Il file della lezione include ora anche l'azione seguente. Se parti da una copia
precedente, aggiungi questo blocco una sola volta; la riga della maschera è già
presente nel deposito:

```text
Azione "trasferire maschera" senza oggetti con comando "trasferisci maschera".

Regola "trasferimento maschera" per trasferire maschera nella fase invece priorità 10
quando tabella "deposito" contiene riga "maschera" 25 falso:
    rimuovi riga "maschera" 25 falso da tabella "deposito";
    aggiungi riga "maschera" 25 falso a tabella "mostra";
    dì "La maschera è stata trasferita nella mostra.";
Fine regola.

Regola "maschera non disponibile" per trasferire maschera nella fase verifica:
    fallisci "La maschera non è disponibile nel deposito.";
Fine regola.
```

Prova `trasferisci maschera`, poi `trasferisci astrolabio`: il deposito diventa
vuoto e la mostra contiene entrambe le righe, nell'ordine di trasferimento.
Ripeti ciascun comando: il rifiuto deve lasciare entrambe le tabelle invariate.
Puoi anche ricompilare e invertire l'ordine dei due trasferimenti.

Le condizioni confrontano tutti e tre i valori, incluso `falso`: il nome da
solo non è una chiave della tabella. La priorità 10 segue lo schema dell'astrolabio:
la sostituzione riuscita trasferisce la riga, mentre la verifica spiega il rifiuto
quando la riga non è più disponibile.

`consulta deposito` e `consulta mostra` nell'esempio parlano dell'astrolabio e
della sua vetrina centrale; non stampano l'intera tabella. Per controllare anche
la maschera usa le tabelle nell'Indice del mondo. Le righe del registro non creano
oggetti narrativi trasportabili: `prendi maschera` non sostituisce questa azione.
