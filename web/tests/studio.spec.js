import { test, expect } from "@playwright/test";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { unzipSync } from "fflate";
test("progetto, compilazione, gioco, test e release statica", async ({
  page,
  context,
}) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await context.grantPermissions(["clipboard-read", "clipboard-write"]);
  await page.goto("/");
  await expect(page.locator("#compileStatus")).toContainText("compilato", {
    timeout: 90000,
  });
  await expect(page.locator("#files .file")).toHaveCount(1);
  await expect(page.locator("#activeFile")).toHaveText("storia.locus");
  await expect(page.locator(".cm-content")).toContainText(
    'Titolo: "Il faro di Selce"',
  );
  await expect(page.locator(".cm-content")).not.toContainText("Includi");
  await expect(page.locator("#title")).toHaveValue("Il faro di Selce");
  await expect(page.locator("#storyByline")).toHaveText("di Esempio LOCUS");
  const pixel = Buffer.from(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=",
    "base64",
  );
  await page.locator("#assetFile").setInputFiles({
    name: "molo.png",
    mimeType: "image/png",
    buffer: pixel,
  });
  await expect(page.locator("#assets")).toContainText("media/molo.png");
  await page.locator(".cm-content").click();
  await page.keyboard.press("ControlOrMeta+End");
  await page.keyboard.insertText(
    '\nIl Molo ha immagine "media/molo.png".\nIl Molo ha testo alternativo "Il molo nella foschia.".\nLa Vedetta è una stanza.\nLa Vedetta è a nordest del Molo.\nLa Torre è una stanza.\nLa Torre sovrasta il Molo.\nLa Camera Ottica è una stanza.\nIl Molo racchiude la Camera Ottica.',
  );
  await page
    .getByRole("button", { name: "▶ Compila e prova", exact: true })
    .click();
  await expect(page.locator("#transcript")).toContainText("Molo");
  await expect(page.locator("#mediaStage img")).toHaveAttribute(
    "alt",
    "Il molo nella foschia.",
  );
  await page.locator("#command").fill("e");
  await page.locator("#send").click();
  const absentExit = page.locator(".story-output", {
    hasText: "Non c'è alcun passaggio in quella direzione.",
  });
  await expect(absentExit).toHaveCount(1);
  await page.locator("#command").fill("o");
  await page.locator("#send").click();
  await expect(absentExit).toHaveCount(2);
  await page.locator("#command").fill("ne");
  await page.locator("#send").click();
  await expect(page.locator(".story-output").last()).toContainText("Vedetta");
  await page.locator("#command").fill("so");
  await page.locator("#send").click();
  await expect(page.locator(".story-output").last()).toContainText("Molo");
  await page.locator("#command").fill("u");
  await page.locator("#send").click();
  await expect(page.locator(".story-output").last()).toContainText("Torre");
  await page.locator("#command").fill("d");
  await page.locator("#send").click();
  await expect(page.locator(".story-output").last()).toContainText("Molo");
  await page.locator("#command").fill("dentro");
  await page.locator("#send").click();
  await expect(page.locator(".story-output").last()).toContainText(
    "Camera Ottica",
  );
  await page.locator("#command").fill("fuori");
  await page.locator("#send").click();
  await expect(page.locator(".story-output").last()).toContainText("Molo");
  await page.locator("#command").fill("apri custodia");
  await page.locator("#send").click();
  await expect(page.locator("#transcript")).toContainText(
    "Hai aperto: custodia.",
  );
  await page.locator("#command").fill("x scatola");
  await page.locator("#send").click();
  await expect(page.locator("#transcript")).toContainText("Stato: aperto.");
  await page.locator("#command").fill("prendi chiave");
  await page.locator("#send").click();
  await expect(page.locator("#transcript")).toContainText(
    "Hai preso: chiave di rame.",
  );
  await page.getByRole("button", { name: "Test", exact: true }).click();
  await page.locator("#runTest").click();
  await expect(page.locator("#testResult")).toContainText("SUPERATO", {
    timeout: 30000,
  });
  await page.getByRole("button", { name: "Mappa", exact: true }).click();
  await expect(page.locator("#mapCanvas svg")).toBeVisible();
  await expect(page.locator("#mapCanvas svg")).toContainText(
    "nordest / sudovest",
  );
  await expect(page.locator("#mapCanvas svg")).toContainText("su / giù");
  await expect(page.locator("#mapCanvas svg")).toContainText("dentro / fuori");
  await expect(
    page.locator('#mapCanvas path[stroke-dasharray="6 4"]'),
  ).toHaveCount(1);
  await expect(
    page.locator('#mapCanvas path[stroke-dasharray="2 3"]'),
  ).toHaveCount(1);
  const mapDownload = page.waitForEvent("download");
  await page.locator("#exportMap").click();
  expect((await mapDownload).suggestedFilename()).toBe("mappa-locus.svg");
  await page
    .getByRole("button", { name: "Indice del mondo", exact: true })
    .click();
  await expect(page.locator("#index")).toContainText("cosa › contenitore");
  await expect(page.locator("#index")).toContainText("Gerarchia dei tipi");
  await expect(page.locator("#index")).toContainText("Relazioni");
  await expect(page.locator("#index")).toContainText("Vocabolario");
  await expect(page.locator("#index")).toContainText("Regole");
  await page.locator("#indexSearch").fill("scatola");
  await expect(page.locator("#indexSearchCount")).toContainText("1 voce");
  await page.locator("#indexSearch").fill("termine inesistente zzz");
  await expect(page.locator("#indexEmpty")).toBeVisible();
  await page.locator("#indexSearch").fill("");
  const indexDownload = page.waitForEvent("download");
  await page.locator("#exportIndex").click();
  const indexFile = await indexDownload;
  expect(indexFile.suggestedFilename()).toBe("indice-mondo-locus.json");
  const exportedIndex = JSON.parse(
    await readFile(await indexFile.path(), "utf8"),
  );
  expect(exportedIndex.version).toBe(21);
  expect(exportedIndex.rules.length).toBeGreaterThan(0);
  expect(exportedIndex.synonyms.some((item) => item.alias === "scatola")).toBe(
    true,
  );
  await page.getByRole("button", { name: "Storia", exact: true }).click();
  await page.screenshot({ path: "test-results/studio.png", fullPage: true });
  const downloadPromise = page.waitForEvent("download");
  await page.locator("#release").click();
  const downloaded = await downloadPromise;
  const bytes = await readFile(await downloaded.path());
  const files = unzipSync(bytes);
  expect(files["runtime/pyodide.asm.wasm"]).toBeTruthy();
  expect(files["project.json"]).toBeTruthy();
  expect(Buffer.from(files["media/molo.png"])).toEqual(pixel);
  // Una release servita sotto un percorso diverso, senza dipendenze CDN.
  for (const [name, data] of Object.entries(files)) {
    const dest = "site/release-test/" + name;
    await mkdir(dest.slice(0, dest.lastIndexOf("/")), { recursive: true });
    await writeFile(dest, data);
  }
  const player = await context.newPage();
  await player.route("**/*", (route) =>
    route.request().url().startsWith("http://127.0.0.1:8765/")
      ? route.continue()
      : route.abort(),
  );
  await player.goto("/release-test/");
  await expect(player.locator("#transcript")).toContainText("Molo", {
    timeout: 90000,
  });
  await expect(player.locator("#mediaStage img")).toBeVisible();
  await player.locator("#command").fill("apri custodia");
  await player.locator("#send").click();
  await expect(player.locator("#transcript")).toContainText(
    "Hai aperto: custodia.",
  );
  await page.locator("#commandGuideButton").click();
  await expect(page.locator("#manualContent")).toContainText(
    "Comandi, abbreviazioni e nomi degli oggetti",
  );
  await page.locator("#manualButton").click();
  await expect(page.locator("#manualContent")).toContainText(
    "Manuale dell'autore LOCUS",
  );
  await expect(page.locator("#manualContent .copy-code").first()).toBeVisible();
  await page.locator("#manualContent .copy-code").first().click();
  await expect(page.locator("#manualContent .copy-code").first()).toHaveText(
    "Copiato ✓",
  );
  expect(errors).toEqual([]);
});
test("diagnosi precisa, manuale e persistenza", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("#compileStatus")).toContainText("compilato", {
    timeout: 90000,
  });
  await page.locator(".cm-content").click();
  await page.keyboard.press("ControlOrMeta+End");
  await page.keyboard.insertText("\nLa Fantasma è un tipoignoto.");
  await page.locator("#compile").click();
  await expect(page.locator("#diagnostics")).toContainText("E102");
  await expect(page.locator("#diagnostics")).toContainText("storia.locus");
  await page.getByRole("button", { name: "Apri nel manuale ↗" }).click();
  await expect(page.locator("#manualContent")).toContainText(
    "Tipi definiti dall'autore",
  );
  await page.reload();
  await expect(page.locator("#diagnostics")).toContainText("E102", {
    timeout: 90000,
  });
  await expect(page.locator(".cm-content")).toContainText("tipoignoto");
});
test("migra soltanto l'esempio modulare distribuito", async ({ page }) => {
  const files = {};
  for (const name of [
    "faro/mondo.locus",
    "faro/regole.locus",
    "04_faro.locus",
  ]) {
    files[name] = await readFile("../examples/tutorial/" + name, "utf8");
  }
  const tests = [
    {
      name: "Il segnale nella foschia",
      commands: await readFile("../examples/tutorial/04_faro.comandi", "utf8"),
      expected: await readFile("../examples/tutorial/04_faro.atteso", "utf8"),
    },
  ];
  await page.addInitScript(
    ({ legacyFiles, legacyTests }) => {
      localStorage.setItem(
        "locus-studio-project-v1",
        JSON.stringify({
          format: "locus-project-1",
          title: "Il faro di Selce",
          entry: "04_faro.locus",
          files: legacyFiles,
          tests: legacyTests,
        }),
      );
    },
    { legacyFiles: files, legacyTests: tests },
  );
  await page.goto("/");
  await expect(page.locator("#compileStatus")).toContainText("compilato", {
    timeout: 90000,
  });
  await expect(page.locator("#files .file")).toHaveCount(1);
  await expect(page.locator("#activeFile")).toHaveText("storia.locus");
  await expect(page.locator("#toast")).toContainText("sorgente unico");
});
test("gestione file, backup e confronto test negativo", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("#compileStatus")).toContainText("compilato", {
    timeout: 90000,
  });
  await page.locator("#addFile").click();
  await page.locator("#dialogInput").fill("appunti.locus");
  await page.locator("#dialogConfirm").click();
  await expect(page.locator("#activeFile")).toHaveText("appunti.locus");
  await page.locator(".cm-content").click();
  await page.keyboard.insertText("La spiaggia è una stanza.");
  await page.locator("#renameFile").click();
  await page.locator("#dialogInput").fill("paesaggio.locus");
  await page.locator("#dialogConfirm").click();
  await expect(page.locator("#activeFile")).toHaveText("paesaggio.locus");
  const d = page.waitForEvent("download");
  await page.locator("#backup").click();
  const p = JSON.parse(await readFile(await (await d).path(), "utf8"));
  expect(p.files["paesaggio.locus"]).toContain("spiaggia");
  await page.locator("#deleteFile").click();
  await page.locator("#dialogConfirm").click();
  await expect(page.locator('[data-file="paesaggio.locus"]')).toHaveCount(0);
  await page.getByRole("button", { name: "Test", exact: true }).click();
  await page.locator("#testExpected").fill("Testo diverso\n");
  await page.locator("#runTest").click();
  await expect(page.locator("#testResult")).toContainText("NON SUPERATO");
  await expect(page.locator("#testResult")).toContainText("riga 1");
});
test("mobile: menu progetto e nessun overflow orizzontale", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await expect(page.locator("#compileStatus")).toContainText("compilato", {
    timeout: 90000,
  });
  await page.locator("#toggleFiles").click();
  await expect(page.locator("#files")).toBeVisible();
  await page.locator("#toggleFiles").click();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
});

