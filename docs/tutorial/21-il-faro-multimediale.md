# 21. Il faro multimediale

File completo: `examples/tutorial/21_faro_multimediale.locus`.

## Obiettivo

Associare a un luogo un'immagine accessibile e un paesaggio sonoro, quindi
esportare una release che funzioni senza servizi esterni.

## Codice copiabile

```locus
Titolo: "Il faro illustrato".
Autore: "Il tuo nome".

Il Molo è una stanza.
Inizia nella "Molo".
Il Molo ha descrizione "La risacca batte contro le tavole del pontile.".
Il Molo ha immagine "media/molo.png".
Il Molo ha suono "media/risacca.wav".
Il Molo ha testo alternativo "Un faro chiaro oltre il molo, sotto il cielo notturno.".

La campana è una cosa nel Molo.
La campana ha descrizione "Il bronzo porta i segni della salsedine.".
```

Nello Studio premi **＋** accanto a **Risorse** e aggiungi `molo.png` e
`risacca.wav`. I file appariranno come `media/molo.png` e
`media/risacca.wav`. L'esempio nel repository contiene già due piccole risorse
originali generate per questa lezione.

## Prova guidata

1. Compila e prova: sopra il transcript compare l'immagine del Molo e un
   controllo per ascoltare la risacca.
2. Scrivi `x campana`: le risorse del luogo scompaiono perché la campana non ne
   dichiara di proprie.
3. Scrivi `guarda`: tornano le risorse del Molo.
4. Apri **Indice del mondo** e trova **Risorse multimediali**.
5. Esporta la release, estrai lo ZIP e servilo via HTTP. La cartella `media`
   contiene entrambi i file.

## Caso negativo

Prova a cambiare il percorso in `"../molo.png"`. La compilazione si ferma con
`E126`: una storia non può leggere file fuori dal progetto. Anche
`immagine "media/risacca.wav"` fallisce, perché un'immagine deve usare un
formato immagine.

## Esercizio

Associa un'immagine alla campana e descrivila con un testo alternativo che
comunichi forma e dettagli utili, senza iniziare con “immagine di”. Verifica con
`x campana`, poi scarica e riapri il backup del progetto.
