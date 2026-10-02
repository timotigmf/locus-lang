# Aiuto contestuale durante la partita

Stato: implementato nella stdlib di LOCUS 0.5.0a1, senza modifica dell'IR 21.

In CLI, nello Studio e nelle release web puoi scrivere una di queste forme:

```text
aiuto
comandi
help
?
```

LOCUS mostra i comandi principali divisi per attività. L'elenco si adatta al
mondo compilato: dialoghi, scene, veicoli e commercio compaiono soltanto quando
la storia li contiene. Le forme iniziali delle azioni definite dall'autore
sono raccolte dalla IR, ordinate e mostrate nella sezione «azioni della storia».

L'aiuto è un metacomando: non consuma un turno, non attiva regole e non cambia
il mondo. Durante una conversazione o una domanda di chiarimento resta
disponibile e conserva il dialogo o le alternative ancora da scegliere.

## Errori precisi

Il primo pacchetto non introduce argomenti tematici. `aiuto movimento` è quindi
un comando sconosciuto, mentre `aiuto` mostra già il riepilogo completo. Quando
un altro comando non è riconosciuto, la correzione indica esplicitamente di
scrivere `aiuto`.

## Limiti

Il catalogo elenca le forme di comando, non spiega le regole specifiche di ogni
storia. L'autore deve descrivere enigmi e convenzioni narrative nel testo della
propria opera. Il manuale incorporato nello Studio resta la fonte approfondita
per sintassi, esempi copiabili e diagnostica.
