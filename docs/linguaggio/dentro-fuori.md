# Dentro e fuori

Stato: implementato in LOCUS 0.5.0a1, senza cambiare la forma dell'IR 21.

## Dichiarazione naturale

`racchiude` collega un luogo esterno a un luogo interno:

```locus
La Villa è una stanza.
L'Atrio è una stanza.
La Villa racchiude l'Atrio.
```

La frase crea `Villa — interno → Atrio` e l'inversa
`Atrio — esterno → Villa`. Questi archi descrivono la navigazione fra stanze e
sono distinti da `mondo.dentro`, che colloca oggetti, persone e veicoli.

Due interni diversi dichiarati dalla stessa stanza producono `E106`. Le
relazioni sono mutabili: una regola può usare
`crea relazione "dentro" da "Villa" a "Atrio";` e rimuoverla in seguito. La
relazione inversa partecipa alla stessa transazione.

## Comandi del giocatore

| Direzione | Forme italiane | Forme classiche |
| --- | --- | --- |
| dentro | `dentro`, `interno` | `in`, `inside` |
| fuori | `fuori`, `esterno` | `out`, `outside` |

`esci` e `q` continuano a terminare la sessione. `entra nella saetta` e `enter`
restano comandi dei veicoli; in una storia senza veicoli l'autore può ancora
definire un'azione propria chiamata `entra`. Se non esiste l'arco richiesto,
LOCUS risponde «Non c'è alcun passaggio in quella direzione.» senza cambiare la
sessione.

Una porta può proteggere un passaggio dentro/fuori. Un veicolo guidato attraversa
il collegamento insieme al giocatore, con validazione atomica dello stato.

## Atlante

Lo Studio esporta un solo collegamento `dentro` per coppia inversa. L'atlante lo
mostra con una linea puntinata e l'etichetta `dentro / fuori`, distinta dalle
linee continue della rosa dei venti e dal tratteggio dei livelli verticali.

## Limiti

Il collegamento è topologico: non implica contenimento fisico, regione, edificio
o visibilità. Ogni luogo ha una sola destinazione per direzione. I
[passaggi a senso unico](passaggi-senso-unico.md) possono usare anche `dentro`
e `fuori`; regioni con più accessi richiedono una specifica separata.
