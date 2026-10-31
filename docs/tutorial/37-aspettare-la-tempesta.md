# 37. Aspettare la tempesta

Apri `examples/tutorial/37_aspettare.locus` nello Studio e premi **Compila e
prova**. L'esempio collega l'azione standard di attesa a una scena temporale.

```locus
La Torre è una stanza.

Scena "il temporale" dal turno 1 al turno 2:
    Inizio "Un tuono scuote i vetri.".
    Fine "La pioggia si allontana oltre i tetti.".
    Punti 2.
Fine scena.

Regola "gocce" per attendere nella fase dopo:
    dì "Conti le gocce sul davanzale.";
Fine regola.
```

## Prova guidata

1. Scrivi `turno`: l'orologio indica zero e non avanza.
2. Scrivi `attendi`: compare il testo standard, la regola e l'inizio della scena.
3. Scrivi `z`: termina la scena e assegna due punti.
4. Scrivi `punteggio`: il totale è due e il turno resta invariato.
5. Prova anche `aspetta` e `wait`: entrambe le forme eseguono la stessa azione.

## Caso negativo

Prova a dichiarare `Azione "sostare" senza oggetti con comando "attendi".`:
la compilazione produce `E311`, perché la forma appartiene alla libreria.

## Esercizio

Aggiungi una seconda regola `invece` per attendere e osserva come sostituisce il
messaggio «Il tempo passa.». Poi falla fallire con un testo: il rollback lascia
intatto lo stato, secondo il contratto generale delle regole.

Il [riferimento sull'attesa](../linguaggio/attendere.md) descrive alias, rulebook
e avanzamento delle scene.

## Esercizio risolto: attesa e rollback

Apri `examples/tutorial/37b_attesa_al_riparo.locus` oppure copia:

```locus
Titolo: "Aspettare al riparo".
Autore: "Esempio LOCUS".

La Torre è una stanza.
Inizia nella Torre.
La riparo pronto è una proprietà logica.
La attese è una proprietà numerica.

Azione "preparare" senza oggetti con comando "prepara".
Regola "preparare il riparo" per preparare nella fase invece:
    imposta "riparo pronto" di "Torre" a vero;
    dì "Ti sistemi sotto la tettoia.";
Fine regola.

Regola "attesa protetta" per attendere nella fase invece:
    aumenta "attese" di "Torre" di 1;
    dì "Ascolti la pioggia dal riparo.";
Fine regola.

Regola "controllare il riparo" per attendere nella fase dopo
quando "riparo pronto" di "Torre" è falso:
    fallisci "Prima prepara il riparo.";
Fine regola.

Scena "pioggia" dal turno 3 al turno 4:
    Inizio "La pioggia batte sul tetto.".
    Fine "Il cielo si schiarisce.".
    Punti 2.
Fine scena.
```

| Comando | Risultato |
| --- | --- |
| `attendi` | «Prima prepara il riparo.»; turno 1; il contatore resta zero |
| `prepara` | Riparo pronto, turno 2 |
| `z` | Risposta personalizzata, turno 3, inizio della pioggia |
| `wait` | Seconda attesa riuscita, turno 4, fine della pioggia e 2 punti |
| `punteggio` | 2 punti, senza avanzare il tempo |

La fase `invece` sostituisce «Il tempo passa.» con una risposta propria.
La regola successiva può ancora far fallire l’intera azione: il primo tentativo
annulla sia l’incremento di attese sia il testo «Ascolti la pioggia dal riparo.».
Resta visibile soltanto il motivo del fallimento.

Dopo `prepara`, il controllo non fallisce più: ogni attesa incrementa il
contatore una sola volta. Prova altri `aspetta`: il punteggio resta 2 perché
la scena conclusa non assegna nuovamente il premio. Il contatore attese è una
proprietà del mondo; non è un nuovo comando del giocatore.

Il rollback riguarda gli effetti delle regole. Un’azione riconosciuta che
fallisce può comunque consumare un turno: qui la prima attesa porta il tempo
a 1. Il ciclo delle scene avviene dopo la transazione delle regole.
