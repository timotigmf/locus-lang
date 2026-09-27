# Visibilità esplicita e oggetti di scenario

Stato: implementato nell'IR 13.

## Proprietà `visibile`

La libreria standard assegna a cose, contenitori, chiavi e scenari la
proprietà logica `visibile`, con valore predefinito `vero`. Un oggetto può
iniziare nascosto:

```locus
La Sala è una stanza.
La chiave è una cosa nella Sala.
La chiave ha visibile falso.
```

Un'entità con `visibile falso` non compare nella descrizione del luogo e il
parser del giocatore non può risolverne il nome. `esamina chiave` e `prendi
chiave` rispondono quindi che l'oggetto non si trova lì. L'entità rimane nel
mondo tipato: condizioni e regole dell'autore possono riferirsi a essa.

La visibilità segue il contenimento. Se un contenitore è invisibile, anche tutti
i suoi discendenti lo sono. Un contenitore chiuso continua a nascondere il suo
contenuto anche quando è visibile. Un oggetto posseduto ma invisibile non viene
elencato nell'inventario finché una regola non lo rivela.

## Rivelare e nascondere

Le regole usano il normale effetto tipato `imposta`:

```locus
La Sala è una stanza.
Il pannello è uno scenario nella Sala.
La chiave è una cosa nella Sala.
La chiave ha visibile falso.

Regola "apri il vano" per esaminare "pannello" nella fase dopo:
    imposta "visibile" di "chiave" a vero;
    dì "Dietro il pannello compare una chiave.";
Fine regola.
```

L'effetto appartiene alla transazione della regola. Se un'istruzione successiva
esegue `fallisci`, il valore di `visibile` torna a quello precedente e l'oggetto
non viene esposto parzialmente.

## Tipo `scenario`

`scenario` è un tipo standard collocabile in una stanza o in un contenitore.
Può avere descrizione, sinonimi e regole e può essere esaminato. Non è una cosa
trasportabile: `prendi mosaico` produce l'esito “non puoi prendere questo
elemento”. È possibile dichiararne sottotipi:

```locus
La Sala è una stanza.
Un affresco è un tipo di scenario.
Il cielo dipinto è un affresco nella Sala.
```

## Limiti

Questa estensione modella presenza percettibile esplicita. Luce e oscurità,
contenitori trasparenti, supporti, percezione per personaggio e priorità delle
descrizioni richiedono contratti separati. `visibile` non crea o elimina uscite:
per i passaggi usa le [relazioni dinamiche](relazioni-dinamiche.md).