test("azione tipata dell'autore nello Studio", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("#compileStatus")).toContainText("compilato", {
    timeout: 90000,
  });
  const source = `Titolo: "Il gong".
La Sala è una stanza.
Il gong è una cosa nella Sala.
Il martello è una cosa nella Sala.
Azione "suonare" su una cosa con una cosa con comando "suona"
    e sinonimo "fai risuonare" e separatore "insieme a".
Regola "rintocco" per suonare "gong" con "martello" nella fase invece:
    dì "Il gong risuona nella sala.";
Fine regola.`;
  await page.locator(".cm-content").click();
  await page.keyboard.press("ControlOrMeta+A");
  await page.keyboard.insertText(source);
  await page
    .getByRole("button", { name: "▶ Compila e prova", exact: true })
    .click();
  await expect(page.locator("#transcript")).toContainText("Sala", {
    timeout: 90000,
  });
  await page.locator("#command").fill("fai risuonare gong insieme al martello");
  await page.locator("#send").click();
  await expect(page.locator("#transcript")).toContainText(
    "Il gong risuona nella sala.",
  );
  await page
    .getByRole("button", { name: "Indice del mondo", exact: true })
    .click();
  await expect(page.locator("#index")).toContainText(
    "Azioni definite dall'autore",
  );
  await expect(page.locator("#index")).toContainText("suona");
  await expect(page.locator("#index")).toContainText("fai risuonare");
  await expect(page.locator("#index")).toContainText("insieme a");
});

