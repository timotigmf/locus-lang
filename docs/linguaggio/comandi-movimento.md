# Comandi naturali di movimento

Stato: implementato in LOCUS 0.5.0a1, senza cambiare la forma dell'IR 21.

Il giocatore può scrivere una direzione da sola oppure introdurla con un verbo
di movimento:

```text
nord
vai a nord
cammina verso sudovest
muoviti in alto
dirigiti all'esterno
procedi dentro
```

Sono riconosciuti `vai`, `cammina`, `muoviti`, `dirigiti` e `procedi`. Le forme
classiche inglesi `go`, `move` e `walk` accettano le stesse direzioni e
abbreviazioni già disponibili in LOCUS. Fra verbo e direzione si può omettere la
preposizione oppure usare `a`, `verso` o `in`; sono accettate anche le forme
articolate necessarie, come `all'esterno`.

La destinazione resta una delle dodici direzioni strutturate: cardinali,
diagonali, `su`/`giù` e `dentro`/`fuori`. Il parser produce lo stesso intento
tipato della forma breve; il runtime non reinterpreta la frase.

## Correzioni precise

Un verbo senza direzione non consuma un turno e produce:

```text
Indica in quale direzione vuoi andare.
```

Una destinazione che non appartiene al catalogo direzionale produce:

```text
Direzione non riconosciuta. Usa nord, sud, est, ovest, le diagonali, su, giù, dentro o fuori.
```

Questa distinzione evita di presentare il generico «Comando non riconosciuto»
quando l'intenzione di muoversi è già chiara. I verbi introduttivi sono comandi
standard riservati; un'azione dell'autore non può riusarli come prefisso.

## Limiti

Il comando indica una direzione, non il nome di una stanza. `vai alla Cripta`
non calcola automaticamente un percorso: produce la correzione sulle direzioni.
La pianificazione di itinerari e il movimento attraverso più stanze richiedono
un contratto separato.
