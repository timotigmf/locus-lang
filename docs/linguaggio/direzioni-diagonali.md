# Otto direzioni della rosa dei venti

Stato: implementato in LOCUS 0.5.0a1, senza cambiare la forma dell'IR 21.

## Dichiarazioni

La libreria narrativa offre otto relazioni fra stanze. Alle quattro cardinali
`nord`, `sud`, `est` e `ovest` si aggiungono `nordest`, `sudest`, `sudovest` e
`nordovest`.

```locus
La Piazza è una stanza.
La Vedetta è una stanza.
La Vedetta è a nordest della Piazza.
```

Ogni relazione crea automaticamente l'inversa: nell'esempio la Piazza è a
`sudovest` della Vedetta. Ripetere lo stesso collegamento è idempotente. Due
destinazioni diverse dalla stessa stanza nella stessa direzione producono
`E106`, con la posizione della dichiarazione in conflitto.

Le otto relazioni sono dinamiche. Una regola può quindi creare o rimuovere, per
esempio, una relazione `nordest`; l'effetto include anche `sudovest` e partecipa
allo stesso rollback degli altri effetti.

## Comandi del giocatore

| Direzione | Abbreviazione | Forma inglese |
| --- | --- | --- |
| nordest | `ne` | `northeast` |
| sudest | `se` | `southeast` |
| sudovest | `so` | `southwest` |
| nordovest | `no`, `nw` | `northwest` |

Un comando direzionale valido senza uscita produce `no_exit` e il testo «Non
c'è alcun passaggio in quella direzione.»; la sessione non cambia. Le porte
possono proteggere anche un passaggio diagonale perché il controllo usa gli
estremi del collegamento, non il nome della direzione.

La mappa esporta una sola linea per ogni coppia inversa e dispone i quattro assi
diagonali in modo coerente. Quando più percorsi richiedono la stessa posizione,
il layout sposta una stanza sulla linea libera più vicina.

## Limiti

`Su` e `giù` sono definiti dalla specifica dei
[livelli verticali](livelli-verticali.md) e nella specifica
[dentro/fuori](dentro-fuori.md). Il passaggio direzionale `dentro` resta distinto
dalla relazione strutturale `mondo.dentro`, usata per collocare oggetti e veicoli. Percorsi a senso unico
richiedono un contratto successivo.
