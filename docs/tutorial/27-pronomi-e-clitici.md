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
`metti lanterna in essa`. Il pronome nel secondo argomento indica la scatola,
mentre l'oggetto diretto resta la lanterna scritta nel comando.

Nel pannello **Test**, registra la prova guidata. Cambia `essa` in `it`: la forma
classica inglese usa lo stesso referente e il transcript finale non cambia.

