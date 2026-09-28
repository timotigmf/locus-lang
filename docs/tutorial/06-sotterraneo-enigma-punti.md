# 6. Un sotterraneo con enigma, sinonimi e punti

Il progetto completo è `examples/tutorial/06_sotterraneo.locus`. Puoi copiare
l'intero sorgente nello Studio: il pulsante **Copia codice** appare sopra ogni
esempio del manuale.

```locus
Titolo: "Il sotterraneo dell'orologio".
Autore: "Esempio LOCUS".

L'Ingresso è una stanza.
La Galleria è una stanza.
La Cripta è una stanza.
La Galleria è a nord dell'Ingresso.
La Cripta è a est della Galleria.
Inizia nella "Ingresso".

L'Ingresso ha descrizione "Una scala scende sotto la città. La galleria continua a nord.".
La Galleria ha descrizione "Un arco di pietra protegge la cripta a est.".
La Cripta ha descrizione "Un idolo d'ambra riposa su un piedistallo.".

La cassetta è un contenitore nell'Ingresso.
La "chiave d'argento" è una chiave nella cassetta.
La porta di pietra è una porta.
La porta di pietra collega la Galleria alla Cripta.
La porta di pietra ha stato "bloccato".
La "chiave d'argento" apre la porta di pietra.
Il "idolo d'ambra" è una cosa nella Cripta.

Il registro è una cosa.
La punti è una proprietà numerica.
Il registro ha punti 0.

Comprendi "scatola" come "cassetta".
Comprendi "scrigno" come "cassetta".
Comprendi "reliquia" come "idolo d'ambra".
Comprendi "statua" come "idolo d'ambra".

Regola "premio della cripta" per prendere "idolo d'ambra" nella fase dopo:
    aumenta "punti" di "registro" di 10;
    dì "Hai risolto l'enigma della cripta e ottenuto dieci punti.";
Fine regola.
```

## Prova guidata

Esegui `apri cassetta`, `prendi chiave`, `n`, `apri porta di pietra con chiave`,
`e`, `prendi reliquia`. L'ultimo comando usa un sinonimo dell'idolo e assegna i
punti una volta sola: un secondo tentativo di prendere lo stesso oggetto fallisce
prima della regola premio.

Nel pannello **Indice del mondo**, cerca la proprietà `punti` del registro. Il
valore passa da 0 a 10. Il trace mostra la regola che ha assegnato il premio.

## Come progettare l'enigma

La soluzione forma una catena verificabile: contenitore → chiave → porta → stanza →
tesoro → premio. Ogni passaggio ha anche un caso negativo utile per i test:
chiave nascosta, porta bloccata, chiave non posseduta, movimento impedito e premio
non duplicabile.

## Passaggi segreti e limiti attuali

Puoi descrivere un passaggio come segreto e proteggerlo con una porta. Per farlo
comparire dopo una ricerca usa le relazioni dinamiche della
[lezione 12](12-passaggi-segreti.md): testo, navigazione e mappa restano coerenti.

Le lezioni successive introducono dialoghi ramificati, veicoli e acquisti con
denaro spendibile. La lezione 20 aggiunge vendita e mercanti con scorte. La
[guida dell'autore](../manuale/guida-autore.md) distingue ciò che è eseguibile
oggi dalle estensioni future.
