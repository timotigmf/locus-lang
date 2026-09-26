import { build } from "esbuild";
import { zipSync, strToU8 } from "fflate";
import { readdir, readFile, mkdir, cp, writeFile, rm } from "node:fs/promises";
import { join, relative } from "node:path";
const root = new URL("../", import.meta.url).pathname;
const out = new URL("./site/", import.meta.url).pathname;
await rm(out, { recursive: true, force: true });
await mkdir(out, { recursive: true });
await cp(new URL("./public/", import.meta.url), out, { recursive: true });
await build({
  entryPoints: ["src/app.js", "src/player.js"],
  bundle: true,
  format: "esm",
  outdir: out,
  minify: true,
  sourcemap: false,
  legalComments: "eof",
});
await cp("src/worker.js", join(out, "worker.js"));
async function walk(dir) {
  let a = [];
  for (const e of await readdir(dir, { withFileTypes: true })) {
    const p = join(dir, e.name);
    if (e.isDirectory()) {
      if (!e.name.startsWith("__")) a.push(...(await walk(p)));
    } else a.push(p);
  }
  return a;
}
const python = {};
for (const p of await walk(join(root, "src/locus"))) {
  if (p.endsWith(".py"))
    python[relative(join(root, "src"), p)] = new Uint8Array(await readFile(p));
}
await writeFile(join(out, "locus-python.zip"), zipSync(python));
await mkdir(join(out, "runtime"));
const runtime = [];
for (const name of [
  "pyodide.mjs",
  "pyodide.asm.mjs",
  "pyodide.asm.wasm",
  "python_stdlib.zip",
  "pyodide-lock.json",
]) {
  await cp(join("node_modules/pyodide", name), join(out, "runtime", name));
  runtime.push("runtime/" + name);
}
const docs = {};
for (const p of [
  ...(await walk(join(root, "docs"))),
  join(root, "LANGUAGE_SPEC.md"),
  join(root, "README.md"),
]) {
  if (p.endsWith(".md")) docs[relative(root, p)] = await readFile(p, "utf8");
}
await writeFile(join(out, "manual.json"), JSON.stringify(docs));
const demoFiles = {};
demoFiles["storia.locus"] = await readFile(
  join(root, "examples/tutorial/studio_faro.locus"),
  "utf8",
);
const demo = {
  format: "locus-project-1",
  title: "Il faro di Selce",
  entry: "storia.locus",
  files: demoFiles,
  tests: [
    {
      name: "Il segnale nella foschia",
      commands: await readFile(
        join(root, "examples/tutorial/04_faro.comandi"),
        "utf8",
      ),
      expected: await readFile(
        join(root, "examples/tutorial/04_faro.atteso"),
        "utf8",
      ),
    },
  ],
};
await writeFile(join(out, "demo.json"), JSON.stringify(demo));
const legacyFiles = {};
for (const name of ["faro/mondo.locus", "faro/regole.locus", "04_faro.locus"])
  legacyFiles[name] = await readFile(
    join(root, "examples/tutorial", name),
    "utf8",
  );
await writeFile(
  join(out, "legacy-demo.json"),
  JSON.stringify({
    format: "locus-project-1",
    title: "Il faro di Selce",
    entry: "04_faro.locus",
    files: legacyFiles,
    tests: demo.tests,
  }),
);
let notices =
  "LOCUS Studio — componenti di terze parti\n\nPyodide 314.0.7 (MPL-2.0), non modificato. Sorgente: https://github.com/pyodide/pyodide/tree/314.0.7\nCPython (PSF): https://github.com/python/cpython\n\n";
for (const name of [
  "pyodide",
  "codemirror",
  "@codemirror/view",
  "@codemirror/state",
  "@codemirror/language",
  "@codemirror/commands",
  "@codemirror/autocomplete",
  "@codemirror/lint",
  "@codemirror/search",
  "@lezer/common",
  "@lezer/highlight",
  "@lezer/lr",
  "style-mod",
  "w3c-keyname",
  "crelt",
  "fflate",
  "marked",
  "dompurify",
]) {
  for (const file of ["LICENSE", "LICENSE.md", "LICENSE.txt"]) {
    try {
      notices +=
        `\n===== ${name} =====\n` +
        (await readFile(join("node_modules", name, file), "utf8"));
      break;
    } catch {}
  }
}
for (const p of await walk("licenses"))
  notices += "\n===== " + p + " =====\n" + (await readFile(p, "utf8"));
await writeFile(join(out, "LICENZE.txt"), notices);
await writeFile(
  join(out, "release-assets.json"),
  JSON.stringify([
    ...runtime,
    "locus-python.zip",
    "worker.js",
    "player.js",
    "player.html",
    "style.css",
    "LICENZE.txt",
  ]),
);
await writeFile(join(out, ".nojekyll"), "");
console.log(
  "Studio costruito in web/site, runtime incluso e nessun CDN richiesto.",
);
