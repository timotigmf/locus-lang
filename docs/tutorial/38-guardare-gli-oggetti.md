# 38. Guardare gli oggetti con parole naturali

Apri `examples/tutorial/38_guardare_oggetti.locus` nello Studio e premi
**Compila e prova**. L'esempio contiene una custodia e due medaglioni simili.

```locus
La Archivio è una stanza.
La custodia è un contenitore nell'Archivio.
La custodia ha descrizione "Cuoio scuro, cucito con filo rosso.".

Il "medaglione di bronzo" è una cosa nell'Archivio.
Il "medaglione d'argento" è una cosa nell'Archivio.
Comprendi "argento" come "medaglione d'argento".
```

## Prova guidata

1. Scrivi `guarda`: LOCUS descrive l'Archivio.
2. Scrivi `guarda custodia`: LOCUS esamina la custodia.
3. Prova `osserva la custodia`, `ispeziona custodia` e `look at the custodia`.
4. Scrivi `guarda medaglione`: LOCUS chiede quale dei due intendi.
5. Rispondi `argento`: viene esaminato il medaglione d'argento.

## Caso negativo

`osserva` senza nome produce una richiesta precisa dell'oggetto. `guarda` senza
nome non è incompleto: conserva il significato di descrivere il luogo.

## Esercizio

Aggiungi una regola `per esaminare "custodia" nella fase dopo` che stampi un
indizio. Verifica che si attivi sia con `x custodia` sia con `guarda custodia`:
il rulebook riceve la stessa azione strutturata.

Il [riferimento su guardare ed esaminare](../linguaggio/guardare-esaminare.md)
elenca alias, errori e rapporto con la disambiguazione.

## Richiamare l'oggetto appena osservato

Dopo `guarda custodia`, puoi digitare `guardala`, `osservala`, `ispezionala`
o `controllala`: tutte esaminano lo stesso oggetto. Sono disponibili anche
le forme maschili `guardalo`, `osservalo`, `ispezionalo` e `controllalo`.
Usano il referente dell'ultimo oggetto diretto, come `esaminalo`.

In una nuova partita, prima di identificare un oggetto, `guardala` segnala
che manca un referente. `guardala custodia` non è una forma valida: usa
il clitico da solo oppure `guarda custodia`. Non è ancora verificato
l'accordo grammaticale tra il clitico e il nome dell'oggetto.

## Esercizio risolto: un indizio nella cucitura

Apri `examples/tutorial/38b_cucitura_custodia.locus` oppure copia:

```locus
Titolo: "La cucitura della custodia".
Autore: "Esempio LOCUS".

La Archivio è una stanza.
Inizia nella Archivio.
La custodia è un contenitore nella Archivio.
La custodia ha descrizione "Cuoio scuro, cucito con filo rosso.".
La nota piegata è una cosa nella custodia.
La nota piegata ha descrizione "Il passaggio si trova dietro lo scaffale numero tre.".
La nota piegata ha visibile falso.
La scoperta è una proprietà logica.

Regola "cucitura già notata" per esaminare "custodia" nella fase dopo priorità 10
quando "scoperta" di "custodia" è vero:
    dì "Hai già individuato la tasca interna.";
Fine regola.

Regola "scoprire la tasca" per esaminare "custodia" nella fase dopo
quando "scoperta" di "custodia" è falso:
    imposta "visibile" di "nota piegata" a vero;
    imposta "scoperta" di "custodia" a vero;
    dì "La cucitura indica una tasca interna: apri la custodia per esplorarla.";
Fine regola.
```

1. Scrivi `x custodia`: compare l’indizio della tasca.
2. Scrivi `guarda custodia`: compare soltanto il promemoria della tasca già
   individuata, oltre alla descrizione ordinaria.
3. Prova `prendi nota`: la custodia è ancora chiusa, quindi la nota non è
   raggiungibile anche se la regola l’ha resa visibile.
4. `apri custodia` annuncia la nota piegata; `prendi nota` riesce.
5. `x nota` permette di leggere il suo testo.

Riparti e sostituisci il primo comando con `osserva custodia`,
`ispeziona custodia` o `look at custodia`: il risultato è lo stesso.
`guarda` senza oggetto descrive invece il luogo e non scopre la tasca.

**Perché la priorità 10?** Il promemoria deve essere valutato prima della
regola che imposta scoperta a vero. Al primo esame non viene eseguito;
invertendo l’ordine, entrambe le condizioni potrebbero diventare vere nello
stesso comando e produrre un messaggio prematuro.

**Limite dell’esempio.** Il passaggio indicato nella nota è soltanto testo:
questa storia non dichiara ancora un collegamento dietro lo scaffale.
Per costruirlo consulta la lezione sui passaggi segreti.
