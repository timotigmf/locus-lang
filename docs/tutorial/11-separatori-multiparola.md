# 11. Collegare due oggetti con una locuzione

Il progetto completo è `examples/tutorial/11_separatori_multiparola.locus`.
Questa lezione costruisce comandi italiani in cui i due oggetti sono collegati
da una locuzione, non soltanto da una preposizione.

```locus
Una persona è un tipo di cosa.
Una merce è un tipo di cosa.

Il Banco è una stanza.
Il mercante è una persona nella Banco.
La moneta è una merce nella Banco.
La chiave di vetro è una merce nella Banco.
L'amuleto è una merce nella Banco.

Azione "scambiare" su una merce con una merce con comando "scambia"
    e sinonimo "dai in pegno"
    e separatore "in cambio di" e separatore "insieme a".
Azione "consultare" su una persona con una merce con comando "interroga"
    e separatore "a proposito di".

Regola "baratto registrato" per scambiare "moneta" con "chiave di vetro"
    nella fase invece:
    dì "Il mercante registra lo scambio e ripone la moneta.";
Fine regola.

Regola "domanda sull'amuleto" per consultare "mercante" con "amuleto"
    nella fase invece:
    dì "Il mercante indica il sigillo inciso sotto l'amuleto.";
Fine regola.
```

## Prova guidata

```text
scambia moneta in cambio della chiave di vetro
dai in pegno moneta insieme alla chiave di vetro
interroga mercante a proposito dell'amuleto
```

La forma `della` deriva automaticamente dall'ultima parola `di`; `alla` deriva
da `a`. Nel secondo comando LOCUS consuma prima la forma iniziale multiparola
`dai in pegno`, poi cerca l'intera sequenza `insieme alla`.

Prova anche `scambia moneta in chiave di vetro`: viene rifiutato perché `in` non
è un separatore dichiarato e non basta a sostituire `in cambio di`.

## Errore da correggere

Non dichiarare insieme `in` e `in cambio di`. La forma breve sarebbe un prefisso
della lunga e il compilatore produce `E311`. Usa forme indipendenti, per esempio
`con` e `in cambio di`.

## Esercizio

Definisci un'azione `confrontare` su due merci con comando `confronta` e
separatori `rispetto a` e `a paragone con`. Scrivi una regola per confrontare
l'amuleto con la chiave di vetro e prova anche le forme articolate dell'ultima
preposizione.
