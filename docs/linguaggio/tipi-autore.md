# Tipi definiti dall'autore

Stato: implementato in LOCUS 0.5.0a1, IR 7.

Questa specifica permette di nominare categorie proprie e di ereditare il
comportamento di un tipo esistente. Il compilatore tratta la gerarchia in modo
generico; stanza, cosa, contenitore, porta e chiave appartengono alla libreria
narrativa, non al nucleo del linguaggio.

## Sintassi

Una dichiarazione di tipo precede o segue gli oggetti che la usano:

```locus
Una reliquia è un tipo di tesoro.
Un tesoro è un tipo di cosa.
Il rubino è una reliquia.
```

La forma grammaticale è:

```ebnf
dichiarazione_tipo = indefinito nome "è" indefinito "tipo" "di" nome_tipo "." ;
indefinito         = "un" | "uno" | "una" | "un'" ;
```

Il nome è singolare e può contenere più parole. Gli articoli non determinano
genere o numero: servono alla leggibilità e sono controllati solo sintatticamente.
I riferimenti in avanti sono validi, perciò `reliquia` può derivare da `tesoro`
prima della dichiarazione di `tesoro`.

## Ereditarietà e capacità

Ogni tipo ha al massimo un genitore. Un'entità di un sottotipo è accettata
ovunque sia richiesto un suo antenato. Nella libreria corrente:

```text
cosa
├── contenitore
└── chiave

stanza
porta
```

`contenitore` e `chiave` sono cose; stanza e porta sono radici separate. Quindi
un `reliquiario` derivato da contenitore si può aprire, può contenere oggetti ed
è trasportabile. Una `chiave rituale` derivata da chiave può aprire gli elementi
associati. Un `santuario` derivato da stanza compare nella mappa e può essere il
punto iniziale. Proprietà, relazioni, regole e convalida del mondo consultano la
stessa gerarchia.

```locus
Un santuario è un tipo di stanza.
Un reliquiario è un tipo di contenitore.
Una chiave rituale è un tipo di chiave.

La Cripta è un santuario.
Il cofano è un reliquiario nella Cripta.
La chiave di bronzo è una chiave rituale nella Cripta.
La chiave di bronzo apre il cofano.
```

## Identità, errori e progetto

I nomi sono confrontati con la stessa normalizzazione delle entità. Non si può
ridefinire un tipo della libreria o dichiarare due volte lo stesso tipo (`E113`).
Un genitore assente produce `E102`; un ciclo, anche attraverso riferimenti in
avanti, produce `E114`. Le dichiarazioni nei file inclusi appartengono alla stessa
gerarchia del progetto.

L'IR 7 contiene record `TypeIR(id, label, parent_id)`. Gli ID dei tipi dell'autore
sono deterministici per lo stesso ordine sorgente ma non sono identificatori
persistenti. Il runtime convalida unicità, genitori, cicli e tipi delle entità
prima di istanziare il mondo.

## Limiti attuali

L'ereditarietà è singola. Non sono ancora disponibili tratti, tipi parametrici,
enumerazioni, cambio di tipo durante la partita o proprietà dichiarate soltanto
per una categoria scelta dall'autore. Le azioni definite dall'autore formeranno
un pacchetto separato. Questi limiti evitano di attribuire alla frase una
semantica non ancora implementata.
