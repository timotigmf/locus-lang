# ADR 0038 — comandi naturali di movimento

Stato: accettato, 2026-10-01.

## Contesto

Le dodici direzioni hanno forme brevi e abbreviazioni, ma frasi comuni come
`vai a nord` ricadono nel comando sconosciuto. Il runtime usa già intenti
direzionali tipati e non deve ricevere testo da reinterpretare.

## Decisione

Il parser del giocatore riconosce un insieme chiuso di verbi introduttivi,
preposizioni facoltative e nomi direzionali esistenti. Produce lo stesso intento
di `nord`, `su` o `fuori`. Verbo senza complemento e complemento non direzionale
producono due eventi specifici, entrambi privi di avanzamento del turno.

I verbi introduttivi entrano nell'insieme dei comandi standard riservati, così
le azioni dell'autore non possono creare una grammatica in conflitto. L'IR e il
runtime direzionale restano invariati.

## Alternative considerate

- Trattare tutto ciò che segue `vai` come una stanza: richiederebbe ricerca di
  percorsi e una politica per porte, passaggi segreti e archi a senso unico.
- Riscrivere la frase nella forma breve: introdurrebbe una trasformazione
  testuale fuori dal parser e perderebbe la diagnosi precisa.
- Accettare qualunque verbo mediante un dizionario generale: renderebbe il
  comportamento dipendente da una risorsa lessicale non versionata.

## Conseguenze e verifica

Le forme brevi restano compatibili. I test coprono italiano, forme classiche
inglesi, preposizioni articolate, errori senza consumo di turno, Studio, browser
e tutorial. Nuovi verbi richiedono una modifica esplicita del catalogo.
