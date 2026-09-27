# 10. Usare comandi composti da più parole

Il progetto completo è `examples/tutorial/10_comandi_multiparola.locus`. La
lezione introduce locuzioni iniziali esplicite senza affidarsi a correzioni o
deduzioni automatiche.

```locus
Una persona è un tipo di cosa.
Una reliquia è un tipo di cosa.

La Sala Verde è una stanza.
Il custode è una persona nella Sala Verde.
L'amuleto è una reliquia nella Sala Verde.

Azione "tacere" senza oggetti con comando "fai silenzio"
    e sinonimo "resta immobile".
Azione "salutare" su una persona con comando "saluta solennemente"
    e sinonimo "onora".
Azione "mostrare" su una reliquia con una persona con comando "fai vedere"
    e sinonimo "porta in vista" e separatore "a" e separatore "verso".

Regola "silenzio rituale" per tacere nella fase invece:
    dì "La sala sprofonda nel silenzio.";
Fine regola.

Regola "saluto rituale" per salutare "custode" nella fase invece:
    dì "Il custode china il capo.";
Fine regola.

Regola "amuleto mostrato" per mostrare "amuleto" con "custode" nella fase invece:
    dì "Il custode riconosce l'amuleto e apre il registro.";
Fine regola.
```

## Prova guidata

Prova queste frasi:

```text
fai silenzio
resta immobile
saluta solennemente custode
onora custode
fai vedere amuleto al custode
porta in vista amuleto verso il custode
```

`fai` da solo non è un comando: LOCUS richiede l'intera forma dichiarata. Anche
`fai silenzio ora` viene rifiutato perché l'azione non accetta oggetti.

## Collisione da correggere

Non aggiungere contemporaneamente `fai` e `fai silenzio`. Il compilatore produce
`E311` perché la prima forma è un prefisso della seconda. Scegli invece due forme
senza prefissi, per esempio `agisci` e `fai silenzio`.

## Esercizio

Definisci un'azione `prestare attenzione` su una persona con le forme `ascolta
con cura` e `presta attenzione`. Aggiungi una regola per il custode e verifica
che la parola immediatamente successiva alla forma completa diventi l'oggetto.
