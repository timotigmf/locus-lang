# Primo programma

Salvare in UTF-8 senza BOM un file `.ita`:

```ita
La Cucina è una stanza.
Il Corridoio è una stanza.
La chiave è una cosa.
```

`italica controlla file.ita` conferma tre entità. `italica ast file.ita` mostra
nomi e posizioni; `italica ir file.ita` mostra ID e tipi risolti. La chiave non è
ancora collocata nella Cucina: le posizioni arriveranno in M1. Lo skeleton non
permette di giocare. Un nome duplicato o un tipo sconosciuto produce un errore
con nome del file, riga, colonna e codice.
