# 17. Una tempesta misurata in turni

Questa lezione introduce scene temporali, turni e premi registrati. Apri
`examples/tutorial/17_tempesta_e_punteggio.locus` nello Studio e scegli
**Compila e prova**.

## La scena

```locus
La Torre è una stanza.

Scena "la tempesta" dal turno 1 al turno 3:
    Inizio "Un tuono scuote la torre: la tempesta è iniziata.".
    Fine "Al terzo rintocco le nuvole si aprono e il faro torna visibile.".
    Punti 10.
Fine scena.
```

La descrizione iniziale non consuma tempo. Prova:

```text
> turno
Turno: 0.
> guarda
...
Un tuono scuote la torre: la tempesta è iniziata.
> inventario
Inventario: vuoto.
> esamina orologio
...
Al terzo rintocco le nuvole si aprono e il faro torna visibile.
> punteggio
Punteggio: 10.
```

`turno` e `punteggio` osservano lo stato senza far avanzare l'orologio. Il
premio compare una sola volta nel registro, anche continuando a giocare.

## Esperimento negativo

Cambia `dal turno 3 al turno 2`. La compilazione produce `E122`: il turno
finale deve seguire quello iniziale. Prova anche a ripetere `Punti`: ogni voce
del blocco può comparire una sola volta.

## Esercizio

Aggiungi una seconda scena dal turno 2 al turno 4 con premio zero. Osserva
nell'Indice del mondo che le due scene hanno identità separate e nel trace che
possono sovrapporsi.

La [specifica di scene, tempo e punteggio](../linguaggio/scene-tempo-punteggio.md)
elenca limiti e criteri di avanzamento.
