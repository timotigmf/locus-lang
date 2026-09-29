# Imparare LOCUS costruendo un faro

Un percorso originale in italiano, verificato con LOCUS 0.5.0a1. Ogni lezione
ha un file completo da eseguire, un esperimento e un risultato controllabile.
Non serve conoscere Inform. Le letture che hanno orientato il percorso sono
registrate in [Materiali e scelte](../architettura/materiali-didattici.md).

## Preparazione

Dalla cartella principale del repository, dopo l'installazione descritta nel
[README](../../README.md), usa `locus` oppure `.venv/bin/python -m locus` su macOS/Linux.
Su Windows puoi usare `.venv\Scripts\python -m locus`. Non digitare i comandi shell
al prompt della storia: lì si scrivono soltanto i comandi del giocatore.

| Lezione | File da giocare | Obiettivo |
| --- | --- | --- |
| [1. Luoghi e mappa](01-luoghi.md) | `examples/tutorial/01_mappa.locus` | Distinguere mondo, descrizione e comandi |
| [2. Oggetti e accesso](02-oggetti.md) | `examples/tutorial/02_custodia.locus` | Provare contenimento, visibilità e inventario |
| [3. Regole e descrizioni](03-regole.md) | `examples/tutorial/03_segnale.locus` | Mantenere coerenti stato e racconto |
| [4. Progetto e verifica](04-progetto.md) | `examples/tutorial/04_faro.locus` | Comporre un enigma completo su più file |
| [5. Comandi e nomi](05-comandi-e-nomi.md) | `examples/tutorial/02_custodia.locus` | Usare abbreviazioni, nomi parziali e ambiguità |
| [6. Sotterraneo, enigma e punti](06-sotterraneo-enigma-punti.md) | `examples/tutorial/06_sotterraneo.locus` | Comporre mappa, chiave, sinonimi e premio |
| [7. Tipi definiti dall'autore](07-tipi-autore.md) | `examples/tutorial/07_tipi.locus` | Creare categorie che ereditano capacità e proprietà |
| [8. Azioni definite dall'autore](08-azioni-autore.md) | `examples/tutorial/08_azioni.locus` | Dichiarare comandi con zero, uno o due oggetti tipati |
| [9. Sinonimi delle azioni](09-sinonimi-azioni.md) | `examples/tutorial/09_sinonimi_azioni.locus` | Accettare più forme e separatori italiani per la stessa azione |
| [10. Comandi multiparola](10-comandi-multiparola.md) | `examples/tutorial/10_comandi_multiparola.locus` | Dichiarare locuzioni iniziali deterministiche fino a quattro parole |
| [11. Separatori multiparola](11-separatori-multiparola.md) | `examples/tutorial/11_separatori_multiparola.locus` | Collegare due oggetti con locuzioni e preposizioni articolate |
| [12. Passaggi segreti](12-passaggi-segreti.md) | `examples/tutorial/12_passaggio_segreto.locus` | Creare e rimuovere uscite con rollback e mappa dinamica |
| [13. Scenario e oggetti nascosti](13-visibilita-scenario.md) | `examples/tutorial/13_scenario_nascosto.locus` | Separare esistenza, visibilità e trasportabilità |
| [14. Un taccuino di indizi](14-elenchi-indizi.md) | `examples/tutorial/14_taccuino_indizi.locus` | Raccogliere, verificare e rimuovere elementi tipati |
| [15. Il registro dei reperti](15-tabelle-reperti.md) | `examples/tutorial/15_tabelle_reperti.locus` | Definire schemi e trasferire righe in una transazione |
| [16. La guardiana del faro](16-dialogo-guardiana.md) | `examples/tutorial/16_dialogo_guardiana.locus` | Costruire una conversazione a nodi, scelte e cicli |
| [17. Tre rintocchi nella tempesta](17-tempesta-e-punteggio.md) | `examples/tutorial/17_tempesta_e_punteggio.locus` | Pianificare scene a turni e registrare un premio |
| [18. Attraversare la città in bicicletta](18-bicicletta-in-movimento.md) | `examples/tutorial/18_bicicletta_in_movimento.locus` | Dichiarare un veicolo e spostarlo con il conducente |
| [19. Comprare provviste al mercato](19-il-mercato-del-faro.md) | `examples/tutorial/19_mercato_del_faro.locus` | Usare valuta, prezzi e acquisti atomici |
| [20. La bottegaia, la scorta e la rivendita](20-la-bottegaia-del-faro.md) | `examples/tutorial/20_bottegaia_e_rivendita.locus` | Modellare mercanti, incassi, scorte e vendita |
| [21. Il faro multimediale](21-il-faro-multimediale.md) | `examples/tutorial/21_faro_multimediale.locus` | Integrare immagini, suoni e release autosufficienti |
| [22. Leggere l'Indice del mondo](22-leggere-indice-del-mondo.md) | `examples/tutorial/22_indice_completo.locus` | Ispezionare, filtrare ed esportare l'intera IR |
| [23. La rosa dei venti](23-la-rosa-dei-venti.md) | `examples/tutorial/23_direzioni_diagonali.locus` | Dichiarare, percorrere e mappare le quattro diagonali |
| [24. I tre livelli del faro](24-i-tre-livelli-del-faro.md) | `examples/tutorial/24_livelli_verticali.locus` | Dichiarare scale e botole con su, giù e `sovrasta` |
| [25. Entrare e uscire dalla lanterna](25-entrare-e-uscire.md) | `examples/tutorial/25_dentro_fuori.locus` | Distinguere passaggi dentro/fuori e contenimento degli oggetti |

Prima prova la versione fornita. Poi modifica un solo elemento e riesegui la
sequenza di comandi. In caso di errore conserva il messaggio, il file sorgente e
la sequenza minima che lo produce. Il [ricettario](../cookbook/README.md) e la
[scheda per chi conosce Inform](da-inform-a-locus.md) aiutano a orientarsi.

Ogni lezione combina un esempio eseguibile, una prova guidata, almeno un caso
negativo e un esercizio. La quinta lezione mostra come trasformare un
transcript esplorativo in un test ripetibile direttamente nello Studio.

Gli esempi non sono traduzioni dei giochi presenti nei manuali e non usano codice
o estensioni Inform. Persone e dialoghi sono strutture LOCUS compilate; la luce
fisica e i sinonimi non documentati non sono simulati. La lanterna è modellata
esplicitamente come un contenitore con schermatura: aprirla e chiuderla cambia il
testo, non un motore della luce.
