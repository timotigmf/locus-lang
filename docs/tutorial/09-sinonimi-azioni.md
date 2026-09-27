# 9. Dare più forme ai comandi

Il progetto completo è `examples/tutorial/09_sinonimi_azioni.locus`. Questa
lezione rende più naturale il vocabolario di una storia mantenendo ogni forma
esplicita e controllabile.

```locus
Una persona è un tipo di cosa.
Una reliquia è un tipo di cosa.

La Sala delle Insegne è una stanza.
Il custode è una persona nella Sala delle Insegne.
L'amuleto è una reliquia nella Sala delle Insegne.

Azione "salutare" su una persona con comando "saluta"
    e sinonimo "riverisci" e sinonimo "inchinati".

Azione "mostrare" su una reliquia con una persona con comando "mostra"
    e sinonimo "esibisci" e separatore "a" e separatore "verso".

Regola "saluto" per salutare "custode" nella fase invece:
    dì "Il custode ricambia il saluto.";
Fine regola.

Regola "mostrare amuleto" per mostrare "amuleto" con "custode" nella fase invece:
    dì "Il custode riconosce l'amuleto.";
Fine regola.
```

## Prova guidata

Esegui in sequenza:

```text
saluta custode
riverisci custode
inchinati custode
mostra amuleto al custode
esibisci amuleto verso il custode
```

Le prime tre frasi attivano tutte `salutare`; le ultime due attivano `mostrare`.
Nell'**Indice del mondo** la colonna Comando mostra tutte le forme e la colonna
Oggetti elenca entrambi i separatori.

Il progetto completo aggiunge anche l'azione `parlare`, con separatori `di` e
`su`. Prova `parla custode dell'amuleto` e `racconta custode sull'amuleto`:
l'apostrofo e la preposizione articolata non diventano parte del nome.

## Errori utili

Se aggiungi `e sinonimo "x"`, la compilazione produce `E311`: `x` è già il
comando standard per esaminare. Lo stesso codice segnala due sinonimi uguali,
un separatore su un'azione con un solo oggetto o un'azione a due oggetti priva
di separatore.

## Esercizio

Definisci un'azione `consegnare` fra una cosa e una persona. Accetta `consegna`
e `dai` come forme, più `a` e `verso` come separatori. Scrivi una regola per una
lettera e verifica sia `consegna lettera alla messaggera` sia `dai lettera verso
la messaggera`.