test("passaggio segreto aggiorna navigazione e mappa", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("#compileStatus")).toContainText("compilato", {
    timeout: 90000,
  });
  const source = `Titolo: "Il varco".
La Sala è una stanza.
La Cripta è una stanza.
La leva è una cosa nella Sala.
Regola "rivela" per esaminare "leva" nella fase dopo:
    crea relazione "nord" da "Sala" a "Cripta";
    dì "Il varco è aperto.";
Fine regola.`;
  await page.locator(".cm-content").click();
  await page.keyboard.press("ControlOrMeta+A");
  await page.keyboard.insertText(source);
  await page
    .getByRole("button", { name: "▶ Compila e prova", exact: true })
    .click();
  await expect(page.locator("#mapSummary")).toContainText("0 collegamenti", {
    timeout: 90000,
  });
  await page.locator("#command").fill("x leva");
  await page.locator("#send").click();
  await expect(page.locator("#transcript")).toContainText("Il varco è aperto.");
  await expect(page.locator("#mapSummary")).toContainText("1 collegamenti");
  await page.locator("#command").fill("nord");
  await page.locator("#send").click();
  await expect(page.locator("#transcript")).toContainText("Cripta");
  await page.locator("#command").fill("sud");
  await page.locator("#send").click();
  await expect(page.locator("#transcript")).toContainText("Sala");
});

