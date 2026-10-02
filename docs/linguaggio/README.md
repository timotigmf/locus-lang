# Linguaggio

La [specifica normativa M1](../../LANGUAGE_SPEC.md) distingue funzioni eseguibili
da funzionalità future. Il suffisso alpha non autorizza ambiguità silenziose:
un cambiamento di semantica deve aggiornare specifica e test. Articoli, pronomi
singolari e clitici standard hanno contratti separati; accordo grammaticale,
plurali e forme composte richiederanno decisioni ulteriori.

La versione attuale è descritta nelle specifiche [M2](milestone-2.md),
[M3](milestone-3.md), [M4](milestone-4.md) e in
[Metadati e vocabolario](metadati-vocabolario.md). I
[tipi definiti dall'autore](tipi-autore.md) aggiungono una gerarchia nominale a
ereditarietà singola, usata in modo uniforme dal compilatore e dal runtime.
Le [azioni definite dall'autore](azioni-autore.md) collegano comandi italiani,
argomenti tipati e regole senza interpretazione testuale nel runtime.
La [grammatica dei comandi dell'autore](grammatica-comandi-autore.md) aggiunge
sinonimi espliciti, separatori alternativi e preposizioni articolate nell'IR 9.
Le [forme multiparola](comandi-multiparola.md) aggiungono locuzioni iniziali
deterministiche e diagnostica delle collisioni di prefisso nell'IR 10.
I [separatori multiparola](separatori-multiparola.md) aggiungono locuzioni fisse
fra due oggetti e articolazione dell'ultima preposizione nell'IR 11.
Le [relazioni dinamiche](relazioni-dinamiche.md) permettono alle regole di creare
o rimuovere passaggi transazionali, anche a senso unico, nell'IR 12.
Le [direzioni diagonali](direzioni-diagonali.md) completano la rosa dei venti
nella stdlib, nel runtime e nell'atlante senza cambiare la forma dell'IR 21.
I [livelli verticali](livelli-verticali.md) aggiungono `su`/`giù`, il verbo
relazionale `sovrasta` e una resa distinta nell'atlante.
[Dentro e fuori](dentro-fuori.md) aggiunge passaggi topologici con `racchiude`
senza riutilizzare il contenimento degli oggetti.
I [comandi naturali di movimento](comandi-movimento.md) accettano verbi come
`vai`, `cammina` e `muoviti` davanti alle dodici direzioni strutturate.
[Tornare al luogo precedente](ritorno-indietro.md) aggiunge `indietro`, `torna`
e `back` senza aggirare il grafo corrente.
[Attendere](attendere.md) aggiunge l'azione standard senza oggetti, gli alias
`aspetta`, `z` e `wait` e l'integrazione con regole e scene.
[Guardare ed esaminare](guardare-esaminare.md) distingue `guarda` senza oggetto
da `guarda NOME` e raccoglie alias italiani nell'unico intento `examine`.
L'[aiuto in partita](aiuto-in-partita.md) elenca comandi standard e azioni
dell'autore in base alle capacità del mondo corrente senza consumare un turno.
I [passaggi a senso unico](passaggi-senso-unico.md) dichiarano esplicitamente
origine, direzione e destinazione senza generare l'arco inverso.
La [disambiguazione a più turni](disambiguazione-multiturno.md) conserva la
domanda nella sessione e riprende l'azione dopo una scelta univoca.
[Pronomi e clitici](pronomi-e-clitici.md) aggiunge un referente di sessione e
forme unite italiane per le azioni standard più comuni.
I [clitici con complemento](clitici-con-complemento.md) combinano il referente
diretto con un contenitore o una chiave scritti nel comando.
I [clitici doppi](clitici-doppi.md) aggiungono un referente separato per la
destinazione delle forme `metticelo` e `metticela`.
Il [clitico locativo](clitico-locativo.md) riusa la stessa destinazione con un
oggetto diretto ancora esplicito in `mettici OGGETTO`.
Gli [avverbi locativi](avverbi-locativi.md) esprimono lo stesso ruolo in
`metti OGGETTO lì` e `metti OGGETTO là`.
I [pronomi per ruolo](pronomi-per-ruolo.md) permettono al secondo argomento di
riusare un referente diverso dal primo, come in `aprilo con essa`.
La [visibilità esplicita](visibilita-scenario.md) aggiunge oggetti nascosti e il
tipo ambientale non trasportabile `scenario` nell'IR 13.
Gli [elenchi tipati](liste-tipate.md) aggiungono collezioni omogenee, condizioni
di appartenenza ed effetti transazionali nell'IR 14.
Le [tabelle tipate](tabelle-tipate.md) aggiungono colonne nominate, righe
eterogenee e mutazioni atomiche nell'IR 15.
I [dialoghi strutturati](dialoghi-strutturati.md) aggiungono persone, nodi,
scelte e conversazioni multi-turno nell'IR 16.
Le [scene temporali](scene-tempo-punteggio.md) aggiungono turni, ciclo di vita,
punteggio e registro dei premi nell'IR 17.
I [veicoli](veicoli.md) aggiungono un tipo standard, salita, discesa e movimento
congiunto del conducente nell'IR 18.
Il [denaro e gli acquisti](denaro-e-acquisti.md) aggiungono valuta tipata, saldo,
merci, prezzi e pagamento atomico nell'IR 19.
I [mercanti e la vendita](mercanti-e-vendita.md) aggiungono scorte, cassa e
rivendita atomica nell'IR 20.
Le [risorse multimediali](risorse-multimediali.md) aggiungono immagini e suoni
locali mediante un manifest validato nell'IR 21.
