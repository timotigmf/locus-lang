# Relazioni dinamiche e passaggi segreti

Questa specifica estende le regole con effetti strutturati sul grafo del mondo.
È introdotta dall'IR 12.

## Sintassi

```ebnf
effetto_relazione = ( "crea" | "rimuovi" ) "relazione" stringa
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

## Controlli statici

Il compilatore risolve i tre nomi, controlla i tipi degli estremi e rifiuta
auto-collegamenti. Solo uno schema di relazione dichiarato dinamico può essere
usato. La libreria standard abilita `nord`, `sud`, `est`, `ovest`, `nordest`,
`sudest`, `sudovest` e `nordovest`; contenimento, lati delle porte e relazione
fra chiave e serratura restano strutturali.

Una relazione sconosciuta, immutabile o riflessiva produce `E312`. Estremi di
tipo incompatibile producono `E305`. Gli effetti non sono ammessi nella fase
`verifica`, che resta priva di mutazioni (`E307`).

## Semantica runtime

Per una direzione, il compilatore inserisce nello stesso effetto anche l'inversa:
creare `nord` crea `sud` al ritorno; rimuoverla elimina entrambe. Ripetere la
stessa creazione o rimozione è idempotente. Se la sorgente possiede già una
destinazione diversa nella stessa direzione, l'azione fallisce.

Gli effetti partecipano alla transazione della regola. Un `fallisci` successivo,
un conflitto o un vincolo del mondo non valido ripristina relazioni, proprietà,
inventario e posizione precedenti. La mappa dello Studio viene ricavata dallo
snapshot corrente e cambia appena il passaggio viene rivelato o nascosto.

## Limiti

Il sorgente non può ancora dichiarare nuovi schemi di relazione. La versione
corrente riguarda gli otto collegamenti della rosa dei venti della libreria.
Visibilità degli oggetti, porte segrete come entità e collegamenti a senso unico
richiedono specifiche successive.
