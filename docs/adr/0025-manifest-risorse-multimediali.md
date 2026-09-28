# ADR 0025 — manifest delle risorse multimediali

Stato: accettato, 2026-09-28.

## Contesto

Una storia deve poter associare immagini e suoni a luoghi e oggetti. Un semplice
percorso interpretato soltanto dal browser renderebbe CLI, Studio e release
divergenti; URL remoti renderebbero inoltre il risultato dipendente dalla rete.

## Decisione

La stdlib espone le proprietà testuali `immagine`, `suono` e `testo alternativo`.
L'adattatore autore le abbassa in record `ResourceIR` risolti, uno per coppia
entità/tipo. Il core conserva e convalida il manifest senza conoscere quando una
storia debba presentarlo. Lo Studio restituisce le risorse pertinenti dopo
`guarda` ed `esamina`; i frontend decidono la resa.

I percorsi sono POSIX relativi al progetto. Sono vietati URL, percorsi assoluti,
segmenti `.`/`..`, drive Windows e backslash. IR 21 ammette PNG, JPEG, WebP, GIF,
MP3, Ogg e WAV e ne controlla la firma interna. Ogni file può occupare al massimo 5 MB; lo Studio ammette fino a
64 risorse e 20 MB complessivi. `compile_story_file` controlla presenza, confine
e dimensione; `compile_story` in memoria controlla soltanto percorso e formato.

Il progetto web salva i byte in Base64 per produrre un backup JSON completo. La
release copia anche i file ai rispettivi percorsi e resta autosufficiente. Il
suono appare con controlli espliciti: non viene avviato automaticamente.

## Alternative considerate

- URL remoti: scartati perché introducono rete, tracciamento e contenuti mutevoli.
- Path usati direttamente dal solo frontend: scartati perché privi di semantica
  IR e di diagnostica condivisa.
- Byte incorporati nell'IR: scartati perché gonfiano il contratto del motore e
  confondono identità della risorsa e trasporto del progetto.
- Riproduzione automatica: rinviata perché i browser la bloccano spesso e perché
  l'autore deve poter controllare accessibilità e ripetizione.

## Conseguenze

Il manifest è ispezionabile e portabile; una risorsa mancante produce `E126` sul
sorgente che la nomina. Backup e release possono crescere fino ai limiti
dichiarati. Video, didascalie temporizzate, precaricamento e mutazioni delle
risorse durante il gioco richiedono contratti successivi.
