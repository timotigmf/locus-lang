# 27. Parlare di un oggetto già noto

Apri `examples/tutorial/27_pronomi_e_clitici.locus` nello Studio e premi
**Compila e prova**.

## Prova guidata

```text
> esamina lanterna
lanterna di vetro
Il vetro conserva tracce di salsedine.
> prendila
Hai preso: lanterna di vetro.
> x essa
lanterna di vetro
Il vetro conserva tracce di salsedine.
> lasciala
Hai lasciato: lanterna di vetro.
```

La prima azione identifica la lanterna. Le azioni successive conservano quel
referente, anche se scrivi `guarda` o `inventario` fra un comando e l'altro.

## Prova negativa

Riavvia la storia e digita subito `prendila`. LOCUS non indovina quale oggetto
intendi e segnala che manca un referente. Il comando non modifica il mondo e non
consuma un turno narrativo.

## Esercizio

Aggiungi una scatola aperta, prendi la lanterna, esamina la scatola e prova
`metti lanterna in essa`. Se non è ancora stato ricordato un secondo oggetto, il pronome indica la
scatola appena esaminata; l'oggetto diretto resta la lanterna scritta nel comando.
Se esiste già un referente indiretto, questo ha precedenza: vedi il laboratorio
seguente e la lezione 32.

Nel pannello **Test**, registra la prova guidata. Cambia `essa` in `it`: la forma
classica inglese usa lo stesso referente e il transcript finale non cambia.


## Esercizio risolto: il primo deposito e quelli successivi

Apri `examples/tutorial/27b_lanterna_e_scatole.locus` oppure copia:

```locus
Titolo: "La lanterna e le scatole".
Autore: "Esempio LOCUS".

La Sala è una stanza.
Inizia nella Sala.
La lanterna di vetro è una cosa nella Sala.
La scatola rossa è un contenitore nella Sala.
La scatola rossa ha stato "aperto".
La scatola blu è un contenitore nella Sala.
La scatola blu ha stato "aperto".
```

1. `prendi lanterna`, `esamina scatola rossa`, `metti lanterna in essa`:
   non essendoci un secondo referente, essa usa la scatola appena esaminata.
2. `prendi lanterna`, `esamina scatola blu`, `metti lanterna in essa`:
   la lanterna torna nella **rossa**, perché il primo deposito l’ha
   memorizzata come destinazione e quel ruolo ha precedenza.
3. Per cambiare destinazione, usa `prendi lanterna`, poi
   `metti lanterna nella scatola blu`.

Puoi sostituire `essa` con `it`: la risoluzione dei due ruoli è identica.
`guarda`, `inventario` e `aiuto` non cambiano i referenti.

**Prova negativa.** Dopo `prendi lanterna`, in una partita nuova, scrivi
`metti lanterna in essa` senza esaminare una scatola. Il pronome indica
la lanterna, che non è un contenitore: il deposito fallisce e l’oggetto resta
nell’inventario. LOCUS non sceglie automaticamente una scatola dalla stanza.
