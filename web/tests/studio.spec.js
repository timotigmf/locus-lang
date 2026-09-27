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
  await page
    .getByRole("button", { name: "▶ Compila e prova", exact: true })
    .click();
  await expect(page.locator("#transcript")).toContainText("Molo");
  await page.locator("#command").fill("e");
  await page.locator("#send").click();
  const absentExit = page.locator(".story-output", {
    hasText: "Non c'è alcun passaggio in quella direzione.",
  });
  await expect(absentExit).toHaveCount(1);
  await page.locator("#command").fill("o");
  await page.locator("#send").click();
  await expect(absentExit).toHaveCount(2);
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
  const mapDownload = page.waitForEvent("download");
  await page.locator("#exportMap").click();
  expect((await mapDownload).suggestedFilename()).toBe("mappa-locus.svg");
  await page
    .getByRole("button", { name: "Indice del mondo", exact: true })
    .click();
  await expect(page.locator("#index")).toContainText("cosa › contenitore");
  await page.getByRole("button", { name: "Storia", exact: true }).click();
  await page.screenshot({ path: "test-results/studio.png", fullPage: true });
  const downloadPromise = page.waitForEvent("download");
  await page.locator("#release").click();
  const downloaded = await downloadPromise;
  const bytes = await readFile(await downloaded.path());
  const files = unzipSync(bytes);
  expect(files["runtime/pyodide.asm.wasm"]).toBeTruthy();
  expect(files["project.json"]).toBeTruthy();
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
