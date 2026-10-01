# ADR 0035 — risoluzione pronominale per ruolo

Stato: accettato, 2026-10-01.

## Contesto

Con un solo referente, `aprilo con essa` risolve entrambi i pronomi nello stesso
oggetto e non può riusare la chiave di una precedente azione riuscita. La
sessione dispone ora di un referente diretto e di uno indiretto, ma i pronomi
ordinari continuavano a ignorare il secondo.

## Decisione

Il parser di sessione risolve un pronome ordinario in base al ruolo dell'intento:

- l'oggetto diretto usa `pronoun_id`;
- il secondo oggetto usa `indirect_pronoun_id`, quando presente;
- in assenza di un referente indiretto, il secondo oggetto usa `pronoun_id` per
  conservare il comportamento delle sessioni precedenti.

La scelta avviene sugli ID e non riscrive il comando. Il marcatore locativo `ci`
continua invece a richiedere esplicitamente `indirect_pronoun_id` e produce la
diagnostica dedicata quando manca.

## Alternative considerate

- Usare sempre il referente diretto: impedisce frasi naturali con porta e chiave.
- Usare sempre il referente indiretto nel secondo ruolo: romperebbe `metti gemma
  in essa` dopo aver esaminato un contenitore in una sessione senza secondo
  referente.
- Scegliere in base al genere: le entità non dichiarano ancora genere
  grammaticale e l'inferenza dalla desinenza non è affidabile.

## Conseguenze e verifica

Una stessa forma pronominale può risolvere due ID diversi nella medesima frase,
ma la regola è deterministica e ispezionabile nello Studio. Test unitari,
runtime, CLI, Studio, tutorial e browser verificano la preferenza per ruolo e il
ripiego compatibile. L'IR resta alla versione 21.
