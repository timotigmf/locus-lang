# Primo programma

Salvare in UTF-8 senza BOM un file `.locus`:

```ita
La Cucina è una stanza.
Il Corridoio è una stanza.
La chiave è una cosa.
```

`locus controlla file.locus` conferma tre entità. `locus ast file.locus` mostra
nomi e posizioni; `locus ir file.locus` mostra ID e tipi risolti. La chiave non è
ancora collocata nella Cucina: le posizioni arriveranno in M1. Lo skeleton non
permette di giocare. Un nome duplicato o un tipo sconosciuto produce un errore
con nome del file, riga, colonna e codice.
