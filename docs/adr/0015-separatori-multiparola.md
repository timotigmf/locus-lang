# ADR 0015 — separatori multiparola con articolazione finale

Stato: accettato.

## Contesto

L'IR 10 ammetteva locuzioni nella forma iniziale del comando, ma il collegamento
fra due oggetti restava una sola parola. Espressioni italiane come `in cambio
di`, `a proposito di` e `per mezzo di` non potevano essere descritte senza
introdurre comandi artificiali.

## Decisione

Un separatore contiene da uno a quattro token alfabetici fissi. Il parser cerca
una sequenza completa fra i due sintagmi nominali. Se l'ultimo token è una
preposizione italiana supportata, genera le relative forme articolate. Il
compilatore e il runtime rifiutano duplicati e rapporti di prefisso fra tutte le
varianti, comprese quelle articolate. L'IR 11 mantiene la tupla `separators` e ne
estende il contratto di validazione e interpretazione.

## Alternative considerate

- Spezzare la locuzione e riconoscere soltanto l'ultima preposizione: scartato
  perché parole del primo nome potrebbero essere consumate come grammatica.
- Scegliere sempre la sequenza più lunga: scartato perché un nuovo separatore
  potrebbe cambiare il significato di un comando già valido.
- Introdurre subito pattern arbitrari con ruoli nominati: rinviato; richiede un
  modello più generale per ordine, opzionalità e diagnostica degli argomenti.

## Conseguenze

I comandi a due oggetti esprimono locuzioni italiane comuni senza euristiche e
mantengono una sola interpretazione. Restano esclusi i pattern con parole fisse
dopo il secondo oggetto, gli argomenti facoltativi e le azioni con più di due
oggetti.
