# 3. Regole, stato e descrizioni che cambiano

Esegui `locus debug examples/tutorial/03_segnale.locus`.

La lanterna è un contenitore con una schermatura apribile. Il testo iniziale
racconta un fascio nascosto. Una regola nella fase `dopo` reagisce all'apertura
riuscita: imposta una proprietà logica, aggiorna la descrizione della Terrazza e
aggiunge un messaggio. La regola complementare reagisce alla chiusura.

Tre responsabilità diverse:

- L'azione della stdlib apre o chiude la lanterna.
- `imposta` modifica il modello e la descrizione memorizzata.
- `dì` produce soltanto un messaggio per questa azione.

Se scrivessi solo `dì "Il segnale è acceso";`, nessuna proprietà cambierebbe.
Una storia coerente deve far corrispondere racconto e stato consultabile.

| Comando | Risultato da controllare |
| --- | --- |
| `guarda` | La schermatura nasconde il fascio |
| `apri lanterna` | Il segnale raggiunge il mare |
| `guarda` | Il nuovo testo descrive il fascio nella foschia |
| `apri lanterna` | È già aperta: la regola dopo non viene eseguita |
| `chiudi lanterna` | La luce torna dietro la schermatura |
| `guarda` | Ricompare la descrizione iniziale |

Il trace di `debug` mostra nome, fase, priorità e posizione della regola.
Le righe di trace vanno su stderr; il racconto va su stdout. Con `gioca` si vede
soltanto il racconto. Un movimento esegue la descrizione della stanza ma non una
seconda azione autore `guardare`: evita di assumere che le due cose siano equivalenti.

**Esercizio.** Scrivi una versione del messaggio di apertura più breve.
**Soluzione.** Cambia il testo dell'istruzione `dì`, lasciando invariati gli `imposta`.
Il testo di `guarda` non deve cambiare: dipende dalla proprietà della Terrazza.

**Approfondimento.** `verifica` è la fase dei rifiuti con `fallisci`; `dopo` lavora
solo dopo il successo. `descrivi` può sostituire l'intera narrazione predefinita:
usala quando vuoi assumerti anche il compito di fornire al lettore le informazioni
utili. Le condizioni, gli esiti e il rollback sono descritti nella [specifica M3](../linguaggio/milestone-3.md).
