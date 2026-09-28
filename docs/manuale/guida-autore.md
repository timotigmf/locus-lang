# Manuale dell'autore LOCUS

Questa è la porta d'ingresso al linguaggio e allo Studio. Gli esempi sono
eseguibili e hanno un pulsante **Copia codice**. Parti dal percorso breve, poi usa
l'indice tematico per costruire una storia più complessa.

## La prima storia in dieci minuti

Scegli **Progetto vuoto** e sostituisci il sorgente con questo:

```locus
Titolo: "La casa sul promontorio".
Autore: "Il tuo nome".

L'Atrio è una stanza.
Il Giardino è una stanza.
Il Giardino è a est dell'Atrio.
Inizia nella "Atrio".

L'Atrio ha descrizione "Una porta a vetri conduce al giardino.".
Il Giardino ha descrizione "Il vento piega l'erba alta.".
La lanterna è una cosa nell'Atrio.
Comprendi "lume" come "lanterna".
```

Premi **Compila e prova**. Scrivi `guarda`, `prendi lume`, `e`, `o`. Titolo e
autore vengono letti dal sorgente; la barra superiore non è un secondo posto in
cui riscriverli.

## Come si usa il manuale nello Studio

- **Manuale** apre questa pagina; il menu in alto cambia capitolo.
- **Cerca nei capitoli** filtra i capitoli che contengono le parole digitate.
- **Tutorial del faro** apre il corso progressivo con esercizi e risultati attesi.
- **? Comandi** porta direttamente ai comandi del giocatore.
- **Copia codice** copia un esempio completo; incollalo in `storia.locus`.
- Le diagnosi hanno **Apri nel manuale** e portano al riferimento pertinente.

`Includi` serve ai progetti avanzati divisi in più file. Il progetto iniziale e
l'esempio principale usano un solo `storia.locus`, così puoi leggere la storia
dall'alto verso il basso prima di studiare i moduli.

## Corso progressivo

