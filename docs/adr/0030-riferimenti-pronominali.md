# ADR 0030 — riferimenti pronominali di sessione

Stato: accettato, 2026-09-29.

## Contesto

Dopo aver identificato un oggetto, ripeterne sempre il nome rende artificiale il
dialogo. Un dizionario morfologico globale non risolve però il riferimento: `la`
può essere articolo o pronome e la storia non dichiara ancora il genere dei nomi.

## Decisione

La sessione conserva l'identificatore dell'ultimo oggetto diretto di un'azione
riuscita. I pronomi `esso`, `essa`, `questo`, `questa`, `quello`, `quella` e `it`
lo richiamano come oggetto diretto o indiretto. Il parser riconosce inoltre le
forme unite `prendilo/a`, `esaminalo/a`, `aprilo/a`, `chiudilo/a` e `lascialo/a`.

Il suffisso maschile o femminile non effettua ancora un controllo grammaticale:
entrambe le forme richiamano lo stesso referente. Senza referente il runtime
produce un evento dedicato e non consuma un turno. Un'azione fallita non cambia
il referente, preservando l'identità della sessione sui fallimenti.

## Alternative considerate

- Deducere il genere dall'articolo o dalla desinenza: fragile per nomi irregolari,
  forestierismi e nomi dichiarati dall'autore.
- Sostituire il pronome con testo prima del parsing: perde l'identità già risolta
  e confonde frontend e runtime.
- Usare l'ultimo oggetto menzionato in qualsiasi output: `guarda` renderebbe
  imprevedibile il riferimento in stanze affollate.

## Conseguenze e verifica

`Session.pronoun_id` è stato di gioco ispezionabile; `Intent` trasporta l'ID
risolto già introdotto per i chiarimenti. CLI, Studio e release usano lo stesso
parser di sessione. I test coprono referente assente, forme unite, pronome
separato italiano e inglese, oggetto indiretto e scelta disambiguata.

