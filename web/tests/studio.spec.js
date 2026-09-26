import { test, expect } from "@playwright/test";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { unzipSync } from "fflate";
test("progetto, compilazione, gioco, test e release statica", async ({
  page,
  context,
}) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/");
  await expect(page.locator("#compileStatus")).toContainText("compilato", {
    timeout: 90000,
  });
  await page
    .getByRole("button", { name: "▶ Compila e prova", exact: true })
    .click();
  await expect(page.locator("#transcript")).toContainText("Molo");
  await page.locator("#command").fill("apri custodia");
  await page.locator("#send").click();
  await expect(page.locator("#transcript")).toContainText(
    "Hai aperto: custodia.",
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
  await expect(page.locator("#diagnostics")).toContainText("04_faro.locus");
  await page.getByRole("button", { name: "Apri nel manuale ↗" }).click();
  await expect(page.locator("#manualContent")).toContainText("M2");
  await page.reload();
  await expect(page.locator("#diagnostics")).toContainText("E102", {
    timeout: 90000,
  });
  await expect(page.locator(".cm-content")).toContainText("tipoignoto");
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
