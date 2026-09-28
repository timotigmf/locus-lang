# Separatori composti da più parole

Stato: implementato in LOCUS 0.5.0a1, introdotto in IR 11 e conservato in IR 21.

Un'azione con due oggetti separa il primo nome dal secondo mediante una o più
forme dichiarate. Ogni forma può contenere da una a quattro parole alfabetiche:

```locus
Una merce è un tipo di cosa.

Azione "scambiare" su una merce con una merce con comando "scambia"
    e separatore "in cambio di" e separatore "insieme a" e separatore "con".
```

Sono quindi validi:

```text
scambia moneta in cambio della chiave di vetro
scambia moneta insieme alla chiave di vetro
```

Il parser consuma prima la forma iniziale del comando. Cerca poi una sola
sequenza separatrice completa e assegna i token precedenti al primo oggetto e
quelli successivi al secondo. Una forma incompleta come `in cambio` non separa
gli oggetti.

## Preposizioni articolate

Se l'ultima parola è `a`, `in`, `di`, `da`, `su` o `con`, LOCUS ne accetta anche
le forme articolate già supportate dai separatori semplici. Per esempio:

- `insieme a` riconosce `insieme al`, `insieme alla` e `insieme all'`;
- `a proposito di` riconosce `a proposito del`, `della` e `dell'`;
- `per mezzo di` riconosce `per mezzo dei` e `degli`.

Il nome che segue conserva il normale trattamento degli articoli. `interroga
mercante a proposito dell'amuleto` risolve quindi `mercante` e `amuleto`.

## Assenza di ambiguità

Le forme uguali o in rapporto di prefisso producono `E311`:

```text
separatore "in" e separatore "in cambio di"
```

La verifica considera anche le forme articolate. `a` e `al posto di` sono in
conflitto perché `a` genera la variante `al`, prefisso della seconda forma. In
questo modo l'aggiunta di un nuovo separatore non cambia il significato di una
frase esistente.

Se una sequenza separatrice compare più volte fuori dalle virgolette, il comando
è rifiutato come non riconoscibile. Le virgolette proteggono invece un nome che
contiene davvero la locuzione: `scambia "moneta in cambio di rame" con chiave`
usa soltanto `con` come separatore.

## IR e limiti

`ActionIR.separators` resta una tupla di stringhe canoniche. In IR 11 ogni
stringa contiene da uno a quattro token fissi; compilatore e runtime verificano
forma, duplicati, prefissi e varianti articolate. Non sono ancora disponibili
ruoli nominati, oggetti facoltativi, più di due oggetti o parole fisse dopo il
secondo oggetto.
