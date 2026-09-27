import { zipSync, strToU8 } from "fflate";
import { marked } from "marked";
import DOMPurify from "dompurify";
import { Engine, download, el, getJSON } from "./client.js";
import { makeEditor } from "./editor.js";
import { drawMap } from "./map.js";
const $ = (id) => document.getElementById(id);
const storageKey = "locus-studio-project-v1";
let project,
  activeFile,
  diagnostics = [],
  compiled = null,
  revision = 0,
  compiledRevision = -1,
  ready = false,
  busy = false;
let manual = {},
  currentManual = "docs/manuale/guida-autore.md",
  testIndex = 0,
  lastTranscript = "",
  mapSVG = "",
  zoom = 1;
const engine = new Engine();
const editor = makeEditor(
  $("editor"),
  (text) => {
    if (!project || !activeFile) return;
    project.files[activeFile] = text;
    dirty();
    save();
  },
  () => execute(() => compileProject(true)),
  (line, col) => {
    $("cursor").textContent = `Riga ${line} · Colonna ${col}`;
  },
);
const actionButtons = [
  "compile",
  "play",
  "release",
  "restart",
  "runTest",
  "runAllTests",
];
function notice(message) {
  $("toast").textContent = message;
  $("toast").hidden = false;
  clearTimeout(notice.timer);
  notice.timer = setTimeout(() => ($("toast").hidden = true), 7000);
}
async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    return;
  } catch {
    const area = el("textarea", {
      "aria-hidden": "true",
      style: "position:fixed;left:-9999px;top:0",
    });
    area.value = text;
    document.body.append(area);
    area.select();
    const copied = document.execCommand("copy");
    area.remove();
    if (!copied) throw new Error("Copia non disponibile");
  }
}
function setBusy(value) {
  busy = value;
  for (const id of actionButtons) $(id).disabled = value || !ready;
  $("engineStatus").textContent = value
    ? "◌ Operazione in corso…"
    : ready
      ? "● Motore pronto · Esecuzione locale"
      : "◌ Avvio del motore…";
  $("send").disabled = value || !canPlay();
}
function canPlay() {
  return (
    ready &&
    compiledRevision === revision &&
    $("command").dataset.running === "true"
  );
}
async function execute(fn) {
  if (busy) {
    notice("Attendi il completamento dell’operazione oppure interrompila.");
    return;
  }
  setBusy(true);
  try {
    await fn();
  } catch (error) {
    notice(error.message);
  } finally {
    setBusy(false);
  }
}
function save() {
  if (!project) return;
  try {
    localStorage.setItem(storageKey, JSON.stringify(project));
    $("saveStatus").textContent =
      "Salvato in questo browser · " +
      new Date().toLocaleTimeString("it-IT", {
        hour: "2-digit",
        minute: "2-digit",
      });
  } catch {
    $("saveStatus").textContent =
      "Salvataggio non disponibile: scarica un backup";
    notice(
      "Il browser non permette il salvataggio locale. Scarica il progetto per conservarlo.",
    );
  }
}
function stopGame() {
  delete $("command").dataset.running;
  $("command").disabled = true;
  $("send").disabled = true;
}
function dirty() {
  $("testResult").replaceChildren();
  $("trace").replaceChildren(
    el(
      "p",
      { class: "empty" },
      "Sorgente modificato: ricompila prima di osservare le regole.",
    ),
  );
  lastTranscript = "";
  revision++;
  compiledRevision = -1;
  compiled = null;
  diagnostics = [];
  editor.diagnostics([]);
  stopGame();
  $("compileStatus").textContent = "Modifiche da compilare";
  $("errorCount").textContent = "—";
  $("mapCanvas").replaceChildren(
    el(
      "p",
      { class: "empty" },
      "La mappa sarà aggiornata alla prossima compilazione.",
    ),
  );
  mapSVG = "";
  $("diagnostics").replaceChildren(
    el(
      "p",
      { class: "empty" },
      "Sorgente modificato: compila per aggiornare le diagnosi.",
    ),
  );
  $("index").replaceChildren(
    el("p", { class: "empty" }, "Indice da aggiornare."),
  );
}
function validate(p) {
  if (
    !p ||
    p.format !== "locus-project-1" ||
    !p.files ||
    typeof p.files !== "object" ||
    Array.isArray(p.files)
  )
    throw new Error("Il file non è un progetto LOCUS valido.");
  const files = Object.entries(p.files);
  if (files.length < 1 || files.length > 256)
    throw new Error("Sono ammessi da 1 a 256 file.");
  let size = 0;
  for (const [n, t] of files) {
    if (!validName(n) || typeof t !== "string")
      throw new Error("Nome o contenuto di file non valido: " + n);
    size += new TextEncoder().encode(t).length;
  }
  if (size > 2000000) throw new Error("Il progetto supera il limite di 2 MB.");
  if (!Object.hasOwn(p.files, p.entry))
    throw new Error("File principale assente.");
  if (
    p.tests !== undefined &&
    (!Array.isArray(p.tests) ||
      p.tests.length > 100 ||
      p.tests.some(
        (t) =>
          !t ||
          typeof t.name !== "string" ||
          typeof t.commands !== "string" ||
          typeof t.expected !== "string",
      ))
  )
    throw new Error("Copioni del progetto non validi.");
  return {
    ...p,
    title: typeof p.title === "string" ? p.title.slice(0, 100) : "Senza titolo",
    tests: p.tests ?? [],
  };
}
function validName(name) {
  return (
    typeof name === "string" &&
    name.endsWith(".locus") &&
    !/[\\:\x00-\x1f]/.test(name) &&
    !name.startsWith("/") &&
    name.split("/").every((p) => p && p !== "." && p !== "..")
  );
}
function sameFiles(left, right) {
  const leftNames = Object.keys(left).sort();
  const rightNames = Object.keys(right).sort();
  return (
    leftNames.length === rightNames.length &&
    leftNames.every(
      (name, index) => name === rightNames[index] && left[name] === right[name],
    )
  );
}
function setProject(p) {
  project = validate(p);
  editor.clear();
  activeFile = null;
  revision++;
  compiledRevision = -1;
  compiled = null;
  diagnostics = [];
  testIndex = 0;
  lastTranscript = "";
  $("title").value = project.title;
  $("projectHeading").textContent = project.title;
  $("storyByline").hidden = true;
  stopGame();
  $("transcript").replaceChildren(
    el(
      "div",
      { class: "welcome" },
      "Il progetto è pronto. Scegli «Compila e prova» per iniziare.",
    ),
  );
  renderFiles();
  openFile(project.entry);
  renderTests();
  dirty();
  save();
}
function renderFiles() {
  const nav = $("files");
  nav.replaceChildren();
  $("entry").replaceChildren();
  for (const name of Object.keys(project.files)) {
    const b = el(
      "button",
      {
        class: "file" + (name === activeFile ? " active" : ""),
        "data-file": name,
      },
      "≡  " + name,
    );
    b.onclick = () => openFile(name);
    nav.append(b);
    $("entry").append(el("option", { value: name }, name));
  }
  $("entry").value = project.entry;
  $("fileCount").textContent =
    `${Object.keys(project.files).length} file · principale: ${project.entry}`;
}
function openFile(name, line, column) {
  if (!Object.hasOwn(project.files, name)) return;
  activeFile = name;
  editor.open(name, project.files[name]);
  $("activeFile").textContent = name;
  renderFiles();
  editor.diagnostics(diagnostics.filter((d) => d.file === name));
  if (line) editor.go(line, column ?? 1);
}
function tab(id) {
  for (const node of document.querySelectorAll("[data-tab]")) {
    node.classList.toggle("selected", node.dataset.tab === id);
    node.setAttribute("aria-pressed", node.dataset.tab === id);
  }
  for (const node of document.querySelectorAll(".preview-pane>.panel"))
    node.classList.toggle("active", node.id === id);
}
function inspector(id) {
  for (const node of document.querySelectorAll("[data-inspector]"))
    node.classList.toggle("selected", node.dataset.inspector === id);
  for (const node of document.querySelectorAll(".inspector-content"))
    node.classList.toggle("active", node.id === id);
}
for (const b of document.querySelectorAll("[data-tab]"))
  b.onclick = () => tab(b.dataset.tab);
