# Sinonimi e separatori delle azioni

Stato: implementato in LOCUS 0.5.0a1, introdotto in IR 9, esteso fino a IR 11 e conservato in IR 18.

Questa specifica estende le [azioni definite dall'autore](azioni-autore.md) con
forme di comando equivalenti e separatori alternativi dichiarati esplicitamente.
Il compilatore risolve le forme in un catalogo tipato; il parser del giocatore
non coniuga verbi, non interroga un dizionario remoto e non riscrive testo.

## Forme di comando

La prima forma segue `con comando`. Ogni clausola `e sinonimo` aggiunge una
forma equivalente:

```locus
Una persona è un tipo di cosa.

Azione "salutare" su una persona con comando "saluta"
    e sinonimo "riverisci" e sinonimo "inchinati".
```

`saluta custode`, `riverisci custode` e `inchinati custode` producono lo stesso
ID di azione e attraversano le stesse regole. Le forme contengono da una a quattro
parole alfabetiche. La lista è esplicita perché l'imperativo italiano non si ricava in modo
affidabile dall'infinito, soprattutto per verbi irregolari e pronominali.

## Separatori alternativi

Un'azione con due oggetti dichiara uno o più separatori, ciascuno formato da una
a quattro parole:

```locus
Una persona è un tipo di cosa.
Una reliquia è un tipo di cosa.

Azione "mostrare" su una reliquia con una persona con comando "mostra"
    e sinonimo "esibisci" e separatore "a" e separatore "verso".
```

Sono quindi equivalenti `mostra amuleto al custode` ed `esibisci amuleto verso
il custode`. Per `a`, `di`, `da`, `in` e `su` sono riconosciute anche le forme
articolate italiane singolari e plurali; `con` riconosce anche `col` e `coi`.
Una forma apostrofata unita al nome, come `dell'amuleto`, viene separata senza
perdere il nome dell'oggetto.
Locuzioni come `in cambio di` e `a proposito di` articolano l'ultima
preposizione; la specifica completa è in [separatori multiparola](separatori-multiparola.md).

Se il nome di un oggetto contiene davvero una parola usata come separatore,
racchiudilo tra virgolette nel comando del giocatore: le parole interne a un nome
quotato non dividono gli argomenti.

Un'azione con zero o un oggetto non accetta separatori. Un'azione con due oggetti
ne richiede almeno uno. L'ordine delle clausole `e sinonimo` ed `e separatore`
non cambia la semantica.

## Collisioni e IR

Ogni forma di comando condivide lo stesso spazio di nomi con le altre azioni e
con i comandi standard. Duplicati, forme non valide, collisioni e separatori
duplicati o incoerenti producono `E311` sulla dichiarazione. La verifica avviene
prima di compilare le regole.

L'IR 9 ha sostituito i campi singolari di `ActionIR` con `commands` e `separators`;
l'IR 10 ammette più token in ogni comando e l'IR 11 in ogni separatore. Entrambi restano tuple ordinate e non
vuote quando richiesto dall'arità. Il runtime
convalida l'intero catalogo, inclusa l'unicità globale delle forme di comando.
CLI, Studio e release web consumano direttamente questi record.

## Limiti

Non sono ancora disponibili pattern liberi con ruoli nominati, pronomi e
clitici, oggetti sottintesi
o una domanda di chiarimento che continui nel turno successivo. L'ambiguità fra
nomi di oggetto continua a produrre una richiesta esplicita con le alternative.
