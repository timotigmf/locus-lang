# 34. Rivelare una botola senza ritorno

Apri `examples/tutorial/34_passaggio_unidirezionale_segreto.locus` nello Studio
e premi **Compila e prova**. La Cripta esiste già, ma la mappa non mostra ancora
un collegamento.

```locus
La Sala è una stanza.
La Cripta è una stanza.
La leva è una cosa nella Sala.

Regola "apri la botola" per esaminare "leva" nella fase dopo:
    crea relazione a senso unico "giù" da "Sala" a "Cripta";
    dì "La lastra ruota e scopre una discesa senza appigli.";
Fine regola.
```

## Prova guidata

1. Scrivi `giù`: la botola non è ancora aperta.
2. Scrivi `x leva`: la regola crea soltanto l'arco verso il basso.
3. Apri **Mappa**: compare una freccia `giù (solo andata)`.
4. Torna alla storia e scrivi `d`: raggiungi la Cripta.
5. Scrivi `u`: non esiste un passaggio per risalire.

`crea relazione` continua a creare anche l'inversa. Le parole `a senso unico`
chiedono invece un solo arco strutturato. `rimuovi relazione a senso unico`
rimuove quello stesso arco senza toccare un eventuale collegamento opposto.

## Caso negativo

Questo effetto produce `E312`, perché `sottovento` non è una relazione dinamica
registrata:

```text
crea relazione a senso unico "sottovento" da "Sala" a "Cripta";
```

## Esercizio

Aggiungi un'azione `riarma botola` che rimuove la relazione unidirezionale.
Verifica che ripetere la rimozione sia innocuo e che la mappa torni a mostrare
due luoghi separati.

Il [riferimento sulle relazioni dinamiche](../linguaggio/relazioni-dinamiche.md)
descrive controlli statici, rollback e differenza fra effetti bidirezionali e a
senso unico.
