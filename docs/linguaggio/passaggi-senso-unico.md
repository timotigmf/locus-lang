# Passaggi a senso unico

Stato: implementato in LOCUS 0.5.0a1, senza cambiare la forma dell'IR 21.

## Dichiarazione

La forma dedicata nomina prima l'origine, poi la direzione e infine la
destinazione:

```locus
La Sala è una stanza.
La Cripta è una stanza.
Dalla Sala si va a nord verso la Cripta.
```

Sono accettate le preposizioni articolate `dalla`, `dal`, `dallo` e `dall'`.
La direzione usa lo stesso catalogo delle relazioni ordinarie, quindi comprende
cardinali, diagonali, `su`/`giù` e `dentro`/`fuori`. `a` precede normalmente
cardinali e diagonali; può essere omessa nelle forme naturali `si va su`, `si va
giù`, `si va dentro` e `si va fuori`. Nomi composti e nomi tra virgolette
seguono le regole comuni dei sintagmi nominali.

La dichiarazione emette soltanto l'arco strutturato dall'origine alla
destinazione. Non genera l'inversa che una frase ordinaria produrrebbe.

```text
La Cripta è a nord della Sala.
Dalla Sala si va a nord verso la Cripta.
```

La prima frase crea `nord` e `sud`; la seconda crea soltanto `nord`. Sono due
alternative e non vanno usate insieme per descrivere lo stesso passaggio.

## Controlli

Entità, tipi, auto-collegamenti e conflitti usano i controlli delle altre
relazioni. Una direzione assente dal catalogo produce `E104`; estremità
incompatibili producono `E105`; due destinazioni dalla stessa origine nella
stessa direzione producono `E106`; un collegamento riflessivo produce `E107`.
La frase è risolta dal compilatore e non viene reinterpretata come testo nel
runtime.

## Runtime e atlante

I comandi di movimento consultano soltanto gli archi presenti. Arrivati alla
destinazione, il comando opposto produce `no_exit` se l'autore non ha dichiarato
un altro collegamento. Porte e veicoli applicano gli stessi controlli atomici
dei passaggi bidirezionali.

Lo Studio aggiunge `oneWay: true` al collegamento esportato e disegna una
freccia orientata. L'etichetta mostra la sola direzione seguita da
`(solo andata)`. I collegamenti ordinari conservano il formato precedente.

## Limiti

Le regole dinamiche continuano a creare e rimuovere insieme una relazione e la
sua inversa. Una futura estensione potrà rendere esplicita la direzionalità
anche negli effetti delle regole. Un passaggio a senso unico non implica da
solo caduta, teletrasporto, danno o blocco narrativo: tali conseguenze vanno
modellate con regole e proprietà.
