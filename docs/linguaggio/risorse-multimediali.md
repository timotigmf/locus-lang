# Risorse multimediali

Stato: implementato nell'IR 21.

## Associare un'immagine e un suono

Le risorse sono file locali del progetto:

```locus
La Terrazza è una stanza.
La Terrazza ha immagine "media/terrazza.jpg".
La Terrazza ha suono "media/vento.ogg".
La Terrazza ha testo alternativo "La terrazza del faro sotto un cielo scuro.".
```

`immagine`, `suono` e `testo alternativo` sono proprietà standard disponibili
per ogni entità. Il compilatore crea un manifest `ResourceIR` con entità, genere,
percorso, tipo MIME e testo alternativo. Se il testo manca, usa il nome
dell'entità. `guarda` presenta le risorse della stanza; `esamina NOME` presenta
quelle dell'oggetto esaminato.

## Aggiungere i file nello Studio

Scegli **＋** accanto a **Risorse** e seleziona uno o più file. Lo Studio li salva
con un percorso `media/NOMEFILE`; usa esattamente quel percorso nel sorgente.
**Scarica progetto** produce un JSON che contiene anche i byte, così il backup
può essere riaperto senza recuperare file separati.

Formati immagini: `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`. Formati audio:
`.mp3`, `.ogg`, `.wav`. Ogni file può occupare 5 MB; un progetto web ammette 64
risorse e 20 MB complessivi. I percorsi devono essere relativi, con `/`, senza
URL, drive, `.` o `..`. LOCUS controlla anche che la firma interna del file
corrisponda all'estensione dichiarata.

La release ZIP include runtime, progetto e risorse. L'immagine usa il testo
alternativo dichiarato; il suono offre i controlli del browser e non parte da
solo. Questo rende la storia più prevedibile e accessibile.

## Diagnostica

`E126` segnala formato incoerente, percorso non sicuro, file assente, file fuori
dal progetto o risorsa oltre 5 MB. Per esempio, questa assegnazione è rifiutata:

```text
La Terrazza ha immagine "../foto/terrazza.png".
```

Un'immagine non può usare un'estensione audio e viceversa. La compilazione da
testo in memoria non dispone di un filesystem e controlla percorso ed
estensione; la CLI e lo Studio controllano anche il file reale.

## Limiti di IR 21

Le risorse sono statiche e associate a un'entità. Non sono ancora disponibili
video, immagini condizionali, playlist, dissolvenze o avvio audio da una regola.
