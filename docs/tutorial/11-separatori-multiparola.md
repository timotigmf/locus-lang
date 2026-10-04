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

## Soluzione: confrontare i sigilli

Apri `examples/tutorial/11b_confrontare_sigilli.locus` oppure copia:

```locus
Titolo: "Il confronto dei sigilli".
Autore: "Esempio LOCUS".
Il Banco è una stanza.
Inizia nel Banco.
Una merce è un tipo di cosa.
L'amuleto è una merce nel Banco.
La chiave di vetro è una merce nel Banco.

Azione "confrontare" su una merce con una merce con comando "confronta"
    e separatore "rispetto a" e separatore "a paragone con".

Regola "sigilli uguali" per confrontare "amuleto" con "chiave di vetro" nella fase invece:
    dì "Lo stesso sigillo compare sull'amuleto e sulla chiave.";
Fine regola.
```

Queste tre forme attivano la stessa regola:

```text
confronta amuleto rispetto a la chiave di vetro
confronta amuleto rispetto alla chiave di vetro
confronta amuleto a paragone con la chiave di vetro
```

La prima forma rende visibile il confine fra separatore e articolo, anche se
in italiano corrente preferirai `rispetto alla`. Con `a paragone con` usa la forma `con la`: in questo
incremento la variante `colla` non è riconosciuta.

**Controlli negativi.** `confronta amuleto rispetto chiave` omette la preposizione;
`confronta amuleto a paragone chiave` omette `con`. Nessuna delle due frasi
attiva il confronto. Anche il secondo oggetto deve essere presente: fermarsi a
`rispetto alla` non basta.

Questo esempio confronta soltanto due oggetti, senza trasferirli. Nel precedente
banco degli scambi il messaggio di baratto è narrativo: la regola aumenta la
fiducia, ma non sposta la moneta né la chiave. Un trasferimento effettivo richiede
effetti espliciti; il nome del comando non li aggiunge automaticamente.
