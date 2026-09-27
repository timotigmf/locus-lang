# Azioni e comandi definiti dall'autore

Stato: implementato in LOCUS 0.5.0a1, introdotto in IR 8 ed esteso fino a IR 10.

Questa specifica permette di dichiarare un'azione, assegnarle un comando italiano
e indicare i tipi dei suoi oggetti. Le regole forniscono comportamento e testo.
Il compilatore conserva azioni e comandi come strutture tipate: non riscrive il
sorgente e il runtime non interpreta frasi LOCUS.

## Dichiarazioni

Un'azione può richiedere zero, uno o due oggetti:

```locus
Una persona è un tipo di cosa.

Azione "attendere" senza oggetti con comando "attendi".
Azione "salutare" su una persona con comando "saluta".
Azione "mostrare" su una cosa con una persona con comando "mostra" e separatore "a".
```

La grammatica controllata è:

```ebnf
azione = "Azione" stringa
         ( "senza" "oggetti"
         | "su" indefinito tipo
           [ "con" indefinito tipo ] )
         "con" "comando" stringa
         { "e" ( "sinonimo" | "separatore" ) stringa } "." ;
```

Il nome fra virgolette è l'infinito usato nelle regole. `comando` è la forma
digitata dal giocatore. In IR 10 un comando contiene da una a quattro parole
alfabetiche normalizzate; ogni separatore resta una parola. Un'azione con due
oggetti richiede almeno un separatore.
Il nome dell'azione contiene parole alfabetiche e non usa `con` o `nella`, che
delimitano rispettivamente il secondo oggetto e la fase nelle regole.
Con il separatore `a`, il parser accetta anche `al`, `alla`, `allo`, `ai`,
`agli`, `alle` e `all'`; la specifica della grammatica elenca le articolazioni
riconosciute anche per `di`, `da`, `in`, `su` e `con`.

I tipi possono essere della libreria o definiti dall'autore e possono comparire
prima o dopo l'azione. Un sottotipo è valido dove è richiesto un suo antenato.
Il controllo avviene sia nei selettori e nelle sostituzioni delle regole sia nei
comandi del giocatore.

## Comportamento attraverso le regole

La dichiarazione registra l'azione ma non inventa un effetto. Senza una regola,
il comando riesce e risponde `Non accade nulla.`. Una regola nella fase `invece`
fornisce il comportamento completo e sostituisce quel testo:

```locus
Una persona è un tipo di cosa.
La Sala è una stanza.
Il custode è una persona nella Sala.

Azione "salutare" su una persona con comando "saluta".

Regola "saluto" per salutare "custode" nella fase invece:
    dì "Il custode ricambia il saluto.";
Fine regola.
```

Il giocatore può ora digitare `saluta custode`. Le sei fasi, le priorità, le
condizioni, il rollback e le sostituzioni sono gli stessi delle azioni della
libreria. `sostituisci con salutare "custode";` è quindi un'operazione strutturata
e controllata staticamente.

## Collisioni e diagnostica

Il nome di un'azione deve essere unico nel catalogo del progetto. Una ripetizione
o la ridefinizione di un'azione della libreria produce `E310`. Il comando deve
essere unico e non può occupare forme standard come `guarda`, `prendi`, `x` o
`nord`; una forma non valida, un duplicato o un separatore incoerente produce
`E311`. Un tipo assente produce `E102`; un oggetto di tipo errato in una regola
produce `E305`. Durante il gioco un oggetto raggiungibile ma incompatibile riceve
un rifiuto esplicito, senza eseguire regole né modificare lo stato.

## IR e separazione dei parser

L'IR 10 usa `ActionIR(id, label, commands, target_type_id,
indirect_type_id, separators)`. Il runtime convalida ID, nomi, comandi, separatori
e riferimenti ai tipi. Il parser autore produce dichiarazioni; il parser giocatore
riceve soltanto i record compilati. CLI, Studio e release web usano lo stesso
catalogo e lo stesso dispatcher.

## Limiti attuali

La [grammatica dei comandi](grammatica-comandi-autore.md) permette più sinonimi e
separatori espliciti. Mancano ancora pattern multiparola, clitici e argomenti
impliciti come “l'oggetto corrente” nel corpo di una regola generica. Le regole
possono selezionare un'entità precisa oppure tutte le entità dell'azione, ma gli
effetti continuano a nominare esplicitamente i propri destinatari.
