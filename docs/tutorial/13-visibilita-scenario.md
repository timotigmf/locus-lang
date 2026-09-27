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