1. [Luoghi, descrizioni e mappa](../tutorial/01-luoghi.md)
2. [Oggetti, contenitori e accessibilità](../tutorial/02-oggetti.md)
3. [Regole e descrizioni](../tutorial/03-regole.md)
4. [Progetto su più file e verifica](../tutorial/04-progetto.md)
5. [Comandi, abbreviazioni e nomi](../tutorial/05-comandi-e-nomi.md)
6. [Sotterraneo, enigma, sinonimi e punti](../tutorial/06-sotterraneo-enigma-punti.md)
7. [Tipi definiti dall'autore](../tutorial/07-tipi-autore.md)
8. [Azioni e comandi definiti dall'autore](../tutorial/08-azioni-autore.md)
9. [Sinonimi e separatori delle azioni](../tutorial/09-sinonimi-azioni.md)
10. [Comandi composti da più parole](../tutorial/10-comandi-multiparola.md)
11. [Separatori composti da più parole](../tutorial/11-separatori-multiparola.md)
12. [Passaggi segreti e mappa dinamica](../tutorial/12-passaggi-segreti.md)
13. [Scenario e oggetti nascosti](../tutorial/13-visibilita-scenario.md)
14. [Elenchi tipati e taccuino di indizi](../tutorial/14-elenchi-indizi.md)
15. [Tabelle tipate e registro dei reperti](../tutorial/15-tabelle-reperti.md)
16. [Persone e dialoghi a scelte](../tutorial/16-dialogo-guardiana.md)
17. [Scene, tempo e punteggio](../tutorial/17-tempesta-e-punteggio.md)
18. [Veicoli e movimento](../tutorial/18-bicicletta-in-movimento.md)
19. [Denaro e acquisti](../tutorial/19-il-mercato-del-faro.md)
20. [Mercanti, scorte e vendita](../tutorial/20-la-bottegaia-del-faro.md)
21. [Immagini, suoni e release](../tutorial/21-il-faro-multimediale.md)

## Indice per obiettivo

| Voglio creare… | Supporto attuale | Da leggere |
| --- | --- | --- |
| Dungeon e mappe | Stanze, quattro direzioni, porte e contenitori | Lezioni 1 e 6 |
| Enigmi con chiavi | Porte/contenitori bloccati, regole e rollback | Lezioni 2, 3 e 6 |
| Punti e tempo | Scene temporali, turni e registro dei premi | Lezioni 6 e 17 |
| Oggetti complessi | Contenimento annidato, proprietà tipate, stati | Lezione 2 e specifica M2 |
| Categorie proprie | Tipi nominali con ereditarietà singola | Lezione 7 |
| Verbi e comandi propri | Azioni tipate con sinonimi e locuzioni multiparola | Lezioni 8–11 |
| Sinonimi | Alias nominali e più forme per le azioni | Lezioni 5, 6 e 9 |
| Passaggi segreti dinamici | Uscite cardinali create o rimosse dalle regole | Lezione 12 |
| Dettagli ambientali e oggetti nascosti | `scenario` non trasportabile e proprietà `visibile` | Lezione 13 |
| Indizi, memoria e cronologie | Elenchi tipati con appartenenza e rollback | Lezione 14 |
| Cataloghi e registri | Tabelle con colonne tipate e righe transazionali | Lezione 15 |
| Dialoghi ramificati | Persone, nodi, scelte, cicli e memoria delle visite | Lezione 16 |
| Scene temporali | Inizio e fine a turni dichiarati con trace | Lezione 17 |
| Veicoli e vetture | Tipo standard, sottotipi, salita/discesa e movimento congiunto | Lezione 18 |
| Denaro e acquisti | Valuta, saldo, merci, prezzi e acquisto atomico | Lezione 19 |
| Mercanti e vendita | Persone venditrici, cassa, scorte e rivendita | Lezione 20 |
| Immagini e paesaggi sonori | Risorse locali validate e incluse nella release | Lezione 21 |

## Vocabolario italiano

LOCUS normalizza maiuscole, accenti e spazi, usa nomi parziali quando non sono
ambigui e permette sinonimi specifici per la storia:

```locus
L'Atrio è una stanza.
La custodia impermeabile è un contenitore nell'Atrio.
Comprendi "cassa" come "custodia impermeabile".
Comprendi "scatola" come "custodia impermeabile".
Comprendi "contenitore stagno" come "custodia impermeabile".
```

Un dizionario italiano completo non basta a comprendere “qualsiasi termine”:
`banco`, per esempio, può indicare un mobile, una scuola, sabbia o pesci. La
decisione appartiene all'autore e al contesto della storia. LOCUS evita scelte
silenziose: se due oggetti corrispondono, chiede quale intendi.

## Riferimenti

- [Prima storia e comandi](README.md)
- [Specifica incrementale](../../LANGUAGE_SPEC.md)
- [Proprietà, contenitori, porte e vocabolario](../linguaggio/milestone-2.md)
- [Regole, condizioni e transazioni](../linguaggio/milestone-3.md)
- [File, inclusioni e punto iniziale](../linguaggio/milestone-4.md)
- [Titolo, autore e sinonimi](../linguaggio/metadati-vocabolario.md)
- [Tipi definiti dall'autore](../linguaggio/tipi-autore.md)
- [Azioni definite dall'autore](../linguaggio/azioni-autore.md)
- [Sinonimi e separatori delle azioni](../linguaggio/grammatica-comandi-autore.md)
- [Forme di comando multiparola](../linguaggio/comandi-multiparola.md)
- [Separatori multiparola](../linguaggio/separatori-multiparola.md)
- [Elenchi tipati](../linguaggio/liste-tipate.md)
- [Tabelle tipate](../linguaggio/tabelle-tipate.md)
- [Persone e dialoghi strutturati](../linguaggio/dialoghi-strutturati.md)
- [Scene, tempo e punteggio](../linguaggio/scene-tempo-punteggio.md)
- [Veicoli e movimento](../linguaggio/veicoli.md)
- [Denaro e acquisti](../linguaggio/denaro-e-acquisti.md)
- [Mercanti e vendita](../linguaggio/mercanti-e-vendita.md)
- [Risorse multimediali](../linguaggio/risorse-multimediali.md)
- [Ricettario](../cookbook/README.md)
- [Da Inform a LOCUS](../tutorial/da-inform-a-locus.md)