test("scenario rivela un oggetto inizialmente invisibile", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("#compileStatus")).toContainText("compilato", {
    timeout: 90000,
  });
  const source = `Titolo: "Il mosaico".
La Sala è una stanza.
Il mosaico è uno scenario nella Sala.
La chiave è una cosa nella Sala.
La chiave ha visibile falso.
Regola "rivela" per esaminare "mosaico" nella fase dopo:
    imposta "visibile" di "chiave" a vero;
    dì "Una chiave compare dietro il mosaico.";
Fine regola.`;
  await page.locator(".cm-content").click();
  await page.keyboard.press("ControlOrMeta+A");
  await page.keyboard.insertText(source);
  await page
    .getByRole("button", { name: "▶ Compila e prova", exact: true })
    .click();
  await expect(page.locator("#transcript")).toContainText("Vedi: mosaico.", {
    timeout: 90000,
  });
  await page.locator("#command").fill("prendi chiave");
  await page.locator("#send").click();
  await expect(page.locator("#transcript")).toContainText(
    "Non trovi qui quell'oggetto.",
  );
  await page.locator("#command").fill("prendi mosaico");
  await page.locator("#send").click();
  await expect(page.locator("#transcript")).toContainText(
    "Non puoi prendere questo elemento.",
  );
  await page.locator("#command").fill("x mosaico");
  await page.locator("#send").click();
  await expect(page.locator("#transcript")).toContainText(
    "Una chiave compare dietro il mosaico.",
  );
  await page.locator("#command").fill("guarda");
  await page.locator("#send").click();
  await expect(page.locator(".story-output").last()).toContainText(
    "Vedi: mosaico, chiave.",
  );
});

