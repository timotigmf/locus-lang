# 4. Un enigma completo, diviso in file

Esegui `locus debug examples/tutorial/04_faro.locus`.

Obiettivo: raggiungere la Terrazza e scoprire il segnale. Il portello è bloccato;
la chiave è in una custodia chiusa. La storia usa tre file:

- `04_faro.locus`: include i moduli e sceglie il Molo come inizio.
- `faro/mondo.locus`: luoghi, collegamenti, porta, oggetti e proprietà.
- `faro/regole.locus`: comportamento della lanterna; include a sua volta il mondo.

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

**Esercizio.** Sposta la descrizione del Molo in un file `faro/testi.locus` e includilo.
**Soluzione.** Sposta l'assegnazione, non copiarla, e aggiungi un `Includi` nel file
principale. Gli oggetti restano dichiarati nel mondo; i riferimenti fra file funzionano.
