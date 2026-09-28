# Scene, tempo a turni e punteggio

Stato: implementato nell'IR 17.

## Dichiarare una scena temporale

Una scena ha un nome, un turno iniziale, un turno finale, due testi e un premio
facoltativo:

```locus
Scena "la tempesta" dal turno 1 al turno 3:
    Inizio "Il vento comincia a scuotere le finestre.".
    Fine "Le nuvole si aprono sopra la torre.".
    Punti 7.
Fine scena.
```

Il turno iniziale deve essere almeno 1 e il turno finale deve essere maggiore.
Sono ammessi fino a 64 scene e un milione di turni e punti per scena. `Inizio` e
`Fine` sono obbligatori; `Punti` è facoltativo e vale zero se omesso. Più scene
possono sovrapporsi.

Il compilatore assegna a ogni scena un ID stabile nell'IR. `E121` segnala nomi
duplicati o il superamento del limite; `E122` segnala intervalli, testi, punti o
voci del blocco non validi.

## Avanzamento del tempo

Il conteggio parte da zero. La descrizione iniziale mostrata all'avvio non
consuma un turno. Un comando riconosciuto fa avanzare il tempo dopo la propria
azione; in quel momento iniziano o terminano le scene previste per il nuovo
turno. Gli errori di sintassi del comando, le richieste ambigue, una scelta di
dialogo non valida e `esci` non avanzano il tempo.

`turno` e `tempo` mostrano il turno corrente senza modificarlo. Questi comandi
sono riservati soltanto nei progetti che dichiarano almeno una scena, così una
storia precedente può continuare a usare gli stessi termini per azioni proprie.

## Punteggio e registro

Quando una scena termina, il suo premio viene sommato una sola volta. `punteggio`
e `score` mostrano il totale senza consumare un turno. La sessione conserva un
registro immutabile con scena, punti e turno di assegnazione; il trace espone
inizio e fine della scena e l'eventuale variazione del punteggio.

Lo Studio elenca le scene nell'Indice del mondo e mostra gli eventi temporali in
**Regole e trace**. CLI, Studio, test e release web usano lo stesso stato.

## Limiti dell'incremento

Le scene IR 17 sono pianificate su turni assoluti. Non iniziano ancora in base a
condizioni del mondo, non eseguono effetti di regola e non si ripetono. Il
punteggio deriva soltanto dalla conclusione delle scene; premi espliciti nelle
regole e obiettivi con massimo dichiarato richiedono un'estensione successiva.