test("elenco tipato raccoglie indizi nello Studio", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("#compileStatus")).toContainText("compilato", {
    timeout: 90000,
  });
  const source = `Titolo: "Gli indizi".
La Sala è una stanza.
Il taccuino è uno scenario nella Sala.
La indizi è una proprietà elenco di testi.
Azione "annotare" senza oggetti con comando "annota".
Azione "dedurre" senza oggetti con comando "deduci".
Regola "annotazione" per annotare nella fase invece:
    aggiungi "orma" a "indizi" di "taccuino";
    dì "Indizio registrato.";
Fine regola.
Regola "deduzione" per dedurre nella fase invece
quando "indizi" di "taccuino" contiene "orma":
    dì "La traccia porta al cortile.";
Fine regola.`;
  await page.locator(".cm-content").click();
  await page.keyboard.press("ControlOrMeta+A");
  await page.keyboard.insertText(source);
  await page
    .getByRole("button", { name: "▶ Compila e prova", exact: true })
    .click();
  await expect(page.locator("#transcript")).toContainText("Sala", {
    timeout: 90000,
  });
  await page.locator("#command").fill("annota");
  await page.locator("#send").click();
  await expect(page.locator("#transcript")).toContainText(
    "Indizio registrato.",
  );
  await page.locator("#command").fill("deduci");
  await page.locator("#send").click();
  await expect(page.locator("#transcript")).toContainText(
    "La traccia porta al cortile.",
  );
  await page
    .getByRole("button", { name: "Indice del mondo", exact: true })
    .click();
  await expect(page.locator("#index")).toContainText("orma");
});

test("tabella tipata aggiorna le righe nell'indice", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("#compileStatus")).toContainText("compilato", {
    timeout: 90000,
  });
  const source = `Titolo: "Il deposito".
La Sala è una stanza.
Azione "trasferire" senza oggetti con comando "trasferisci".
Tabella "deposito":
    Colonna "nome" testuale.
    Colonna "valore" numerica.
    Riga "astrolabio" 40.
Fine tabella.
Regola "trasferimento" per trasferire nella fase invece:
    rimuovi riga "astrolabio" 40 da tabella "deposito";
    aggiungi riga "maschera" 25 a tabella "deposito";
    dì "Registro aggiornato.";
Fine regola.`;
  await page.locator(".cm-content").click();
  await page.keyboard.press("ControlOrMeta+A");
  await page.keyboard.insertText(source);
  await page
    .getByRole("button", { name: "▶ Compila e prova", exact: true })
    .click();
  await expect(page.locator("#transcript")).toContainText("Sala", {
    timeout: 90000,
  });
  await page
    .getByRole("button", { name: "Indice del mondo", exact: true })
    .click();
  await expect(page.locator("#index")).toContainText("astrolabio");
  await page.locator("#command").fill("trasferisci");
  await page.locator("#send").click();
  await expect(page.locator("#transcript")).toContainText(
    "Registro aggiornato.",
  );
  await expect(page.locator("#index")).toContainText("maschera");
  await expect(page.locator("#index")).not.toContainText("astrolabio");
});

test("dialogo strutturato nello Studio con indice e trace", async ({
  page,
}) => {
  await page.goto("/");
  await expect(page.locator("#compileStatus")).toContainText("compilato", {
    timeout: 90000,
  });
  const source = `Titolo: "La guardiana".
La Sala è una stanza.
La guardiana è una persona nella Sala.
Dialogo "segreti" con "guardiana":
    Nodo "inizio" dice "La guardiana attende.":
        Scelta "Chiedi della torre" porta a "torre".
        Scelta "Saluta" termina.
    Fine nodo.
    Nodo "torre" dice "La torre custodisce il fuoco.":
    Fine nodo.
Fine dialogo.`;
  await page.locator(".cm-content").click();
  await page.keyboard.press("ControlOrMeta+A");
  await page.keyboard.insertText(source);
  await page
    .getByRole("button", { name: "▶ Compila e prova", exact: true })
    .click();
  await expect(page.locator("#compileStatus")).toContainText("1 dialoghi", {
    timeout: 90000,
  });
  await page
    .getByRole("button", { name: "Indice del mondo", exact: true })
    .click();
  await expect(page.locator("#index")).toContainText("Dialoghi");
  await expect(page.locator("#index")).toContainText("segreti");
  await expect(page.locator("#index")).toContainText("guardiana");
  await page.getByRole("button", { name: "Storia", exact: true }).click();
  await page.locator("#command").fill("parla con guardiana");
  await page.locator("#send").click();
  await expect(page.locator("#transcript")).toContainText(
    "1. Chiedi della torre",
  );
  await expect(page.locator("#trace")).toContainText(
    "Dialogo «segreti» · nodo «inizio»",
  );
  await page.locator("#command").fill("1");
  await page.locator("#send").click();
  await expect(page.locator("#transcript")).toContainText(
    "La torre custodisce il fuoco.",
  );
  await expect(page.locator("#trace")).toContainText(
    "scelta «Chiedi della torre» · concluso",
  );
});

