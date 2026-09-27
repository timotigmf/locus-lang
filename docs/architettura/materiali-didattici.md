# Materiali forniti e applicazione a LOCUS

Registro delle sei copie PDF fornite dall'utente. Consultazione mirata di indici
e sezioni pertinenti, non revisione integrale delle 1751 pagine. I numeri sotto
sono pagine PDF a partire da 1; per Writing with Inform parte 2 si aggiunge anche
la numerazione stampata, che prosegue dalla parte 1. Nessun PDF, estratto esteso,
immagine o codice dei manuali viene redistribuito nel repository.

## Fonti consultate

| File fornito | Identificazione | Pagine/sezioni consultate | Applicazione |
| --- | --- | --- | --- |
| `well-versed-informer.pdf` | Jeff Nyman, The Well-Versed Informer, v0.1, 14 gennaio 2010; 9 pagine | 1–3, 5–6: metodo e distinzione fra scrittura e programmazione | Lezioni progressive, un esperimento per volta, motivazione delle scelte |
| `well-versed-informer-inform7-foundations.pdf` | Jeff Nyman, Inform Foundations, v0.3, 12 febbraio 2010; 71 pagine | 1–3, 15, 18, 47, 49–50, 56: modello, proprietà, azioni e transcript | Separare verifiche, cambiamenti di stato e resoconti; test positivi e negativi |
| `well-versed-informer-descriptions-and-locales.pdf` | Jeff Nyman, Descriptions and Locale, v0.3, 12 febbraio 2010; 46 pagine | 1–4, 19, 25: descrizione del luogo e oggetti; pagina 19 anche verificata visivamente | Distinguere testo statico, visibilità e contenimento; descrizioni coerenti con lo stato |
| `Writing with Inform Pt 1.pdf` | Writing with Inform, parte 1; 624 pagine; versione della copia non accertata | 1–3, 21 (§2.4–2.5), 34–35 (§3.1), 219–220 (§7.1–7.2) | Sintassi controllata, organizzazione del sorgente e differenza fra comando e azione |
| `Writing with Inform Pt 2.pdf` | Writing with Inform, parte 2; 680 pagine; versione della copia non accertata | 1–3 (§15.1–15.3); 365–366 (§19.1–19.2, stampate 989–990); 580–581 (§24.1–24.2, stampate 1204–1205); 631–632 (§26.10–27.1, stampate 1255–1256) | Regole ordinate, test ripetibili, composizione; differenze esplicite da LOCUS |
| `Inform_Handbook_3.pdf` | **Inform Handbook, by Jim Aikin**, v3.0, aprile 2023, dichiarato valido per Inform 10.1.2; 321 pagine | 1–3, 32, 37–38: evitare eccesso di dettaglio, test incrementali e prove esterne | Enigma piccolo ma completo, copione riproducibile, invito al playtest libero |

I materiali di Nyman sono del 2010; non li usiamo per affermare quale sia il
comportamento dell'ultima versione di Inform. La scheda di confronto riguarda
le sezioni effettivamente consultate. La copia dell'Handbook riporta a pagina 2
condizioni di attribuzione, uso non commerciale e condivisione analoga: i nuovi
esercizi sono originali e non incorporano esempi, traduzioni o illustrazioni del
volume. Nessun autore dei manuali approva o sponsorizza LOCUS.

## Miglioramenti consegnati

Il [percorso del faro](../tutorial/README.md) insegna mappa, inventario, contenitori,
regole, descrizioni reversibili e progetti su più file. Ogni lezione ha un esempio
eseguibile, un risultato atteso e un esercizio con soluzione. Il copione finale
controlla anche rifiuti e tentativi ripetuti. `tests/test_tutorials.py` verifica
l'uscita esatta della CLI e, separatamente, stato logico, inventario e posizione.

M4 aggiunge composizione dei file e ingresso esplicito. La lettura rafforza la
scelta di fornire esempi verificati e diagnostica con origine sorgente; non modifica
retroattivamente la semantica M3 per imitare quella di Inform.

## Priorità emerse, ancora da implementare

| Evoluzione | Motivo | Criterio di accettazione proposto |
| --- | --- | --- |
| Riferimenti parametrici agli oggetti delle azioni | Evitare una regola identica per ogni oggetto | Una regola applicata a due oggetti, secondo oggetto tipato, errori per argomenti assenti |
| Oggetti di scenario e distinzione visibile/raggiungibile | Descrizioni ricche senza rendere trasportabile ogni dettaglio | `scenario` esaminabile ma non prendibile e proprietà `visibile`, implementati nell'IR 13 |
| Test autore dichiarativi | Rendere riproducibili i racconti senza scrivere Python | Comandi, output e stato attesi; exit code non zero sul primo errore |
| Tipi autore ed enumerazioni | Modelli più precisi senza booleani contraddittori | Sottotipi validati, proprietà applicabili, valori enum controllati |
| Namespace e moduli versionati | Riutilizzo di biblioteche senza collisioni | Due moduli con nomi locali uguali e riferimenti qualificati non ambigui |

Questa tabella è progettazione futura, non un elenco di funzionalità disponibili.
L'elenco dettagliato delle differenze è in [Da Inform a LOCUS](../tutorial/da-inform-a-locus.md).
