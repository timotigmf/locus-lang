# Architecture Decision Records

- [0001 — parser](0001-parser.md): accettato per S0, revisione prima di regole/espressioni.
- [0002 — IR e separazione di dominio](0002-ir.md): accettato, formato sperimentale.
- [0003 — Python, CLI e packaging](0003-toolchain.md): accettato per bootstrap.

- [0004 — milestone 1](0004-milestone-1.md): relazioni generiche, sessioni e intenti.

- [0005 — proprietà e mondo M2](0005-proprieta-e-mondo.md): tipi di valore, accessibilità e invarianti.

Ogni ADR include contesto, alternative, conseguenze e criterio di revisione.
Le fonti e le licenze sono nel [registro](../architettura/fonti.md).

- [0006 — regole M3](0006-regole.md): fasi, transazioni, tracing e confronto parser.

- [0007 — progetti M4](0007-progetti.md): inclusioni locali e punto iniziale.

- [0008 — Studio web](0008-studio-web.md): stesso motore in WebAssembly e sito statico.

- [0009 — direzioni cardinali](0009-direzioni-cardinali.md): nord/sud ed est/ovest dal sorgente alla mappa.

- [0010 — metadati e vocabolario](0010-metadati-e-vocabolario.md): titolo e autore nel sorgente, sinonimi nominali dichiarativi.

- [0011 — gerarchia dei tipi](0011-gerarchia-tipi.md): tipi nominali dell'autore, ereditarietà singola e IR 7.

- [0012 — azioni dell'autore](0012-azioni-autore.md): catalogo tipato, comandi compilati e IR 8.

- [0013 — forme di comando](0013-forme-comando.md): sinonimi e separatori espliciti nell'IR 9.

- [0014 — comandi multiparola](0014-comandi-multiparola.md): locuzioni iniziali senza collisioni di prefisso nell'IR 10.

- [0015 — separatori multiparola](0015-separatori-multiparola.md): locuzioni fra due oggetti e articolazione finale nell'IR 11.
- [0016 — relazioni dinamiche](0016-relazioni-dinamiche.md): effetti transazionali sul grafo e mappa dello stato corrente nell'IR 12.
- [0017 — visibilità e scenario](0017-visibilita-scenario.md): campo d'azione esplicito e dettagli ambientali non trasportabili nell'IR 13.
- [0018 — elenchi tipati](0018-elenchi-tipati.md): collezioni omogenee e mutazioni transazionali nell'IR 14.
- [0019 — tabelle tipate](0019-tabelle-tipate.md): colonne nominate e righe transazionali nell'IR 15.
- [0020 — persone e dialoghi](0020-dialoghi-strutturati.md): grafi di conversazione e stato multi-turno nell'IR 16.
- [0021 — scene, tempo e punteggio](0021-scene-tempo-punteggio.md): clock logico, ciclo di vita e registro dei premi nell'IR 17.
- [0022 — veicoli](0022-veicoli.md): tipo standard, salita/discesa e movimento atomico del conducente nell'IR 18.
- [0023 — valuta e acquisti](0023-valuta-e-acquisti.md): saldo, prezzi, possesso e acquisto atomico nell'IR 19.
- [0024 — mercanti, scorte e vendita](0024-mercanti-scorte-e-vendita.md): venditori, cassa e rivendita atomica nell'IR 20.
- [0025 — manifest multimediale](0025-manifest-risorse-multimediali.md): immagini, suoni e release autosufficienti nell'IR 21.
- [0026 — direzioni diagonali](0026-direzioni-diagonali.md): rosa dei venti completa nella stdlib e nell'atlante.
- [0027 — livelli verticali](0027-livelli-verticali.md): su/giù, verbo `sovrasta` e linee di livello.
- [0028 — dentro/fuori](0028-dentro-fuori.md): navigazione topologica distinta dal contenimento.
- [0029 — disambiguazione a più turni](0029-disambiguazione-multiturno.md): chiarimento persistente e ripresa tipata dell'azione.
- [0030 — riferimenti pronominali](0030-riferimenti-pronominali.md): referente di sessione e clitici standard.
- [0031 — clitici con complemento](0031-clitici-con-complemento.md): oggetto diretto pronominale e secondo oggetto esplicito.
- [0032 — clitici doppi](0032-clitici-doppi.md): referenti diretto e indiretto separati per `metticelo`/`metticela`.
- [0033 — clitico locativo](0033-clitico-locativo.md): destinazione ricordata e oggetto esplicito in `mettici`.
- [0034 — avverbi locativi](0034-avverbi-locativi.md): `lì` e `là` come destinazioni contestuali di `metti`.
- [0035 — pronomi per ruolo](0035-pronomi-per-ruolo.md): referenti distinti per oggetto diretto e secondo argomento.
- [0036 — passaggi a senso unico](0036-passaggi-senso-unico.md): origine e destinazione esplicite senza arco inverso.
- [0037 — relazioni dinamiche unidirezionali](0037-relazioni-dinamiche-unidirezionali.md): creazione e rimozione transazionale di un solo arco.
- [0038 — comandi naturali di movimento](0038-comandi-naturali-movimento.md): verbi introduttivi e correzioni direzionali precise.
- [0039 — ritorno al luogo precedente](0039-ritorno-al-luogo-precedente.md): memoria di sessione e riuso del movimento direzionale.
