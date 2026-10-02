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
La premiato è una proprietà logica.
Il registro ha punti 0.

Comprendi "scatola" come "cassetta".
Comprendi "scrigno" come "cassetta".
Comprendi "reliquia" come "idolo d'ambra".
Comprendi "statua" come "idolo d'ambra".

Regola "premio della cripta" per prendere "idolo d'ambra" nella fase dopo
quando "premiato" di "registro" è falso:
    imposta "premiato" di "registro" a vero;
    aumenta "punti" di "registro" di 10;
    dì "Hai risolto l'enigma della cripta e ottenuto dieci punti.";
Fine regola.
```

## Prova guidata

Esegui `apri cassetta`, `prendi chiave`, `n`, `apri porta di pietra con chiave`,
`e`, `prendi reliquia`. L'ultimo comando usa un sinonimo dell'idolo e assegna i
punti una volta sola. La proprietà logica `premiato`, inizialmente falsa,
memorizza il completamento dell’enigma anche quando lasci e riprendi il tesoro.

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

## Verificare un premio non duplicabile

Dopo la soluzione, prova questa sequenza nel pannello di gioco:

```text
prendi statua
lascia reliquia
prendi statua
lascia statua
prendi reliquia
```

Il primo comando fallisce perché possiedi già l'idolo. I successivi riescono,
ma il registro deve restare a 10 punti e il messaggio del premio non deve
ricomparire. Ripeti la sequenza: verificare soltanto due prese consecutive
non basta, perché lasciare l'oggetto rende possibile una nuova presa.

La fase `dopo` assicura che la presa sia riuscita; la condizione su `premiato`
assicura che sia la prima premiata. L'effetto imposta il flag e incrementa i
punti nella stessa transazione. Una nuova partita riparte da zero.

Questi punti sono una proprietà dell'esempio, consultabile nell'Indice: non
modificano il comando standard `punteggio`, che legge il registro delle scene
illustrato nella [lezione 17](17-tempesta-e-punteggio.md).

**Esercizio:** aggiungi un secondo tesoro con un flag distinto e un premio di
cinque punti. Verifica che raccogliere entrambi porti il registro a 15 e che
lasciarli e riprenderli non aumenti il totale.
