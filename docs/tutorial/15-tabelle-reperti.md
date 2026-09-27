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

**Esercizio.** Aggiungi una riga per una maschera con valore 25 e trasferiscila
con una seconda azione.

**Soluzione.** La nuova riga deve avere tre valori nell'ordine `nome`, `valore`,
`fragile`. Copia la coppia rimozione/aggiunta e usa la stessa riga completa
nella condizione.

Consulta la [specifica delle tabelle](../linguaggio/tabelle-tipate.md) per
duplicati, limiti, rollback e funzioni ancora aperte.
