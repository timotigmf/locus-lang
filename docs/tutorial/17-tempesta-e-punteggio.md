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

## Soluzione: due scene sovrapposte

Apri `examples/tutorial/17b_scene_sovrapposte.locus` o copia questa storia:

```locus
Titolo: "Tempesta e segnale".
Autore: "Esempio LOCUS".

La Torre è una stanza.
Inizia nella Torre.

Scena "la tempesta" dal turno 1 al turno 3:
    Inizio "Il tuono scuote la torre.".
    Fine "Le nuvole si aprono.".
    Punti 10.
Fine scena.

Scena "il segnale" dal turno 2 al turno 4:
    Inizio "Una luce pulsa sul mare.".
    Fine "La luce si spegne all'orizzonte.".
    Punti 0.
Fine scena.
```

Usa `aspetta` quattro volte. Dopo ciascun comando consulta `turno` e
`punteggio`: le consultazioni non alterano il calendario.

| Turno | Scene attive | Scene concluse | Punteggio |
| --- | --- | --- | --- |
| 0 | Nessuna | Nessuna | 0 |
| 1 | la tempesta | Nessuna | 0 |
| 2 | la tempesta, il segnale | Nessuna | 0 |
| 3 | il segnale | la tempesta | 10 |
| 4 | Nessuna | la tempesta, il segnale | 10 |

Il segnale continua quando la tempesta è già conclusa: i due intervalli non
si annullano a vicenda. `Punti 0.` conclude normalmente la seconda scena,
senza aggiungere una voce al registro dei premi. Omettere la riga `Punti`
ha lo stesso valore predefinito zero.

**Controlli negativi.** Fra i turni 2 e 3 scrivi un comando sconosciuto come
`xyzzy`: entrambe le scene restano attive e il turno resta 2. Dopo il turno 4
usa ancora `aspetta`: non ricompaiono i testi conclusivi e il premio resta 10.
In **Regole e trace** puoi distinguere gli eventi delle due scene.

I turni sono assoluti dall'avvio della partita. La fine della tempesta non
avvia il segnale: è il suo intervallo dichiarato a determinarne l'inizio.
