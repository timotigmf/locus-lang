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
