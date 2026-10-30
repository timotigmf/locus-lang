# 4. Un enigma completo, diviso in file

Esegui `locus debug examples/tutorial/04_faro.locus`.

Obiettivo: raggiungere la Terrazza e scoprire il segnale. Il portello è bloccato;
la chiave è in una custodia chiusa. La storia usa quattro file:

- `04_faro.locus`: include i moduli e sceglie il Molo come inizio.
- `faro/mondo.locus`: luoghi, collegamenti, porta, oggetti e proprietà.
- `faro/regole.locus`: comportamento della lanterna; include a sua volta il mondo.
- `faro/testi.locus`: descrizione iniziale del Molo.

Il mondo viene caricato una sola volta anche se entrambi i file lo includono.
Il file principale non include la lezione 3 completa: quella ha già un punto
iniziale. I moduli riutilizzabili lasciano la scelta dell'inizio alla storia.

## Percorso di soluzione e controlli negativi

| Passo | Comando | Risultato importante |
| --- | --- | --- |
| 1 | `nord` | Il portello impedisce il passaggio |
| 2 | `prendi chiave di rame` | La chiave non è ancora raggiungibile |
| 3 | `apri custodia` | Puoi accedere al contenuto |
| 4 | `prendi chiave di rame` | La chiave è nell'inventario |
| 5 | `apri portello con chiave di rame` | Apertura riuscita |
| 6 | `nord` | Arrivi in Terrazza |
| 7 | `apri lanterna` | Il segnale raggiunge il mare |
| 8 | `guarda` | La descrizione conferma il cambiamento |
| 9 | `chiudi lanterna` | Il segnale viene nascosto |
| 10 | `guarda` | La descrizione torna coerente con la chiusura |

Non aggiungiamo un sistema di vittoria inesistente: l'obiettivo narrativo è
raggiunto al passo 7, ma il giocatore può continuare o digitare `esci`.

## Ripetere una prova

Il repository include `examples/tutorial/04_faro.comandi` e l'uscita attesa
`04_faro.atteso`. Da macOS/Linux:

```sh
locus gioca examples/tutorial/04_faro.locus < examples/tutorial/04_faro.comandi
```

Da PowerShell:

```powershell
Get-Content examples/tutorial/04_faro.comandi | locus gioca examples/tutorial/04_faro.locus
```

Il file `.atteso` include anche la descrizione iniziale, senza prompt interattivi.
`tests/test_tutorials.py` confronta realmente l'uscita con quella attesa e verifica
proprietà finali e inventario. Il confronto è automatico nella suite del progetto;
la redirezione della CLI da sola riproduce i comandi ma non controlla l'uscita.

Prima di correggere un test che fallisce, chiediti se è cambiato volutamente il
racconto o se il mondo ha smesso di comportarsi correttamente. Un'altra persona
può provare comandi che il percorso previsto non copre: il copione non sostituisce
una prova di gioco libera.

## Laboratorio: separare i testi

La versione completa include già la soluzione dell'esercizio: la descrizione
del Molo vive in `faro/testi.locus`. Il file principale è copiabile così:

```text
Includi "faro/mondo.locus".
Includi "faro/regole.locus".
Includi "faro/testi.locus".
Inizia nel Molo.
```

Il contenuto completo di `faro/testi.locus` è:

```text
Il Molo ha descrizione "Il passaggio a nord conduce alla terrazza. Una custodia contiene la chiave.".
```

Questi due blocchi sono parti di un progetto: il file dei testi richiede anche
la dichiarazione del Molo, presente in `mondo.locus`. Compila il file principale,
non il solo modulo dei testi. Nello Studio conserva i percorsi indicati quando
aggiungi i file al progetto e scegli `04_faro.locus` come file principale.

`Inizia nel Molo.` sceglie esplicitamente la partenza, anche se il mondo dichiara
prima la Terrazza. Il nome può essere non quotato; il percorso di `Includi`
richiede invece le virgolette. Il percorso si calcola dalla cartella del file
che contiene la direttiva: nelle regole basta `Includi "mondo.locus".`, mentre
nel principale serve il prefisso `faro/`.

**Prova positiva.** Esegui il copione della lezione: l'uscita resta identica alla
versione con il testo nel mondo. Separare i file non cambia la partita.

**Prova negativa.** Rinomina temporaneamente `faro/testi.locus` senza aggiornare
l'inclusione. La compilazione restituisce `E402` sulla terza riga del principale,
che contiene il percorso non più trovato. Ripristina il nome per correggere
l'errore. Se cambi soltanto il nome del Molo nel modulo, invece, il riferimento
non dichiarato produce `E103` nel file dei testi.

**Esercizio ulteriore.** Sposta anche la descrizione della lanterna nel modulo
dei testi, rimuovendo l'assegnazione dal mondo. Ripeti il copione per verificare
che la riorganizzazione conservi il comportamento.

## Porta e portello

Nel faro `porta` è un sinonimo esplicito di `portello`. Dopo `apri custodia`
e `prendi chiave`, usa `apri porta con chiave`, poi `nord`. La chiave va
indicata per aprire il portello bloccato: possederla non basta ad aprirlo con
il solo movimento. Il messaggio del passaggio mostra il nome portello e
distingue la serratura bloccata dalla semplice chiusura.

Nei progetti già salvati aggiungi `Comprendi "porta" come "portello".` al
sorgente e ricompila; gli aggiornamenti degli esempi non riscrivono il tuo progetto.

Se hai già la chiave in inventario ma scrivi soltanto `apri porta`, il nuovo
suggerimento ricorda di indicarla nel comando. Usa `apri porta con chiave`.
Non serve prendere nuovamente la chiave: manca il complemento, non l’oggetto.

## Laboratorio: scegliere la chiave adatta

Apri `examples/tutorial/04b_due_chiavi.locus` oppure copia:

```locus
Titolo: "Le due chiavi del portello".
Autore: "Esempio LOCUS".
Il Molo è una stanza.
La Terrazza è una stanza.
La Terrazza è a nord del Molo.
Inizia nel Molo.
Il portello è una porta.
Il portello collega il Molo alla Terrazza.
Il portello ha stato "bloccato".
Comprendi "porta" come "portello".
La chiave di rame è una chiave nel Molo.
La chiave di ferro è una chiave nel Molo.
La chiave di rame apre il portello.
```

1. `apri porta con chiave di rame`: devi prima prendere la chiave indicata.
2. `prendi chiave di ferro`, poi `apri porta con chiave di ferro`: la chiave
   trasportata non è adatta; il portello resta bloccato.
3. `prendi chiave di rame`, poi `apri porta con chiave`: il nome è ambiguo.
4. Rispondi `rame`: l'apertura riprende con la chiave scelta. Ora `nord` funziona.

I messaggi distinguono oggetto non trasportato e chiave incompatibile, indicando
il nome usato. Non rivelano quale altra chiave apra la serratura. Se le chiavi
sono entrambe raggiungibili, scrivere solo `chiave` può richiedere un chiarimento.