for (const b of document.querySelectorAll("[data-inspector]"))
  b.onclick = () => inspector(b.dataset.inspector);
async function ask(title, text, initial = null) {
  $("dialogTitle").textContent = title;
  $("dialogText").textContent = text;
  $("dialogInput").hidden = initial === null;
  $("dialogLabel").textContent = initial === null ? "" : "Nome / percorso";
  $("dialogInput").value = initial ?? "";
  $("dialog").showModal();
  return new Promise((resolve) => {
    $("dialog").addEventListener(
      "close",
      () =>
        resolve(
          $("dialog").returnValue === "confirm"
            ? initial === null
              ? true
              : $("dialogInput").value.trim()
            : null,
        ),
      { once: true },
    );
  });
}
$("toggleFiles").onclick = () => {
  const open = document.querySelector(".sidebar").classList.toggle("open");
  $("toggleFiles").setAttribute("aria-expanded", String(open));
};
$("entry").onchange = () => {
  project.entry = $("entry").value;
  dirty();
  renderFiles();
  save();
};
$("addFile").onclick = () =>
  execute(async () => {
    const name = await ask(
      "Nuovo file",
      "Usa un nome .locus, eventualmente dentro una cartella.",
      "capitolo.locus",
    );
    if (name === null) return;
    if (!validName(name) || Object.hasOwn(project.files, name))
      throw new Error("Nome non valido o già presente.");
    project.files[name] = "";
    dirty();
    openFile(name);
    save();
  });
