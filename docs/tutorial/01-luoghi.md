# 1. Luoghi, descrizioni e mappa

Esegui `locus gioca examples/tutorial/01_mappa.locus`.

Una **stanza** è un luogo esplorabile: può essere anche un molo all'aperto.
Il tipo descrive il ruolo nel modello, non necessariamente quattro pareti.
Una **descrizione** è testo associato al luogo; da sola non crea oggetti o uscite.
Una **relazione** crea invece un collegamento navigabile.

```locus
La Terrazza è una stanza.
Il Molo è una stanza.
Il Magazzino è una stanza.
La Terrazza è a nord del Molo.
Il Magazzino è a est del Molo.
Inizia nella "Molo".
Il Molo ha descrizione "La scala sale a nord e il magazzino è a est.".
```

La Terrazza viene dichiarata per prima, ma `Inizia` sceglie il Molo. Il collegamento
verso nord genera il ritorno verso sud; est genera il ritorno verso ovest. Il testo tra virgolette è una
stringa; il punto dopo le virgolette conclude la frase del linguaggio.

Prova nell'ordine:

| Comando | Risultato da controllare |
| --- | --- |
| `guarda` | Sei al Molo e leggi la descrizione |
| `nord` | Arrivi alla Terrazza |
| `nord` | Direzione impossibile; resti alla Terrazza |
| `sud` | Torni al Molo |
| `e` | Arrivi al Magazzino (`e` abbrevia `est`) |
| `o` | Torni al Molo (`o` abbrevia `ovest`) |
| `o` | Non c'è alcun passaggio verso ovest; resti al Molo |

**Esperimento.** Cambia soltanto la descrizione del Molo scrivendo che la scala
sale a sud. L'uscita resta a nord: il motore non ricava relazioni dal testo narrato.
Correggi la descrizione affinché il lettore possa fidarsi delle indicazioni.

Quando una direzione non è presente, il verbo viene comunque riconosciuto e il
gioco risponde che non c'è alcun passaggio. Sono accettati `n`, `s`, `e`, `o` e,
per compatibilità con parser classici, `north`, `south`, `east`, `west` e `w`.

**Esercizio.** Fai cominciare la storia in Terrazza senza spostare le dichiarazioni.
**Soluzione.** Sostituisci il nome quotato nella direttiva iniziale con `Terrazza`.
Non aggiungere una seconda direttiva: due punti iniziali producono E406.

LOCUS riconosce frasi controllate: `La Terrazza è una stanza.` compila;
una parafrasi libera non è necessariamente una frase del linguaggio.
