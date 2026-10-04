# 14. Un taccuino di indizi

Apri `examples/tutorial/14_taccuino_indizi.locus` nello Studio. L'esempio
registra due indizi in una proprietà tipata e consente la deduzione soltanto
quando entrambi sono presenti.

La parte essenziale è:

```locus
La Sala è una stanza.
L'impronta è uno scenario nella Sala.
Il taccuino è uno scenario nella Sala.
La indizi è una proprietà elenco di testi.

Regola "annota l'orma" per esaminare "impronta" nella fase dopo
quando non "indizi" di "taccuino" contiene "orma":
    aggiungi "orma" a "indizi" di "taccuino";
    dì "Annoti l'orma nel taccuino.";
Fine regola.
```

Prova questa sequenza:

| Comando | Risultato da controllare |
| --- | --- |
| `deduci` | La regola rifiuta una conclusione prematura |
| `x impronta` | Viene aggiunto `"orma"` |
| `x impronta` | L'indizio non viene duplicato, grazie alla condizione |
| `x lettera` | Viene aggiunto `"fibra rossa"` |
| `deduci` | I due elementi permettono di risolvere l'enigma |
| `dimentica impronta` | Una sola occorrenza viene rimossa |
| `deduci` | La conclusione torna incompleta |

L'elenco consente duplicati; è la condizione `non ... contiene ...` a rendere
idempotente la raccolta dell'esempio. Questa distinzione permette anche storie
in cui lo stesso evento deve essere registrato più volte.

**Errore guidato.** Sostituisci `"orma"` con `1` nell'effetto `aggiungi`.
La compilazione deve fermarsi con `E313`, perché `indizi` è un elenco di testi.

**Esercizio.** Aggiungi un terzo scenario, `finestra rotta`, e richiedi
`"vetro"` insieme agli altri due indizi per la deduzione.

**Soluzione.** Crea due regole per esaminare la finestra, una con `non ...
contiene "vetro"` che aggiunge l'elemento e una con `contiene "vetro"` per la
ripetizione. Aggiungi poi la terza condizione alla regola `deduzione completa`.

Consulta la [specifica degli elenchi tipati](../linguaggio/liste-tipate.md) per
duplicati, rimozione, rollback e limiti correnti.

## Prima annotazione e visite successive

Nell'esempio completo, le regole «orma già annotata» e «fibra già annotata»
hanno `priorità 10`; quelle che aggiungono l'indizio mantengono la priorità zero.
Il motore valuta le condizioni sullo stato corrente quando raggiunge ciascuna
regola. Il caso «già annotato» deve quindi essere controllato prima della raccolta:
altrimenti, subito dopo aver scritto l'indizio, anche quel messaggio diventerebbe
vero e comparirebbe durante la prima osservazione.

Alla prima visita devi leggere soltanto «Annoti…»; alla seconda soltanto
«…è già annotata». L'elenco non cambia alla seconda visita. Usa lo stesso ordine
per la soluzione della finestra rotta: assegna priorità 10 alla regola della
ripetizione, lasciando a zero quella che aggiunge `"vetro"`.
