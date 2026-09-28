# 16. La guardiana del faro

Apri `examples/tutorial/16_dialogo_guardiana.locus` nello Studio. Questa lezione
introduce il tipo predefinito `persona` e una conversazione a nodi, con un ciclo,
una conclusione esplicita e un nodo finale.

Il cuore dell'esempio è:

```locus
La Sala è una stanza.
La guardiana è una persona nella Sala.

Dialogo "memorie della guardiana" con "guardiana":
    Nodo "inizio" dice "La guardiana posa il registro sul tavolo.":
        Scelta "Chiedi della tempesta" porta a "tempesta".
        Scelta "Chiedi della chiave" porta a "chiave".
        Scelta "Saluta e concludi" termina.
    Fine nodo.
    Nodo "tempesta" dice "La tempesta spense la luce per tre notti.":
        Scelta "Torna alle domande" porta a "inizio".
    Fine nodo.
    Nodo "chiave" dice "La chiave è nascosta sotto la campana.":
    Fine nodo.
Fine dialogo.
```

Prova questa sequenza:

| Comando | Risultato da controllare |
| --- | --- |
| `guarda` | la guardiana appare nella sala |
| `prendi guardiana` | LOCUS spiega che la persona non è trasportabile |
| `parla con guardiana` | compare la prima battuta con tre scelte |
| `1` | raggiungi il nodo della tempesta |
| `scegli domande` | torni al nodo iniziale attraverso il ciclo |
| `scegli chiave` | raggiungi il nodo finale e il dialogo termina |
| `p guardiana`, poi `basta` | il dialogo riparte e può essere interrotto |

Apri **Regole e trace** dopo una scelta: vedrai il nome del dialogo, il nodo e
la scelta attraversata. Nell'**Indice del mondo** vedrai il dialogo associato
alla guardiana.

**Errore guidato.** Cambia `porta a "tempesta"` in `porta a "temporale"`. La
compilazione produce `E119` e indica la scelta con la destinazione inesistente.

**Esercizio.** Aggiungi un nodo `luce`, raggiungibile dall'inizio, e permetti di
tornare alle domande.

**Soluzione.** Aggiungi una scelta nel nodo iniziale prima di dichiarare il
nuovo nodo. Ogni nodo deve essere raggiungibile seguendo almeno una scelta dal
primo.

Per sintassi, limiti e stato della sessione consulta la
[specifica dei dialoghi](../linguaggio/dialoghi-strutturati.md).