test("scena temporale e punteggio nello Studio", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("#compileStatus")).toContainText("compilato", {
    timeout: 90000,
  });
  const source = `Titolo: "Il temporale".
La Torre è una stanza.
L'orologio è uno scenario nella Torre.
Scena "temporale" dal turno 1 al turno 2:
    Inizio "Il temporale comincia.".
    Fine "Il temporale finisce.".
    Punti 5.
Fine scena.`;
  await page.locator(".cm-content").click();
  await page.keyboard.press("ControlOrMeta+A");
  await page.keyboard.insertText(source);
  await page
    .getByRole("button", { name: "▶ Compila e prova", exact: true })
    .click();
  await expect(page.locator("#compileStatus")).toContainText("1 scene", {
    timeout: 90000,
  });
  await page
    .getByRole("button", { name: "Indice del mondo", exact: true })
    .click();
  await expect(page.locator("#index")).toContainText(
    "Scene, tempo e punteggio",
  );
  await expect(page.locator("#index")).toContainText("temporale");
  await expect(page.locator("#index")).toContainText("turno 2");
  await page.getByRole("button", { name: "Storia", exact: true }).click();
  await page.locator("#command").fill("guarda");
  await page.locator("#send").click();
  await expect(page.locator("#transcript")).toContainText(
    "Il temporale comincia.",
  );
  await expect(page.locator("#trace")).toContainText(
    "Scena «temporale» · iniziata al turno 1",
  );
  await page.locator("#command").fill("esamina orologio");
  await page.locator("#send").click();
  await expect(page.locator("#transcript")).toContainText(
    "Il temporale finisce.",
  );
  await expect(page.locator("#trace")).toContainText("+5 punti");
  await page.locator("#command").fill("punteggio");
  await page.locator("#send").click();
  await expect(page.locator(".story-output").last()).toHaveText(
    "Punteggio: 5.",
  );
});

test("veicolo, movimento e mappa nello Studio", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("#compileStatus")).toContainText("compilato", {
    timeout: 90000,
  });
  const source = `Titolo: "La corsa".
La Rimessa è una stanza.
La Piazza è una stanza.
La Piazza è a est della Rimessa.
Una bicicletta è un tipo di veicolo.
La saetta rossa è una bicicletta nella Rimessa.`;
  await page.locator(".cm-content").click();
  await page.keyboard.press("ControlOrMeta+A");
  await page.keyboard.insertText(source);
  await page
    .getByRole("button", { name: "▶ Compila e prova", exact: true })
    .click();
  await expect(page.locator("#compileStatus")).toContainText("1 veicoli", {
    timeout: 90000,
  });
  await page
    .getByRole("button", { name: "Indice del mondo", exact: true })
    .click();
  await expect(page.locator("#index")).toContainText("Veicoli");
  const vehicleRows = page
    .getByRole("heading", { name: "Veicoli", exact: true })
    .locator("xpath=following-sibling::table[1]")
    .locator("tr");
  await expect(vehicleRows.filter({ hasText: "saetta rossa" })).toContainText(
    "Rimessa",
  );
  await page.getByRole("button", { name: "Storia", exact: true }).click();
  await page.locator("#command").fill("sali sulla saetta");
  await page.locator("#send").click();
  await expect(page.locator("#transcript")).toContainText("salito a bordo");
  await page.locator("#command").fill("est");
  await page.locator("#send").click();
  await expect(page.locator("#transcript")).toContainText(
    "Sei a bordo di: saetta rossa.",
  );
  await page.getByRole("button", { name: "Mappa", exact: true }).click();
  await expect(page.locator("#mapSummary")).toContainText("1 veicoli");
  await expect(page.locator("#mapCanvas svg")).toContainText(
    "MEZZO · saetta rossa",
  );
  await page
    .getByRole("button", { name: "Indice del mondo", exact: true })
    .click();
  await expect(vehicleRows.filter({ hasText: "saetta rossa" })).toContainText(
    "Piazza",
  );
});

