# ADR 0022 — veicoli e movimento atomico del conducente

Stato: accettato, 28 settembre 2026.

## Contesto

Una bicicletta o una barca non è una direzione: possiede identità, tipo,
descrizione e posizione. Modellare il mezzo come semplice testo della sessione
renderebbe incoerenti mappa, risoluzione dei nomi e regole di movimento.

## Decisione

La stdlib introduce il tipo radice `mondo.veicolo`, collocabile direttamente in
una stanza e non trasportabile. L'IR generica conserva il veicolo come normale
entità tipata e la sua posizione come relazione `mondo.dentro`; il compilatore
non assume il significato del tipo narrativo.

La sessione registra al massimo un `vehicle_id`. Salita e discesa sono azioni
standard tipate disponibili alle regole. Durante un comando cardinale, la stdlib
aggiorna in una sola transizione stanza del giocatore e relazione di posizione
del veicolo, poi valida la coerenza dello snapshot. L'IR sale alla versione 18.

I comandi specifici vengono riservati soltanto se il progetto contiene almeno
un veicolo. Lo Studio deriva posizione e conteggio dall'IR e dalle relazioni
correnti, senza rileggere il sorgente.

## Alternative considerate

- Conservare soltanto il nome del veicolo nella sessione: scartato perché la
  mappa e i riferimenti avrebbero una posizione diversa da quella del giocatore.
- Fare di `veicolo` un sottotipo trasportabile di `cosa`: scartato perché
  permetterebbe di prenderlo e metterlo nell'inventario.
- Modellare subito conducente, passeggeri e carico come contenimento generale:
  rinviato per definire capienza, raggiungibilità e movimento di gruppo senza
  cambiare implicitamente la semantica dei contenitori esistenti.
- Aggiungere relazioni separate per strada, acqua e rotaia: rinviato; richiede
  profili di mobilità e diagnostica dei percorsi.

## Conseguenze

Veicolo e conducente non possono separarsi durante un viaggio riuscito, e un
movimento bloccato non modifica nessuno dei due. Sottotipi, descrizioni,
visibilità, regole, mappa e release web condividono lo stesso stato. Il primo
contratto supporta un conducente; passeggeri, carico, risorse e percorsi tipati
restano estensioni esplicite.
