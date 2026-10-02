# 13. Scenario e oggetti nascosti

Apri `examples/tutorial/13_scenario_nascosto.locus` nello Studio. La storia usa
un affresco che il giocatore può osservare ma non raccogliere e una chiave che
esiste nel mondo senza essere inizialmente percepibile.

La dichiarazione essenziale è:

```locus
La Sala è una stanza.
Il mosaico è uno scenario nella Sala.
La chiave è una cosa nella Sala.
La chiave ha visibile falso.

Regola "scopri la chiave" per esaminare "mosaico" nella fase dopo:
    imposta "visibile" di "chiave" a vero;
    dì "Una tessera scatta e scopre la chiave.";
Fine regola.
```

Prova la sequenza:

| Comando | Risultato da controllare |
| --- | --- |
| `guarda` | Compare il cielo stellato, non la chiave |
| `prendi chiave` | Il parser non permette di agire su ciò che è nascosto |
| `prendi cielo` | L'affresco è scenario e non è trasportabile |
| `x cielo` | La regola rende visibile la chiave |
| `guarda` | La chiave compare nell'elenco del luogo |
| `prendi chiave` | Ora l'azione riesce |

La proprietà `scoperta` dell'esempio distingue la prima osservazione dalle
successive. `visibile` controlla invece il campo d'azione reale del giocatore:
non basta omettere un oggetto dalla descrizione testuale.

**Esercizio.** Fai ricomparire la chiave soltanto dopo aver esaminato due volte
l'affresco.

**Soluzione.** Aggiungi una proprietà numerica, aumentala nella regola e sposta
`imposta "visibile" ... a vero` in una seconda regola con condizione `almeno 2`.

Consulta la specifica su [visibilità e scenario](../linguaggio/visibilita-scenario.md)
per contenitori, inventario, rollback e limiti.

## Prima scoperta e visite successive

Nell'esempio completo la regola che racconta lo stato già scoperto ha
`priorità 10`; quella che effettua la scoperta mantiene la priorità predefinita
0. Le priorità maggiori vengono valutate per prime. Così, alla prima azione,
il messaggio «già aperto» non compare insieme all'annuncio della scoperta.
Alle azioni successive compare soltanto il messaggio di stato già noto.

Le condizioni leggono lo stato corrente prima di ogni regola: due condizioni
opposte non formano automaticamente un «se/altrimenti». Senza questa priorità,
la prima regola può cambiare il flag e rendere applicabile la seconda nella
stessa azione.

**Prova negativa:** avvia una nuova partita, esamina il dettaglio, poi ripeti
l'esame e usa `g`. La scoperta deve essere raccontata una sola volta; il testo
per le visite successive deve apparire soltanto dal secondo esame.
