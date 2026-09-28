import { Engine, getJSON, el } from "./client.js";
const $ = (id) => document.getElementById(id),
  engine = new Engine();
let ready = false,
  busy = false,
  project;
function lock(value) {
  busy = value;
  $("send").disabled = value || !ready;
  $("command").disabled = value || !ready;
  $("restart").disabled = value;
}
function append(result, command) {
  if (command)
    $("transcript").append(
      el("p", { class: "player-command" }, "› " + command),
    );
  $("transcript").append(el("div", { class: "story-output" }, result.text));
  renderMedia(result.media ?? []);
  $("transcript").scrollTop = $("transcript").scrollHeight;
  ready = !result.ended;
  $("status").textContent = ready ? "Storia in corso" : "Sessione terminata";
}
function renderMedia(items) {
  const stage = $("mediaStage");
  stage.replaceChildren();
  for (const item of items) {
    const encoded = project.assets?.[item.path];
    const source = encoded
      ? `data:${item.media_type};base64,${encoded}`
      : item.path;
    if (item.kind === "immagine") {
      const figure = el("figure");
      figure.append(
        el("img", { src: source, alt: item.alternative_text }),
        el("figcaption", {}, item.alternative_text),
      );
      stage.append(figure);
    } else if (item.kind === "suono") {
      stage.append(
        el("span", { class: "media-label" }, item.alternative_text),
        el("audio", {
          controls: "",
          preload: "metadata",
          src: source,
        }),
      );
    }
  }
  stage.hidden = !items.length;
}
async function run(fn) {
  if (busy) return;
  lock(true);
  try {
    await fn();
  } catch (e) {
    $("status").textContent = e.message;
  } finally {
    lock(false);
  }
}
async function restart() {
  const r = await engine.request("restart");
  if (!r.ok) throw new Error(r.message);
  $("transcript").replaceChildren();
  append(r);
}
$("restart").onclick = () => run(restart);
$("commandForm").onsubmit = (e) => {
  e.preventDefault();
  if (!ready) return;
  const command = $("command").value.trim();
  if (!command) return;
  run(async () => {
    const r = await engine.request("command", { command });
    if (!r.ok) throw new Error(r.message);
    append(r, command);
    $("command").value = "";
  });
};
run(async () => {
  project = await getJSON("project.json");
  $("storyTitle").textContent = project.title;
  document.title = project.title;
  const r = await engine.request("compile", { project });
  if (!r.ok)
    throw new Error(
      r.diagnostics?.map((d) => d.message).join("\n") ?? r.message,
    );
  await restart();
});
