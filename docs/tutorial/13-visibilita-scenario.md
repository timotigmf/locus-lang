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

## Esercizio risolto: osservare due volte

Fai apparire la chiave soltanto dopo due esami del mosaico. La soluzione completa
è `examples/tutorial/13b_seconda_osservazione.locus`; puoi anche copiare questo
sorgente in un progetto nuovo:

```locus
Titolo: "La seconda osservazione".
Autore: "Esempio LOCUS".

La Sala è una stanza.
Inizia nella "Sala".
Il mosaico è uno scenario nella Sala.
Il mosaico ha descrizione "Una tessera lunare sporge fra le stelle.".
La chiave è una chiave nella Sala.
La chiave ha visibile falso.
La osservazioni è una proprietà numerica.
La scoperta è una proprietà logica.

Regola "conta gli esami" per esaminare "mosaico" nella fase dopo priorità 20
quando "scoperta" di "mosaico" è falso:
    aumenta "osservazioni" di "mosaico" di 1;
Fine regola.

Regola "vano noto" per esaminare "mosaico" nella fase dopo priorità 10
quando "scoperta" di "mosaico" è vero:
    dì "Il vano è già aperto.";
Fine regola.

Regola "primo indizio" per esaminare "mosaico" nella fase dopo
quando "osservazioni" di "mosaico" è 1:
    dì "La luna sembra mobile: osservandola meglio potresti capire il meccanismo.";
Fine regola.

Regola "secondo esame" per esaminare "mosaico" nella fase dopo
quando "osservazioni" di "mosaico" è almeno 2 e "scoperta" di "mosaico" è falso:
    imposta "visibile" di "chiave" a vero;
    imposta "scoperta" di "mosaico" a vero;
    dì "La tessera scatta e rivela una chiave.";
Fine regola.
```

La regola con priorità 20 conta gli esami finché la scoperta non è avvenuta.
Quella con priorità 10 controlla se il vano era già noto. Infine le regole a
priorità 0 distinguono il primo indizio dalla scoperta: vedono già il contatore
aggiornato. Il flag arresta sia il conteggio sia la rivelazione dopo il secondo
esame, anche quando la chiave è ormai nell'inventario.

| Comando | Risultato atteso |
| --- | --- |
| `guarda` | Non incrementa il numero di osservazioni |
| `x mosaico` | Indizio sulla luna mobile, chiave ancora nascosta |
| `prendi chiave` | Fallisce e non incrementa il contatore |
| `g` | Ripete l'esame riuscito: scopre la chiave al secondo esame |
| `prendi chiave` | Raccoglie la chiave |
| `x mosaico` | Vano già aperto, nessuna nuova chiave |

**Variante:** cambia la soglia in tre osservazioni e la condizione del primo
indizio in `è minore di 3`. Verifica che il secondo esame dia ancora un indizio
e soltanto il terzo riveli la chiave. Cambiare soltanto la soglia lascerebbe il
secondo esame senza un messaggio di avanzamento.

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