$("renameFile").onclick = () =>
  execute(async () => {
    const old = activeFile;
    const name = await ask(
      "Rinomina file",
      "Aggiorna anche le direttive Includi che fanno riferimento al vecchio nome.",
      old,
    );
    if (name === null || name === old) return;
    if (!validName(name) || Object.hasOwn(project.files, name))
      throw new Error("Nome non valido o già presente.");
    project.files[name] = project.files[old];
    delete project.files[old];
    if (project.entry === old) project.entry = name;
    dirty();
    openFile(name);
    save();
  });
$("deleteFile").onclick = () =>
  execute(async () => {
    if (Object.keys(project.files).length === 1)
      throw new Error("Mantieni almeno un file nel progetto.");
    if (
      !(await ask(
        "Elimina file",
        `Eliminare ${activeFile}? Scarica un backup se vuoi conservarlo.`,
      ))
    )
      return;
    delete project.files[activeFile];
    if (project.entry === activeFile)
      project.entry = Object.keys(project.files)[0];
    dirty();
    openFile(project.entry);
    save();
  });
$("backup").onclick = () =>
  download(
    "progetto-locus.json",
    JSON.stringify(project, null, 2),
    "application/json",
  );
$("importButton").onclick = () => $("importFile").click();
$("importFile").onchange = () =>
  execute(async () => {
    const files = [...$("importFile").files];
    $("importFile").value = "";
    if (!files.length) return;
    if (files.some((f) => f.size > 4000000))
      throw new Error("Il file è troppo grande.");
    if (files.length === 1 && files[0].name.endsWith(".json")) {
      const p = validate(JSON.parse(await files[0].text()));
      if (
        await ask(
          "Apri progetto",
          "Sostituire il progetto corrente? Scarica prima un backup per conservarlo.",
        )
      )
        setProject(p);
    } else {
      const changes = { ...project.files };
      for (const f of files) {
        if (!validName(f.name))
          throw new Error("Seleziona solo sorgenti .locus.");
        if (
          Object.hasOwn(changes, f.name) &&
          !(await ask("Sostituisci file", `${f.name} esiste già. Sostituirlo?`))
        )
          continue;
        changes[f.name] = await f.text();
      }
      project = validate({ ...project, files: changes });
      dirty();
      openFile(activeFile);
      save();
    }
  });
