# Livelli verticali: su e giù

Stato: implementato in LOCUS 0.5.0a1, senza cambiare la forma dell'IR 21.

## Dichiarazione naturale

`sovrasta` collega due stanze su livelli diversi:

```locus
La Sala è una stanza.
La Soffitta è una stanza.
La Soffitta sovrasta la Sala.
```

La frase crea `Sala — sopra → Soffitta` e l'inversa
`Soffitta — sotto → Sala`. Il compilatore generale non conosce il significato
spaziale di questi archi: `sovrasta` è un verbo registrato dalla stdlib mediante
lo stesso catalogo delle altre relazioni.

Due destinazioni diverse dalla stessa stanza verso `sopra` o `sotto` producono
`E106`. Le relazioni sono mutabili: una regola può usare
`crea relazione "sopra" da "Sala" a "Soffitta";` oppure la forma inversa con
`sotto`. Creazione, rimozione e inversa partecipano alla stessa transazione.

## Comandi del giocatore

| Direzione | Forme italiane | Forme classiche |
| --- | --- | --- |
| su | `su`, `alto` | `u`, `up` |
| giù | `giù`, `giu`, `basso` | `d`, `down` |

Senza un arco corrispondente il comando produce `no_exit` e non modifica la
sessione. Una porta può proteggere una scala o una botola; un veicolo guidato si
sposta insieme al giocatore anche fra livelli.

## Atlante

Lo Studio esporta un solo collegamento `su` per coppia inversa. La linea è
tratteggiata e porta l'etichetta `su / giù`, così resta distinguibile dai punti
cardinali in una mappa bidimensionale. In caso di sovrapposizione, l'atlante
sposta il livello sulla prima colonna libera senza cambiare il grafo compilato.

## Limiti

I livelli sono topologici: non hanno quota, altezza o distanza numerica. La
[navigazione dentro/fuori](dentro-fuori.md) usa relazioni distinte dal
contenimento `mondo.dentro`. I [passaggi a senso unico](passaggi-senso-unico.md)
e le [relazioni dinamiche](relazioni-dinamiche.md) coprono anche `su` e `giù`.
