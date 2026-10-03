# Relazioni dinamiche e passaggi segreti

Questa specifica estende le regole con effetti strutturati sul grafo del mondo.
È introdotta dall'IR 12.

## Sintassi

```ebnf
effetto_relazione = ( "crea" | "rimuovi" ) "relazione"
                    [ "a" "senso" "unico" ] stringa
                    "da" stringa "a" stringa ";" ;
```

Il primo testo è il nome del predicato registrato, seguito dall'entità sorgente
e da quella destinazione. Per esempio:

```locus
La Anticamera è una stanza.
La Cripta è una stanza.
La leva è una cosa nella Anticamera.

Regola "prova il meccanismo" per esaminare "leva" nella fase dopo:
    crea relazione "nord" da "Anticamera" a "Cripta";
    rimuovi relazione "nord" da "Anticamera" a "Cripta";
Fine regola.
```

La forma è intenzionalmente esplicita: `Anticamera` è davvero la sorgente
dell'arco `nord`. Non si applica l'inversione grammaticale usata dalla frase
statica `La Cripta è a nord della Anticamera.`.

La qualificazione `a senso unico` omette l'inversa ed è disponibile sia per la
creazione sia per la rimozione:

```locus
La Sala è una stanza.
La Cripta è una stanza.
La leva è una cosa nella Sala.

Regola "apri la botola" per esaminare "leva" nella fase dopo:
    crea relazione a senso unico "giù" da "Sala" a "Cripta";
Fine regola.
```

## Controlli statici

Il compilatore risolve i tre nomi, controlla i tipi degli estremi e rifiuta
auto-collegamenti. Solo uno schema di relazione dichiarato dinamico può essere
usato. La libreria standard abilita `nord`, `sud`, `est`, `ovest`, `nordest`,
`sudest`, `sudovest`, `nordovest`, `sopra`, `sotto`, `dentro` e `fuori`;
il contenimento degli oggetti, i lati delle porte e la relazione fra chiave e
serratura restano strutturali.

Una relazione sconosciuta, immutabile o riflessiva produce `E312`. Estremi di
tipo incompatibile producono `E305`. Gli effetti non sono ammessi nella fase
`verifica`, che resta priva di mutazioni (`E307`).

## Semantica runtime

Per una direzione, il compilatore inserisce nello stesso effetto anche l'inversa:
creare `nord` crea `sud` al ritorno; rimuoverla elimina entrambe. Ripetere la
stessa creazione o rimozione è idempotente. Se la sorgente possiede già una
destinazione diversa nella stessa direzione, l'azione fallisce.

Con `a senso unico`, il compilatore inserisce soltanto l'arco richiesto. La
creazione non aggiunge il ritorno e la rimozione non tocca un eventuale arco
opposto. In questa forma sono accettati anche `su`, `giù` e `giu` come alias
naturali di `sopra` e `sotto`.

Gli effetti partecipano alla transazione della regola. Un `fallisci` successivo,
un conflitto o un vincolo del mondo non valido ripristina relazioni, proprietà,
inventario e posizione precedenti. La mappa dello Studio viene ricavata dallo
snapshot corrente e cambia appena il passaggio viene rivelato o nascosto.

## Limiti

Il sorgente non può ancora dichiarare nuovi schemi di relazione. La versione
corrente riguarda le dodici direzioni della libreria.
Visibilità degli oggetti e porte segrete come entità richiedono specifiche
successive.

Il [laboratorio del contrappeso](../tutorial/12-passaggi-segreti.md) confronta
una rimozione seguita da `fallisci` con una riuscita: verifica entrambe le
direzioni, un flag, la descrizione e lo scarto dei messaggi intermedi.
