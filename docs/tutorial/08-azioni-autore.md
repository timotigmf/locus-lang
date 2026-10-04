# 8. Creare azioni e comandi

Il progetto completo è `examples/tutorial/08_azioni.locus`. La lezione introduce
due azioni italiane con oggetti tipati e personalizza l'azione standard `attendere`.

```locus
Titolo: "Il custode del sigillo".
Autore: "Esempio LOCUS".

Una persona è un tipo di cosa.

La Sala delle Udienze è una stanza.
Inizia nella "Sala delle Udienze".
La Sala delle Udienze ha descrizione "Un custode attende davanti a una porta senza serratura.".

Il custode è una persona nella Sala delle Udienze.
Il "sigillo d'argilla" è una cosa nella Sala delle Udienze.
La fiducia è una proprietà numerica.
Il custode ha fiducia 0.

Azione "salutare" su una persona con comando "saluta".
Azione "mostrare" su una cosa con una persona con comando "mostra" e separatore "a".

Regola "attesa nella sala" per attendere nella fase invece:
    dì "Il custode rimane immobile mentre la polvere danza nella luce.";
Fine regola.

Regola "mostrare il sigillo" per mostrare "sigillo d'argilla" con "custode" nella fase invece:
    aumenta "fiducia" di "custode" di 1;
    dì "Il custode riconosce il sigillo e annuisce.";
Fine regola.

Regola "saluto riconoscente" per salutare "custode" nella fase invece priorità 10
quando "fiducia" di "custode" è almeno 1:
    dì "Il custode ti saluta come un ospite atteso.";
Fine regola.

Regola "saluto prudente" per salutare "custode" nella fase invece:
    dì "Il custode risponde con un cenno prudente.";
Fine regola.
```

## Prova guidata

Esegui `saluta custode`, `mostra sigillo al custode`, `saluta custode` e
`attendi`. `attendere` appartiene già alla libreria e può ricevere regole senza
una dichiarazione `Azione`. Il primo saluto usa la risposta prudente. Mostrare il sigillo aumenta
`fiducia`; il secondo saluto attiva la regola con priorità maggiore e condizione
vera. `al` viene riconosciuto come forma articolata del separatore `a`.

Apri **Indice del mondo**: sotto le entità compare la tabella delle azioni d'autore con
comando, tipi richiesti e separatore. Il trace distingue la regola esclusa per
condizione falsa da quella eseguita.

## Caso negativo

Prova `saluta sigillo`. Il sigillo è raggiungibile, ma non è una persona: LOCUS
risponde che il comando non si applica e non esegue alcuna regola. Anche questa
risposta fa parte del contratto testabile della storia.

## Esercizio

Definisci un tipo `strumento`, aggiungi un flauto e dichiara un'azione `suonare`
che accetti soltanto strumenti. Scrivi due regole: una per il flauto e una regola
generale che fallisca con un messaggio italiano. Verifica poi che un oggetto di
un altro tipo venga respinto prima delle regole.

## Soluzione: un comando riservato agli strumenti

Apri `examples/tutorial/08b_suonare_strumenti.locus` oppure copia:

```locus
Titolo: "Il flauto della sala".
Autore: "Esempio LOCUS".

La Sala è una stanza.
Inizia nella Sala.
Uno strumento è un tipo di cosa.
Uno strumento a fiato è un tipo di strumento.
Il flauto è uno strumento a fiato nella Sala.
Il tamburo è uno strumento nella Sala.
Il sigillo è una cosa nella Sala.

Azione "suonare" su uno strumento con comando "suona".

Regola "melodia del flauto" per suonare "flauto" nella fase invece priorità 10:
    dì "Una melodia limpida riempie la sala.";
Fine regola.

Regola "strumento senza partitura" per suonare nella fase verifica:
    fallisci "Non conosci una melodia per questo strumento.";
Fine regola.
```

| Comando | Risultato |
| --- | --- |
| `suona flauto` | La melodia riempie la sala |
| `suona tamburo` | Rifiuto dell'autore: manca una melodia |
| `suona sigillo` | Rifiuto di tipo prima di eseguire le regole |

Il flauto è accettato perché il suo tipo discende da `strumento`. La regola
`invece` sostituisce l'azione e termina normalmente prima della verifica generale.
Il tamburo ha il tipo corretto ma non una regola specifica: raggiunge quindi
`fallisci`. Il sigillo, invece, non supera il controllo del tipo dell'argomento.

In **Regole e trace** confronta i due rifiuti: per il tamburo compare la regola
di verifica; per il sigillo non viene eseguita nessuna regola di `suonare`.
Entrambi conservano lo stato della storia. Il testo narrato non riproduce un
file audio: per suoni e immagini consulta la lezione 21.
