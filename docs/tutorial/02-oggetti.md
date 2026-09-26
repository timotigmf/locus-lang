# 2. Oggetti, contenitori e accessibilità

Esegui `locus gioca examples/tutorial/02_custodia.locus`.

Il file dichiara una custodia nel Molo e una chiave nella custodia. La custodia
parte chiusa: la chiave esiste nel mondo ma non è ancora raggiungibile.
Scrivere «una chiave» nella descrizione di una stanza non basta a crearla:
servono una dichiarazione e una collocazione.

| Comando | Risultato da controllare |
| --- | --- |
| `prendi chiave di rame` | Non trovi qui l'oggetto: la custodia è chiusa |
| `esamina custodia` | Descrizione e stato chiuso |
| `apri custodia` | Apertura riuscita |
| `esamina custodia` | Ora compare il contenuto |
| `prendi chiave di rame` | Presa riuscita |
| `inventario` | Compare la chiave |
| `chiudi custodia` | La chiave resta con te |

`guarda` descrive il luogo e ciò che il modello rende visibile; `esamina` chiede
dettagli su un oggetto. L'inventario è separato dal contenimento iniziale.
Non confondere «è stato dichiarato», «è qui», «è raggiungibile» e «lo possiedo».

**Esperimento.** Dopo aver preso la chiave, prova `metti chiave di rame nella custodia`
mentre la custodia è chiusa. L'azione fallisce e la chiave resta nell'inventario.
Apri la custodia e ripeti: la chiave viene spostata nel contenitore.

**Esercizio.** Aggiungi un messaggio utile quando si esamina la chiave.
**Soluzione.** Il file completo contiene già una proprietà `descrizione` sulla chiave:
modifica quel testo. Non aggiungere una seconda assegnazione della stessa proprietà
sullo stesso oggetto: il compilatore segnala E112.

Questo esercizio prova anche un caso negativo: un rifiuto corretto è parte del
comportamento del gioco e merita una verifica quanto il percorso vincente.
