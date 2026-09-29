# Metadati e vocabolario dell'autore

Stato: implementato in LOCUS 0.5.0a1, IR 6.

Questa specifica definisce il frontespizio della storia e i sinonimi nominali
scelti dall'autore. I costrutti sono parte del progetto compilato: funzionano
nella CLI, nello Studio e nelle release esportate.

## Titolo e autore

Un progetto può dichiarare una volta ciascuno titolo e autore:

```locus
Titolo: "Il sotterraneo dell'orologio".
Autore: "Ada Esempio".
```

La stringa può contenere spazi e punteggiatura e usa le regole di escape delle
altre stringhe LOCUS. Titolo e autore non creano entità e non cambiano la logica
del mondo. Lo Studio presenta questi valori dopo la compilazione. Ripetere lo
stesso metadato, anche in un file incluso, produce `E408`.

## Sinonimi degli oggetti

`Comprendi` associa una forma alternativa a un'entità dichiarata:

```locus
La Rimessa è una stanza.
La custodia impermeabile è un contenitore nella Rimessa.
Comprendi "scatola" come "custodia impermeabile".
Comprendi "cassa stagna" come "custodia impermeabile".
```

La forma generale è:

```ebnf
metadato = ("Titolo" | "Autore") ":" stringa "." ;
sinonimo = "Comprendi" stringa "come" stringa "." ;
```

Il bersaglio può essere dichiarato dopo la direttiva, perché viene risolto
dall'analisi semantica. Un bersaglio assente produce `E103`. Un alias uguale al
nome di un'entità o già assegnato produce `E409`; un alias vuoto non è sintassi
valida. LOCUS non sceglie
silenziosamente fra significati incompatibili.

Durante un comando, la risoluzione considera soltanto gli oggetti raggiungibili.
L'ordine è: nome esatto, sinonimo esatto, corrispondenza parziale fra nomi e
sinonimi. Una sola corrispondenza viene scelta; più corrispondenze generano una
richiesta di disambiguazione. Maiuscole, accenti Unicode normalizzati e spazi
ripetuti seguono la stessa canonicalizzazione dei nomi del sorgente.

I sinonimi riguardano i nomi delle entità nei comandi del giocatore. Non
ridefiniscono verbi, parole chiave del sorgente, preposizioni o riferimenti nelle
regole. I [pronomi singolari e clitici standard](pronomi-e-clitici.md) usano un
referente di sessione separato. Flessioni generali e un dizionario italiano
completo restano fuori da questo contratto.

## Rappresentazione interna

L'IR 6 conserva `title`, `author` e una sequenza di coppie alias/ID entità. Il
compilatore tratta queste coppie come simboli generici e non dipende dai tipi
della narrativa interattiva. Il runtime convalida bersagli e unicità prima di
creare il mondo; il parser giocatore resta separato dal parser autore.
