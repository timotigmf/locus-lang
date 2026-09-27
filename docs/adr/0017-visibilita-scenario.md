# ADR 0017 — visibilità esplicita e scenario

Stato: accettato, 27 settembre 2026.

## Contesto

Un testo può omettere un oggetto senza impedirne la risoluzione da parte del
parser. Enigmi, vani segreti e dettagli ambientali richiedono una distinzione
strutturale fra entità esistente, percepibile, raggiungibile e trasportabile.

## Decisione

La stdlib introduce la proprietà logica `visibile`, predefinita a vero, e il
tipo radice `scenario`. `reachable` rifiuta entità invisibili e propaga
l'invisibilità lungo il contenimento. `scenario` partecipa alla relazione
`nella`, alle descrizioni e alle regole, ma non appartiene ai tipi trasportabili.

Il cambiamento di visibilità usa l'effetto generico e transazionale `imposta`;
non viene aggiunto un comando speciale al core. L'inventario e la risoluzione
dei nomi consultano lo stesso snapshot del mondo. L'IR sale alla versione 13.

## Alternative considerate

- Omettere soltanto il nome dalla descrizione: scartato perché i comandi
  continuerebbero a trovare l'oggetto.
- Spostare gli oggetti fuori scena modificando `nella`: utile per altri casi,
  ma più complesso per un oggetto che deve conservare la collocazione narrativa.
- Rendere scenario un sottotipo di cosa: scartato perché erediterebbe la
  trasportabilità, che è proprio la capacità da escludere.

## Conseguenze

I cataloghi standard contengono un tipo e una proprietà in più. I cataloghi del
core restano iniettati e indipendenti dalla narrativa. Trasparenza, illuminazione
e punti di vista multipli restano estensioni future.
