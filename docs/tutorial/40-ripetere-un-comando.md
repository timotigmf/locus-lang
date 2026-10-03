# 40. Ripetere un comando

Apri `examples/tutorial/40_ripetere_comando.locus` nello Studio e premi
**Compila e prova**. La storia contiene una campana, un'azione dell'autore e una
scena temporale.

```locus
La Torre è una stanza.
La campana è una cosa nella Torre.

Azione "suonare" su una cosa con comando "suona".
Regola "rintocco" per suonare "campana" nella fase invece:
    dì "La campana risponde con un rintocco profondo.";
Fine regola.
```

## Prova guidata

1. Appena avviata la storia, scrivi `g`: non esiste ancora un comando riuscito.
2. Scrivi `suona campana`, poi `ancora`: senti due rintocchi distinti.
3. Scrivi `attendi`, poi `ripeti`: trascorrono due turni e la scena avanza.
4. Prova anche `again` e `g` dopo `esamina campana`.

## Caso negativo

Dopo `esamina campana`, scrivi un comando inesistente come `vola`, poi `g`.
L'errore non cancella il ricordo: LOCUS esamina di nuovo la campana.

## Esercizio risolto: due campane

Per provocare un chiarimento, rinomina la prima campana `campana di bronzo`
e aggiungi `campana d'argento`. Non lasciare un oggetto chiamato soltanto
`campana`: il nome esatto ha precedenza sui nomi parziali e selezionerebbe
quell'oggetto senza domanda.

Apri `examples/tutorial/40b_due_campane.locus` oppure copia questo progetto:

```locus
Titolo: "Le due campane".
Autore: "Esempio LOCUS".

La Torre è una stanza.
Inizia nella "Torre".
La campana di bronzo è una cosa nella Torre.
La campana di bronzo ha descrizione "Il bronzo reca una rosa dei venti.".
La "campana d'argento" è una cosa nella Torre.
La "campana d'argento" ha descrizione "L'argento reca una luna crescente.".
Comprendi "lunare" come "campana d'argento".
```

Prova il copione `examples/tutorial/40b_due_campane.comandi`:

| Comando | Risultato atteso |
| --- | --- |
| `x campana` | Domanda con due alternative |
| `scegli 99` | Errore con le stesse alternative, senza scelta automatica |
| `scegli lunare` | Esame della campana d'argento tramite il sinonimo |
| `g` | Stesso esame, senza nuova domanda |
| `vola` | Comando sconosciuto |
| `g` | Ancora la campana d'argento: l'errore non cancella il ricordo |

In una nuova partita ripeti la prova scegliendo `1`: ora `g` deve mostrare
la rosa dei venti della campana di bronzo. Il ricordo segue l'oggetto scelto,
non il testo generico `campana` e non una preferenza fissa per il secondo.

**Variante:** aggiungi una terza campana con descrizione distinta. Verifica che
la domanda offra tre alternative e che la ripetizione conservi quella scelta.

Il [riferimento sulla ripetizione](../linguaggio/ripetere-comando.md) spiega
quali intenti vengono ricordati e come interagiscono con turni e regole.
