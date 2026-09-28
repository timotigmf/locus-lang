# ADR 0021 — scene temporali e registro del punteggio

Stato: accettato, 28 settembre 2026.

## Contesto

Le proprietà numeriche permettono di simulare contatori, ma non distinguono il
tempo della sessione, il ciclo di vita di una scena o la provenienza di un
premio. Affidare questi concetti a testi e convenzioni impedirebbe allo Studio e
ai test di ispezionarli in modo affidabile.

## Decisione

AST e IR aggiungono scene immutabili con ID, nome, turni iniziale e finale,
testi e punti. Il compilatore controlla unicità e limiti; il runtime generico
valida il catalogo senza conoscere i comandi del giocatore.

La sessione della libreria narrativa conserva turno, scene attive e concluse,
punteggio e registro dei premi. Il tempo avanza dopo un comando riconosciuto;
avvio, metacomandi, errori di parsing, ambiguità ed errori di scelta non
consumano turni. La conclusione assegna il premio una sola volta. Ogni
transizione espone un trace strutturato degli eventi di scena. L'IR sale alla
versione 17.

I comandi `turno`, `tempo`, `punteggio` e `score` vengono riservati soltanto se
il progetto dichiara scene, conservando le azioni omonime delle storie esistenti.

## Alternative considerate

- Proprietà globali convenzionali: scartate perché non registrano identità,
  provenienza e completamento delle scene.
- Far avanzare il tempo anche sugli errori del parser: scartato perché un refuso
  cambierebbe il mondo prima che il giocatore abbia espresso un'azione valida.
- Condizioni ed effetti arbitrari nel primo incremento: rinviati per integrarli
  con il rulebook e il rollback senza creare un secondo motore di regole.
- Punteggio come semplice intero: scartato; il registro rende ogni premio
  spiegabile e impedisce assegnazioni ripetute.

## Conseguenze

Le scene temporali sono riproducibili nei transcript e ispezionabili nello
Studio. Scene condizionali, ricorrenti e capaci di effetti restano estensioni
del contratto, non interpretazioni implicite dei testi.
