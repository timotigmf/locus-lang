# Forme di comando multiparola

Stato: implementato in LOCUS 0.5.0a1, introdotto in IR 10 e conservato in IR 20.

Una forma dichiarata con `comando` o `sinonimo` può contenere da una a quattro
parole alfabetiche:

```locus
Una persona è un tipo di cosa.

Azione "tacere" senza oggetti con comando "fai silenzio"
    e sinonimo "resta immobile".
Azione "salutare" su una persona con comando "saluta solennemente".
```

Il parser confronta token completi dall'inizio del comando del giocatore. Le
parole fisse vengono consumate prima di risolvere gli oggetti. `fai silenzio`
attiva quindi `tacere`; `saluta solennemente custode` attiva `salutare` con
`custode` come primo oggetto.

Le forme multiparola funzionano anche con due oggetti e con i separatori di IR 9:

```locus
Una persona è un tipo di cosa.
Una reliquia è un tipo di cosa.

Azione "mostrare" su una reliquia con una persona con comando "fai vedere"
    e sinonimo "porta in vista" e separatore "a" e separatore "verso".
```

Sono validi `fai vedere amuleto al custode` e `porta in vista amuleto verso il
custode`. Tutte le forme producono lo stesso ID di azione e attraversano le
stesse regole.

## Collisioni di prefisso

Il compilatore rifiuta forme uguali e forme in cui una è prefisso token dell'altra.
Questa dichiarazione produce `E311`:

```text
comando "fai" e sinonimo "fai silenzio"
```

Senza il rifiuto, `fai silenzio` potrebbe indicare la forma lunga oppure il
comando `fai` con un oggetto chiamato `silenzio`. La stessa verifica comprende
tutte le azioni e i comandi standard: `guarda bene` è in conflitto con `guarda`.
Il confronto usa token, quindi `fai` non è prefisso di `faina`.

Il limite di quattro parole impedisce cataloghi patologici e mantiene piccoli i
controlli nel browser. Trattini, cifre, punteggiatura e parole vuote producono
`E311`. Maiuscole, accenti e spazi vengono normalizzati come nel resto di LOCUS.

## IR e limiti

`ActionIR.commands` resta una tupla di stringhe canoniche. In IR 10 ogni stringa
può rappresentare una sequenza da uno a quattro token. Il runtime verifica forma,
duplicati e collisioni di prefisso anche per IR costruite tramite API.

Le forme descritte qui occupano l'inizio. IR 11 ammette inoltre
[separatori multiparola](separatori-multiparola.md) fra due oggetti. Non sono
ancora disponibili parole fisse dopo il secondo oggetto, oggetti facoltativi,
clitici come `prendilo` o una disambiguazione proseguita nel turno successivo.
