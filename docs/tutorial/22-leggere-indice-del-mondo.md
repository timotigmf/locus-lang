# 22. Leggere l'Indice del mondo

Apri `examples/tutorial/22_indice_completo.locus` nello Studio e scegli
**Compila e prova**. Questa lezione mostra come controllare ciò che il
compilatore ha realmente costruito.

## Il piccolo archivio

L'esempio dichiara due stanze, un tipo `reperto`, un medaglione con sinonimo,
un'azione, una regola, una tabella e una scena. Sono strutture diverse, ma tutte
compaiono nell'IR e quindi nell'indice.

```locus
Un reperto è un tipo di cosa.
La Sala è una stanza.
Il Deposito è una stanza.
Il Deposito è a nord della Sala.
Il medaglione è un reperto nella Sala.
Comprendi "talismano" come "medaglione".

Azione "catalogare" su un reperto con comando "cataloga".
Regola "scheda del medaglione" per catalogare "medaglione" nella fase invece:
    dì "Registri il medaglione nel catalogo.";
Fine regola.
```

## Prova guidata

1. Apri **Indice del mondo** e trova `reperto` nella gerarchia dei tipi.
2. Cerca `talismano`: rimane la voce del vocabolario diretta a `medaglione`.
3. Cerca `scheda`: compare la regola con fase `invece`, azione `catalogare`,
   effetto `dì` e sorgente.
4. Cancella il filtro e controlla la relazione `Sala — nord — Deposito` e la
   sua inversa `Deposito — sud — Sala`.
5. Scarica il JSON e cerca le chiavi `types`, `relations`, `synonyms`, `rules`,
   `tables` e `scenes`.

Nel gioco esegui `cataloga medaglione`; il testo della regola conferma che
l'azione mostrata nell'indice è davvero eseguibile.

## Caso negativo

Cerca `unicorno inesistente`. Lo Studio mostra **Nessuna voce corrisponde alla
ricerca** e il progetto resta compilato. Cancella il filtro: tutte le righe
ricompaiono. Un filtro senza risultati non è un errore del sorgente.

## Esercizio

Aggiungi un sottotipo `moneta` di `reperto`, una moneta nella Sala e il sinonimo
`soldo`. Ricompila e usa prima `moneta`, poi `soldo` come filtri. Controlla che
la gerarchia e il vocabolario descrivano due aspetti distinti dello stesso
modello.

Il [riferimento dell'Indice](../studio/indice-del-mondo.md) elenca tutte le
sezioni, il formato esportato e i limiti.
