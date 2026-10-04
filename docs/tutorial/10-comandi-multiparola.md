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

## Soluzione: ascoltare il custode

Apri `examples/tutorial/10b_ascoltare_custode.locus` oppure copia:

```locus
Titolo: "Le parole del custode".
Autore: "Esempio LOCUS".
La Sala è una stanza.
Inizia nella Sala.
Il custode anziano è una persona nella Sala.
La campana è una cosa nella Sala.

Azione "prestare attenzione" su una persona con comando "ascolta con cura"
    e sinonimo "presta attenzione".

Regola "consiglio del custode" per prestare attenzione "custode anziano" nella fase invece:
    dì "Il custode consiglia di osservare la parete a nord.";
Fine regola.
```

Prova `ascolta con cura il custode anziano` e `presta attenzione custode`:
entrambi attivano il consiglio. Il parser consuma prima la forma completa e
risolve poi il nome, anche parziale, della persona. L'articolo `il` è facoltativo.

**Controlli negativi.** `ascolta con custode` omette una parola fissa e non
attiva il consiglio. `presta attenzione` omette l'oggetto. Infine,
`ascolta con cura campana` ha una forma valida ma un argomento del tipo sbagliato:
nessuna regola del consiglio viene eseguita. Questi tre errori richiedono
correzioni diverse: completare la locuzione, indicare l'oggetto, scegliere una persona.

Il consiglio è solo testo: non crea un passaggio a nord né rivela una parete.
Per una scoperta che cambia il mondo combina l'azione con gli effetti delle
lezioni 12 e 13.
