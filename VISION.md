# Visione

Italica permette ad autori italiani di descrivere sistemi narrativi leggibili,
verificabili e riproducibili. Inform è un riferimento concettuale, non un formato
da emulare. Non promettiamo di superarlo in ogni dimensione: misureremo chiarezza
delle diagnosi, modularità, riproducibilità, copertura dei casi d'uso e facilità
con cui una libreria introduce un dominio senza cambiare il compilatore.

## Vincoli

Sorgente, comandi e diagnostica per l'autore in italiano. Identificatori interni
Python in inglese per interoperabilità con strumenti e contributori; non sono
sintassi del linguaggio. Core deterministico e offline, nessun LLM necessario.
Parser autore e giocatore indipendenti; AST e IR strutturati. Test e documentazione
sono parte di ogni feature. Il runtime non interpreta frasi sorgente.

Il dominio IF vive nella stdlib; altre librerie potranno modellare didattica,
RPG, visual novel, simulazioni e narrativa procedurale. Python è la prima
implementazione di riferimento, non la definizione della semantica.

## Critica e limiti

Italiano arbitrario e interpretazione prevedibile sono obiettivi in tensione.
Una forma non prevista deve generare una diagnosi, mai un'ipotesi silenziosa.
Genere grammaticale, numero e identità non vanno confusi: «la guardia» non
stabilisce il genere di una persona. Pronomi e soggetti impliciti nell'autore
richiedono regole di scope ancora da progettare; nel giocatore richiedono memoria
del discorso e disambiguazione esplicita.

Estensibilità illimitata di sintassi e semantica non è gratuita: moduli devono
dichiarare vocabolario, collisioni e dipendenze. Non accettiamo monkey patch del
compilatore come sistema di estensioni. Prestazioni e browser richiedono misure:
non promettiamo che un interprete Python sia automaticamente una soluzione web.

Nessuna compatibilità binaria o sorgente con Inform; importatori eventuali saranno
progetti separati. Nessun editor, conversazione, combattimento o NLP in questa fase.
