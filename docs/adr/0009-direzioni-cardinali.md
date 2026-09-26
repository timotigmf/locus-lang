# ADR 0009 — quattro direzioni cardinali nella libreria narrativa

Stato: accettato, 2026-09-27.

## Contesto

Il parser del giocatore riconosceva soltanto nord e sud. Di conseguenza `e` e
`o` producevano «Comando non riconosciuto» invece dell'esito corretto «nessun
passaggio», e il linguaggio dell'autore non poteva dichiarare stanze a est o a
ovest. Limitarsi ad aggiungere due alias al parser avrebbe creato comandi validi
senza una relazione corrispondente nel modello del mondo.

## Decisione

La stdlib registra quattro relazioni cardinali: nord/sud ed est/ovest. Ogni coppia
è inversa e il compilatore continua a trattarla mediante `RelationSpec`, senza
conoscere le direzioni. La frase `La Serra è a est della Sala.` produce un arco
est dalla Sala alla Serra e l'arco ovest inverso.

Il parser del giocatore accetta le forme italiane e le abbreviazioni `n`, `s`,
`e`, `o`. Per compatibilità con le convenzioni delle avventure testuali accetta
anche `north`, `south`, `east`, `west` e `w`. Un comando riconosciuto senza arco
nella stanza corrente restituisce l'evento strutturato `no_exit`; non diventa un
comando sconosciuto e non modifica la sessione.

Azioni e regole aggiungono `andare a est` e `andare a ovest`. Le porte possono
proteggere un passaggio su entrambe le coppie cardinali. Lo Studio esporta un solo
arco per coppia inversa e dispone est/ovest orizzontalmente, nord/sud verticalmente.
L'IR conserva lo stesso schema e la stessa versione: cambiano soltanto gli ID di
relazione forniti dalla stdlib.

## Alternative considerate

- Riconoscere `e` e `o` ma rispondere sempre `no_exit`: rifiutato perché il parser
  prometterebbe direzioni impossibili da dichiarare.
- Conservare soltanto nord/sud e documentare il limite: rifiutato perché produce
  un errore lessicale fuorviante per comandi standard.
- Introdurre subito diagonali, alto, basso, dentro e fuori: rinviato; richiede
  lessico, layout della mappa e casi di conflitto ulteriori.
- Inserire le direzioni nel compilatore generale: rifiutato; restano vocabolario
  sostituibile della libreria narrativa.

## Conseguenze e revisione

Le storie esistenti mantengono lo stesso comportamento. Cataloghi esterni possono
continuare a sostituire le relazioni standard. L'atlante conserva l'orientamento
cardinale nei grafi semplici; in presenza di collisioni sposta una stanza sulla
linea parallela più vicina e può produrre collegamenti incrociati.

Rivedere la decisione prima di aggiungere diagonali o assi verticali, perché gli
alias (`ne`, `su`, `giù`), le porte e l'algoritmo di impaginazione devono essere
specificati insieme.
