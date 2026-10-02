# 39. Chiedere aiuto durante la partita

Apri `examples/tutorial/39_aiuto_in_partita.locus` nello Studio e premi
**Compila e prova**. La storia dichiara il comando proprio `suona NOME`.

```locus
La "Sala della Campana" è una stanza.
La campana è una cosa nella "Sala della Campana".

Azione "suonare" su una cosa con comando "suona".
Regola "rintocco" per suonare "campana" nella fase invece:
    dì "Un rintocco attraversa la torre.";
Fine regola.
```

## Prova guidata

1. Scrivi `aiuto`: compaiono movimento, oggetti e comandi di sessione.
2. Cerca l'ultima riga: `suona` appare fra le azioni della storia.
3. Scrivi `suona campana` e verifica il rintocco.
4. Prova anche `comandi`, `help` e `?`: producono lo stesso elenco.

L'aiuto non fa avanzare il turno. In una storia con scene puoi verificarlo con
`turno`, poi `aiuto`, poi ancora `turno`.

## Caso negativo

Scrivi `aiuto movimento`. Gli argomenti tematici non sono ancora supportati e
LOCUS risponde come a un comando sconosciuto, suggerendo il comando completo
`aiuto`.

## Esercizio

Aggiungi all'esempio una seconda azione con comando `ascolta`. Ricompila e
controlla che l'aiuto mostri `ascolta, suona` in ordine stabile, senza dover
aggiornare manualmente un elenco.

Il [riferimento sull'aiuto in partita](../linguaggio/aiuto-in-partita.md)
descrive il comportamento contestuale e i limiti attuali.
