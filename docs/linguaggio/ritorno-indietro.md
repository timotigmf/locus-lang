# Tornare al luogo precedente

Stato: implementato in LOCUS 0.5.0a1, senza cambiare la forma dell'IR 21.

Il giocatore può tornare al luogo lasciato con una delle forme:

```text
indietro
torna
torna indietro
vai indietro
back
go back
```

La sessione conserva l'identificatore dell'ultimo luogo soltanto dopo un
movimento riuscito. Il comando cerca nel grafo corrente un arco dal luogo
attuale a quello precedente. Se lo trova, percorre quella stessa direzione:
porte, veicoli, regole del mondo e validazione restano quindi identici al
comando esplicito.

Dopo il ritorno, il luogo appena lasciato diventa a sua volta il precedente.
Ripetere `indietro` alterna perciò fra due luoghi finché il collegamento resta
percorribile.

## Errori e passaggi a senso unico

Prima del primo spostamento LOCUS risponde:

```text
Non hai ancora lasciato un luogo a cui tornare.
```

Se il giocatore ha attraversato una botola o un altro arco a senso unico e non
esiste un collegamento inverso, risponde:

```text
Non puoi tornare indietro da qui.
```

Il comando non crea archi impliciti e non aggira una porta chiusa. Un tentativo
impossibile lascia invariati luogo, veicolo e memoria del percorso.

## Limiti

La memoria contiene un solo luogo, non una pila cronologica. `indietro` non
calcola percorsi alternativi e non attraversa più stanze; per quello servirà un
contratto separato di itinerario.
