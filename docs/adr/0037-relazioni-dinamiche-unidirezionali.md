# ADR 0037 — relazioni dinamiche a senso unico

Stato: accettato, 2026-10-01.

## Contesto

Le dichiarazioni iniziali possono omettere l'arco inverso, ma una regola che
rivela o nasconde un passaggio continua a modificare entrambe le direzioni.
Botole, cadute e varchi richiusi richiedono la stessa topologia anche quando
compaiono durante la storia.

## Decisione

Gli effetti accettano la qualificazione italiana `a senso unico`:

```text
crea relazione a senso unico "nord" da "Sala" a "Cripta";
rimuovi relazione a senso unico "nord" da "Sala" a "Cripta";
```

L'AST conserva un indicatore nel riferimento di relazione. Il compilatore
risolve tipi e ID come prima, ma produce un solo `RelationEdge`. L'effetto IR e
il runtime restano invariati: applicano atomicamente l'insieme di archi già
risolto. Gli alias di percorso come `su` e `giù` sono ammessi soltanto nella
forma a senso unico.

## Alternative considerate

- Aggiungere nuovi tipi di effetto IR: duplicazione non necessaria, perché
  `RelationChange` rappresenta già uno o più archi.
- Creare l'inversa e rimuoverla con un secondo effetto: espone uno stato
  intermedio ai controlli transazionali e rende il sorgente fragile.
- Usare una proprietà della stanza: separerebbe la navigazione dal grafo che
  alimenta runtime e atlante.

## Conseguenze e verifica

Creazione e rimozione restano idempotenti e partecipano al rollback. La forma
senza qualificazione conserva il comportamento bidirezionale. Test di parser,
lowering, runtime, Studio, tutorial e browser verificano il singolo arco e la
freccia dinamica. L'IR resta alla versione 21.
