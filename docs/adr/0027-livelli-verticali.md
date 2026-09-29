# ADR 0027 — livelli verticali e verbo relazionale naturale

Stato: accettato, 2026-09-29.

## Contesto

Scale, botole, torri e sotterranei richiedono movimento verticale. La grammatica
cardinale `La B è a nord della A` produrrebbe forme italiane innaturali come
`è a sopra`. Inoltre l'atlante bidimensionale deve distinguere un livello da un
collegamento verso nord.

## Decisione

La stdlib registra la coppia mutabile `sopra`/`sotto` e associa il verbo
relazionale `sovrasta` al primo schema. La sintassi già prevista per i verbi di
relazione permette `La Soffitta sovrasta la Sala.`; il lowering inverte gli
operandi e produce un arco `sopra` dalla Sala alla Soffitta con l'inversa
`sotto`. Il compilatore resta indipendente dal dominio.

Il parser del giocatore produce gli intenti `up` e `down`. La stdlib accetta le
forme italiane, quelle senza accento e le abbreviazioni classiche. Runtime,
porte, veicoli e mutazioni delle regole usano gli stessi archi strutturati delle
altre direzioni.

Lo Studio esporta il solo arco `sopra` come direzione `su`; l'atlante lo disegna
tratteggiato e lo etichetta `su / giù`. La forma dell'IR 21 non cambia.

## Alternative considerate

- Usare `è a sopra della`: scartato perché non è italiano naturale.
- Interpretare `sali` e `scendi` come direzioni: scartato perché sono già azioni
  legate ai veicoli e possono richiedere un oggetto.
- Modellare quote numeriche: rinviato perché distanza e geometria richiedono
  nuovi valori, vincoli e algoritmi di mappa.
- Riutilizzare `mondo.dentro`: scartato perché contenimento e navigazione hanno
  cardinalità e invarianti differenti.

## Conseguenze

Le storie precedenti e l'IR restano compatibili. L'autore descrive una coppia
verticale con la stanza superiore come soggetto di `sovrasta`; l'inversa basta
per dichiarare una stanza inferiore. Dentro/fuori è specificato separatamente
nell'[ADR 0028](0028-dentro-fuori.md); quote e percorsi a senso unico restano
contratti distinti.