test("valuta, acquisto e indice del commercio", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("#compileStatus")).toContainText("compilato", {
    timeout: 90000,
  });
  const source = `Titolo: "Il mercato".
La Bottega è una stanza.
Il credito portuale è una valuta.
Il credito portuale ha saldo 15.
Una provvista è un tipo di prodotto.
La bussola è una provvista nella Bottega.
La bussola ha prezzo 7.
La corda è una provvista nella Bottega.
La corda ha prezzo 9.`;
  await page.locator(".cm-content").click();
  await page.keyboard.press("ControlOrMeta+A");
  await page.keyboard.insertText(source);
  await page
    .getByRole("button", { name: "▶ Compila e prova", exact: true })
    .click();
  await expect(page.locator("#compileStatus")).toContainText("2 merci", {
    timeout: 90000,
  });
  await page.locator("#command").fill("prendi bussola");
  await page.locator("#send").click();
  await expect(page.locator("#transcript")).toContainText("prima comprare");
  await page.locator("#command").fill("compra bussola");
  await page.locator("#send").click();
  await expect(page.locator("#transcript")).toContainText("Saldo: 8");
  await page.locator("#command").fill("compra corda");
  await page.locator("#send").click();
  await expect(page.locator("#transcript")).toContainText(
    "Fondi insufficienti",
  );
  await page
    .getByRole("button", { name: "Indice del mondo", exact: true })
    .click();
  const commerce = page
    .getByRole("heading", { name: "Commercio", exact: true })
    .locator("xpath=following-sibling::table[1]");
  await expect(commerce).toContainText("saldo 8");
  await expect(commerce).toContainText("bussola");
  await expect(commerce).toContainText("inventario");
  await expect(commerce).toContainText("corda");
  await expect(commerce).toContainText("Bottega");
});

test("mercante, scorta e rivendita atomica", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("#compileStatus")).toContainText("compilato", {
    timeout: 90000,
  });
  const source = `Titolo: "La bottega".
La Bottega è una stanza.
Il credito portuale è una valuta.
Il credito portuale ha saldo 20.
La Ada è una mercante nella Bottega.
La Ada ha cassa 25.
La bussola è un prodotto nella Bottega.
La bussola ha prezzo 7.
La bussola ha prezzo di rivendita 3.
La Ada vende la bussola.`;
  await page.locator(".cm-content").click();
  await page.keyboard.press("ControlOrMeta+A");
  await page.keyboard.insertText(source);
  await page
    .getByRole("button", { name: "▶ Compila e prova", exact: true })
    .click();
  await expect(page.locator("#compileStatus")).toContainText("1 mercanti", {
    timeout: 90000,
  });
  await page.locator("#command").fill("compra bussola da Ada");
  await page.locator("#send").click();
  await expect(page.locator("#transcript")).toContainText("Saldo: 13");
  await page.locator("#command").fill("vendi bussola a Ada");
  await page.locator("#send").click();
  await expect(page.locator("#transcript")).toContainText("Saldo: 16");
  await page
    .getByRole("button", { name: "Indice del mondo", exact: true })
    .click();
  const commerce = page
    .getByRole("heading", { name: "Commercio", exact: true })
    .locator("xpath=following-sibling::table[1]");
  await expect(commerce).toContainText("Ada");
  await expect(commerce).toContainText("cassa 29");
  await expect(commerce).toContainText("rivendita 3");
  await expect(commerce).toContainText("Bottega");
});

test("chiarimento a più turni per un nome ambiguo", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("#compileStatus")).toContainText("compilato", {
    timeout: 90000,
  });
  const source = `Titolo: "Le due chiavi".
La Sala è una stanza.
La chiave di rame è una chiave nella Sala.
La chiave di ferro è una chiave nella Sala.
Comprendi "scura" come "chiave di ferro".`;
  await page.locator(".cm-content").click();
  await page.keyboard.press("ControlOrMeta+A");
  await page.keyboard.insertText(source);
  await page
    .getByRole("button", { name: "▶ Compila e prova", exact: true })
    .click();
  await expect(page.locator("#compileStatus")).toContainText("compilato", {
    timeout: 90000,
  });
  await page.locator("#command").fill("prendi chiave");
  await page.locator("#send").click();
  await expect(page.locator(".story-output").last()).toContainText(
    "1) chiave di rame; 2) chiave di ferro",
  );
  await page.locator("#command").fill("scura");
  await page.locator("#send").click();
  await expect(page.locator(".story-output").last()).toContainText(
    "Hai preso: chiave di ferro.",
  );
});