$("newProject").onclick = () =>
  execute(async () => {
    if (
      await ask(
        "Nuovo progetto",
        "Il progetto corrente verrà sostituito. Scarica un backup per conservarlo.",
      )
    )
      setProject({
        format: "locus-project-1",
        title: "Una nuova storia",
        entry: "storia.locus",
        files: {
          "storia.locus":
            'Titolo: "Una nuova storia".\nAutore: "Scrivi qui il tuo nome".\n\nLa Sala è una stanza.\nInizia nella "Sala".\nLa Sala ha descrizione "Qui comincia la tua storia.".\n',
        },
        tests: [],
      });
  });
$("demoButton").onclick = () =>
  execute(async () => {
    if (
      await ask(
        "Apri il faro di Selce",
        "Sostituire il progetto corrente con l’esempio completo?",
      )
    )
      setProject(await getJSON("demo.json"));
  });
function showDiagnostics(items) {
  diagnostics = items;
  $("errorCount").textContent = String(items.length);
  $("diagnostics").replaceChildren();
  if (!items.length)
    $("diagnostics").append(
      el(
        "p",
        { class: "empty" },
        "✓ Nessun errore. Il progetto è compilato con il motore LOCUS.",
      ),
    );
  for (const d of items) {
    const row = el("div", { class: "diagnostic" });
    row.append(el("span", { class: "code" }, d.code));
    const details = el("div", { class: "details" });
    const target = el(
      "button",
      {},
      `${d.file} · riga ${d.line}, colonna ${d.column}`,
    );
    target.onclick = () => openFile(d.file, d.line, d.column);
    details.append(
      el("strong", {}, d.title),
      el("p", {}, d.message),
      el("p", {}, d.hint),
      target,
    );
    const help = el("button", {}, "Apri nel manuale ↗");
    help.onclick = () => openManual(d.manual);
    row.append(details, help);
    $("diagnostics").append(row);
  }
  editor.diagnostics(items.filter((d) => d.file === activeFile));
}
async function compileProject(play = false) {
  const rev = revision;
  const snapshot = structuredClone(project);
  const result = await engine.request("compile", { project: snapshot });
  if (rev !== revision) {
    compiledRevision = -1;
    notice("Il sorgente è cambiato durante la compilazione. Compila di nuovo.");
    return false;
  }
  stopGame();
  if (!result.ok) {
    compiled = null;
    compiledRevision = -1;
    showDiagnostics(result.diagnostics ?? []);
    $("compileStatus").textContent = "Compilazione non riuscita";
    inspector("diagnostics");
    if (result.message) throw new Error(result.message);
    if (result.diagnostics?.length) {
      const d = result.diagnostics[0];
      openFile(d.file, d.line, d.column);
    }
    return false;
  }
  compiled = result;
  compiledRevision = rev;
  showDiagnostics([]);
  $("compileStatus").textContent =
    `${result.entities} entità · ${result.actions ?? 0} azioni autore · ${result.rules} regole · compilato`;
  if (result.title) {
    project.title = result.title;
    $("title").value = result.title;
    $("projectHeading").textContent = result.title;
    save();
  }
  $("storyByline").textContent = result.author ? `di ${result.author}` : "";
  $("storyByline").hidden = !result.author;
  showMap(result.map);
  zoom = 1;
  renderIndex(result.ir);
  if (play) {
    await restart();
    tab("game");
  }
  return true;
}
function showMap(data) {
  if (!data) return;
  if (compiled) compiled.map = data;
  mapSVG = drawMap(data);
  $("mapCanvas").innerHTML = mapSVG;
  $("mapSummary").textContent =
    `${data.rooms.length} luoghi · ${data.links.length} collegamenti · ${data.doors.length} porte`;
}
function renderIndex(ir) {
  const types = new Map((ir.types ?? []).map((item) => [item.id, item]));
  function typePath(typeId) {
    const labels = [];
    const visited = new Set();
    let current = typeId;
    while (current && !visited.has(current)) {
      visited.add(current);
      const item = types.get(current);
      labels.push(item?.label ?? current.split(".").at(-1));
      current = item?.parent_id;
    }
    return labels.reverse().join(" › ");
  }
  const table = el("table", { class: "data" });
  const head = el("tr");
  for (const s of ["Entità", "Tipo", "Proprietà"]) head.append(el("th", {}, s));
  table.append(head);
  for (const entity of ir.entities) {
    const row = el("tr");
    const props = ir.properties
      .filter((p) => p.entity_id === entity.id)
      .map((p) => `${p.property_id.split(".").at(-1)}: ${String(p.value)}`)
      .join(" · ");
    for (const t of [entity.label, typePath(entity.type_id), props])
      row.append(el("td", {}, t));
    table.append(row);
  }
  const content = [table];
  if ((ir.tables ?? []).length) {
    content.push(el("h3", {}, "Tabelle"));
    for (const data of ir.tables) {
      content.push(el("h4", {}, data.label));
      const grid = el("table", { class: "data" });
      const tableHead = el("tr");
      for (const column of data.columns)
        tableHead.append(
          el("th", {}, `${column.label} · ${column.value_kind}`),
        );
      grid.append(tableHead);
      for (const values of data.rows) {
        const row = el("tr");
        for (const value of values) row.append(el("td", {}, String(value)));
        grid.append(row);
      }
      if (!data.rows.length) {
        const row = el("tr");
        row.append(
          el("td", { colspan: String(data.columns.length) }, "Nessuna riga"),
        );
        grid.append(row);
      }
      content.push(grid);
    }
  }
  if ((ir.actions ?? []).length) {
    content.push(el("h3", {}, "Azioni definite dall'autore"));
    const actions = el("table", { class: "data" });
    const actionHead = el("tr");
    for (const label of ["Azione", "Comando", "Oggetti"])
      actionHead.append(el("th", {}, label));
    actions.append(actionHead);
    for (const action of ir.actions) {
      const row = el("tr");
      const argumentsText = action.target_type_id
        ? action.indirect_type_id
          ? `${typePath(action.target_type_id)} + ${typePath(action.indirect_type_id)} (separatori ${action.separators.map((item) => `«${item}»`).join(", ")})`
          : typePath(action.target_type_id)
        : "nessun oggetto";
      const commandsText = action.commands
        .map((item) => `«${item}»`)
        .join(", ");
      for (const value of [action.label, commandsText, argumentsText])
        row.append(el("td", {}, value));
      actions.append(row);
    }
    content.push(actions);
  }
  $("index").replaceChildren(...content);
}
function showTrace(trace) {
  $("trace").replaceChildren();
  if (!trace.length) {
    $("trace").append(
      el(
        "p",
        { class: "empty" },
        "Nessuna regola autore considerata per questa azione.",
      ),
    );
    return;
  }
  const table = el("table", { class: "data" });
  const h = el("tr");
  for (const s of ["Regola", "Fase", "Priorità", "Esito", "Sorgente"])
    h.append(el("th", {}, s));
  table.append(h);
  for (const t of trace) {
    const row = el("tr");
    for (const v of [t.name, t.phase, String(t.priority), t.outcome])
      row.append(el("td", {}, v));
    const cell = el("td");
    const b = el("button", {}, `${t.origin.source}:${t.origin.line}`);
    b.onclick = () => openFile(t.origin.source, t.origin.line, t.origin.column);
    cell.append(b);
    row.append(cell);
    table.append(row);
  }
  $("trace").append(table);
}
function appendOutput(result, command) {
  if (command)
    $("transcript").append(
      el("p", { class: "player-command" }, "› " + command),
    );
  $("transcript").append(el("div", { class: "story-output" }, result.text));
  $("transcript").scrollTop = $("transcript").scrollHeight;
  showTrace(result.trace);
  showMap(result.map);
  if (compiled && result.properties) {
    compiled.ir.properties = result.properties;
    compiled.ir.tables = result.tables ?? compiled.ir.tables;
    renderIndex(compiled.ir);
  }
  if (result.ended) stopGame();
}
async function restart() {
  if (compiledRevision !== revision) {
    if (!(await compileProject(false))) return;
  }
  const result = await engine.request("restart");
  if (!result.ok) throw new Error(result.message);
  $("transcript").replaceChildren();
  appendOutput(result);
  $("command").disabled = false;
  $("command").dataset.running = "true";
  $("command").focus();
}
$("compile").onclick = () => execute(() => compileProject());
$("play").onclick = () => execute(() => compileProject(true));
$("restart").onclick = () => execute(restart);
$("cancel").onclick = () => {
  engine.abort();
  compiledRevision = -1;
  compiled = null;
  stopGame();
  ready = false;
  setBusy(false);
  engine.request("ready").then(() => {
    ready = true;
    setBusy(false);
    notice(
      "Motore riavviato. Il sorgente è conservato: ricompila per continuare.",
    );
  });
};
$("commandForm").onsubmit = (e) => {
  e.preventDefault();
  if (!canPlay()) return;
  const command = $("command").value.trim();
  if (!command) return;
  execute(async () => {
    const result = await engine.request("command", { command });
    if (!result.ok) throw new Error(result.message);
    appendOutput(result, command);
    $("command").value = "";
  });
};
$("exportMap").onclick = () => {
  if (!mapSVG) return notice("Compila prima il progetto.");
  download("mappa-locus.svg", mapSVG, "image/svg+xml");
};
$("mapJSON").onclick = () => {
  if (!compiled) return notice("Compila prima il progetto.");
  download(
    "mappa-locus.json",
    JSON.stringify(compiled.map, null, 2),
    "application/json",
  );
};
function mapZoom(delta) {
  zoom = Math.max(0.5, Math.min(3, zoom + delta));
  const svg = $("mapCanvas").querySelector("svg");
  if (svg) {
    svg.style.width = Number(svg.getAttribute("width")) * zoom + "px";
    svg.style.minWidth = "0";
  }
}
$("zoomIn").onclick = () => mapZoom(0.25);
$("zoomOut").onclick = () => mapZoom(-0.25);
function renderTests() {
  const list = project.tests;
  $("testSelect").replaceChildren();
  if (!list.length)
    $("testSelect").append(el("option", {}, "Nessun copione: crea un test"));
  list.forEach((t, i) =>
    $("testSelect").append(el("option", { value: i }, t.name)),
  );
  testIndex = Math.min(testIndex, Math.max(0, list.length - 1));
  $("testSelect").value = String(testIndex);
  const t = list[testIndex];
  $("testName").value = t?.name ?? "";
  $("testCommands").value = t?.commands ?? "";
  $("testExpected").value = t?.expected ?? "";
  for (const id of ["testName", "testCommands", "testExpected"])
    $(id).disabled = !t;
}
$("testSelect").onchange = () => {
  testIndex = Number($("testSelect").value);
  renderTests();
};
for (const [id, key] of [
  ["testName", "name"],
  ["testCommands", "commands"],
  ["testExpected", "expected"],
])
  $(id).oninput = () => {
    if (project.tests[testIndex]) {
      project.tests[testIndex][key] = $(id).value;
      if (key === "name") $("testSelect").options[testIndex].text = $(id).value;
      save();
    }
  };
