# 1. Luoghi, descrizioni e mappa

Esegui `locus gioca examples/tutorial/01_mappa.locus`.

Una **stanza** è un luogo esplorabile: può essere anche un molo all'aperto.
Il tipo descrive il ruolo nel modello, non necessariamente quattro pareti.
Una **descrizione** è testo associato al luogo; da sola non crea oggetti o uscite.
Una **relazione** crea invece un collegamento navigabile.

```locus
La Terrazza è una stanza.
Il Molo è una stanza.
La Terrazza è a nord del Molo.
Inizia nella "Molo".
Il Molo ha descrizione "La scala sale a nord verso la terrazza.".
```

La Terrazza viene dichiarata per prima, ma `Inizia` sceglie il Molo. Il collegamento
verso nord genera anche il ritorno verso sud. Il testo tra virgolette è una
stringa; il punto dopo le virgolette conclude la frase del linguaggio.

Prova nell'ordine:

| Comando | Risultato da controllare |
| --- | --- |
| `guarda` | Sei al Molo e leggi la descrizione |
| `nord` | Arrivi alla Terrazza |
| `nord` | Direzione impossibile; resti alla Terrazza |
| `sud` | Torni al Molo |

**Esperimento.** Cambia soltanto la descrizione del Molo scrivendo che la scala
sale a sud. L'uscita resta a nord: il motore non ricava relazioni dal testo narrato.
Correggi la descrizione affinché il lettore possa fidarsi delle indicazioni.

**Esercizio.** Fai cominciare la storia in Terrazza senza spostare le dichiarazioni.
**Soluzione.** Sostituisci il nome quotato nella direttiva iniziale con `Terrazza`.
Non aggiungere una seconda direttiva: due punti iniziali producono E406.

LOCUS riconosce frasi controllate: `La Terrazza è una stanza.` compila;
una parafrasi libera non è necessariamente una frase del linguaggio.