$("addTest").onclick = () => {
  project.tests.push({
    name: "Nuovo test",
    commands: "guarda\n",
    expected: "",
  });
  testIndex = project.tests.length - 1;
  renderTests();
  save();
};
$("deleteTest").onclick = () =>
  execute(async () => {
    if (
      project.tests[testIndex] &&
      (await ask("Elimina test", "Eliminare il copione selezionato?"))
    ) {
      project.tests.splice(testIndex, 1);
      renderTests();
      save();
    }
  });
async function runTests(all) {
  if (compiledRevision !== revision && !(await compileProject())) return;
  const list = structuredClone(
    all ? project.tests : project.tests.slice(testIndex, testIndex + 1),
  );
  if (!list.length) throw new Error("Crea almeno un copione.");
  $("testResult").replaceChildren();
  for (const t of list) {
    const result = await engine.request("test", {
      commands: t.commands.split(/\r?\n/).filter((s) => s.trim()),
      expected: t.expected || null,
    });
    if (!result.ok) throw new Error(result.message);
    lastTranscript = result.actual;
    let description =
      result.passed === true
        ? "SUPERATO"
        : result.passed === false
          ? "NON SUPERATO"
          : "ESPLORATIVO · nessun confronto";
    description = `${t.name}\n${description} · ${result.executed}/${result.requested} comandi eseguiti`;
    if (result.passed === false) {
      const expected = t.expected.replace(/\r\n/g, "\n").split("\n"),
        actual = result.actual.split("\n");
      const i = Array.from(
        { length: Math.max(expected.length, actual.length) },
        (_, i) => i,
      ).find((i) => expected[i] !== actual[i]);
      description += `\nPrima differenza alla riga ${i + 1}\nAtteso: ${expected[i] ?? "(fine)"}\nOttenuto: ${actual[i] ?? "(fine)"}`;
    }
    const box = el(
      "div",
      { class: "result" + (result.passed === false ? " failed" : "") },
      description,
    );
    const details = el("details");
    details.append(
      el("summary", {}, "Transcript effettivo"),
      el("pre", {}, result.actual),
    );
    box.append(details);
    $("testResult").append(box);
  }
  tab("tests");
}
$("runTest").onclick = () => execute(() => runTests(false));
$("runAllTests").onclick = () => execute(() => runTests(true));
$("downloadTranscript").onclick = () => {
  if (!lastTranscript) return notice("Esegui prima un test.");
  download("transcript.txt", lastTranscript, "text/plain;charset=utf-8");
};
function openManual(path) {
  if (!manual[path]) {
    notice("Capitolo non disponibile nel manuale incorporato.");
    return;
  }
  currentManual = path;
  $("manualSearch").value = "";
  renderManualOptions();
  $("manualSelect").value = path;
  $("manualContent").innerHTML = DOMPurify.sanitize(marked.parse(manual[path]));
  for (const a of $("manualContent").querySelectorAll("a")) {
    const href = a.getAttribute("href");
    if (href && !/^(https?:|#|mailto:)/.test(href)) {
      const target = new URL(
        href,
        "https://manual.local/" + path,
      ).pathname.slice(1);
      a.onclick = (e) => {
        e.preventDefault();
        openManual(decodeURIComponent(target));
      };
    } else if (href?.startsWith("http")) {
      a.target = "_blank";
      a.rel = "noopener noreferrer";
    }
  }
  for (const pre of $("manualContent").querySelectorAll("pre")) {
    const button = el(
      "button",
      { class: "copy-code", type: "button" },
      "Copia codice",
    );
    button.onclick = async () => {
      try {
        await copyText(pre.textContent);
        button.textContent = "Copiato ✓";
        setTimeout(() => (button.textContent = "Copia codice"), 1800);
      } catch {
        notice("Copia non disponibile: seleziona il codice nel riquadro.");
      }
    };
    pre.before(button);
  }
  tab("manual");
}
function renderManualOptions(filter = "") {
  const select = $("manualSelect");
  select.replaceChildren();
  for (const [path, text] of Object.entries(manual)) {
    if (filter && !text.toLowerCase().includes(filter.toLowerCase())) continue;
    const title = text.split("\n")[0].replace(/^#+\s*/, "");
    select.append(el("option", { value: path }, title));
  }
  select.value = currentManual;
}
$("manualSelect").onchange = () => openManual($("manualSelect").value);
$("manualSearch").oninput = () => renderManualOptions($("manualSearch").value);
$("manualButton").onclick = () => openManual("docs/manuale/guida-autore.md");
$("guideButton").onclick = () => openManual("docs/tutorial/README.md");
$("commandGuideButton").onclick = () =>
  openManual("docs/tutorial/05-comandi-e-nomi.md");
$("languageButton").onclick = () => openManual("LANGUAGE_SPEC.md");
$("release").onclick = () =>
  execute(async () => {
    if (compiledRevision !== revision && !(await compileProject())) return;
    if (!compiled.map.rooms.length)
      throw new Error("La release narrativa richiede almeno una stanza.");
    notice("Preparazione della release completa: runtime, storia e giocatore…");
    const snapshot = structuredClone(project),
      archive = {};
    const assets = await getJSON("release-assets.json");
    for (const name of assets) {
      const r = await fetch(name);
      if (!r.ok) throw new Error("Risorsa della release assente: " + name);
      archive[name === "player.html" ? "index.html" : name] = new Uint8Array(
        await r.arrayBuffer(),
      );
    }
    archive["project.json"] = strToU8(JSON.stringify(snapshot));
    archive["LEGGIMI.txt"] = strToU8(
      "RELEASE LOCUS\n\nCarica tutti i file estratti su un sito statico HTTPS e apri index.html.\nNon aprire index.html con file://: il runtime richiede HTTP.\nIn locale, dalla cartella estratta: python -m http.server 8000\nPoi apri http://localhost:8000. Python serve solo come server locale.\nIl giocatore sul sito non richiede Python installato.\nRuntime incluso: nessun CDN esterno. Browser moderno con WebAssembly richiesto.\nI sorgenti della storia sono inclusi in project.json; non sono segreti.\nLeggi LICENZE.txt per le dipendenze. Questa anteprima non genera eseguibili nativi.\n",
    );
    download(
      "release-locus.zip",
      zipSync(archive, { level: 6 }),
      "application/zip",
    );
    notice(
      "Release pronta. Estrai lo ZIP e pubblica tutti i file su un sito statico.",
    );
  });
window.addEventListener("beforeunload", () => save());
async function initialize() {
  setBusy(false);
  manual = await getJSON("manual.json");
  renderManualOptions();
  openManual("docs/manuale/guida-autore.md");
  tab("game");
  let saved;
  try {
    saved = localStorage.getItem(storageKey);
    if (saved) {
      project = validate(JSON.parse(saved));
      if (
        project.title === "Il faro di Selce" &&
        project.entry === "04_faro.locus"
      ) {
        const legacy = await getJSON("legacy-demo.json");
        if (
          sameFiles(project.files, legacy.files) &&
          JSON.stringify(project.tests) === JSON.stringify(legacy.tests)
        ) {
          project = validate(await getJSON("demo.json"));
          notice(
            "L’esempio del faro è stato aggiornato al nuovo sorgente unico.",
          );
        }
      }
    }
  } catch {
    notice("Backup locale non valido: carico l’esempio.");
  }
  setProject(project ?? (await getJSON("demo.json")));
  const result = await engine.request("ready");
  if (!result.ok) throw new Error(result.message);
  ready = true;
  setBusy(false);
  await execute(() => compileProject());
}
initialize().catch((error) => {
  notice(error.message);
  $("engineStatus").textContent =
    "Motore non disponibile · riprova con Interrompi";
});
