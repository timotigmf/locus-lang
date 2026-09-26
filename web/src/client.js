export class Engine {
  constructor() {
    this.pending = new Map();
    this.count = 0;
    this.start();
  }
  start() {
    this.worker = new Worker(new URL("worker.js", document.baseURI), {
      type: "module",
    });
    this.worker.onmessage = ({ data }) => {
      const p = this.pending.get(data.id);
      if (p) {
        clearTimeout(p.timer);
        this.pending.delete(data.id);
        p.resolve(data.result);
      }
    };
    this.worker.onerror = () =>
      this.abort(
        "Impossibile avviare il motore. Ricarica la pagina o verifica i file del sito.",
      );
  }
  abort(message = "Operazione annullata. Ricompila il progetto.") {
    this.worker.terminate();
    for (const p of this.pending.values()) {
      clearTimeout(p.timer);
      p.reject(new Error(message));
    }
    this.pending.clear();
    this.start();
  }
  request(operation, data = {}) {
    return new Promise((resolve, reject) => {
      const id = ++this.count;
      const timer = setTimeout(
        () =>
          this.abort("Tempo massimo superato. Il motore è stato riavviato."),
        120000,
      );
      this.pending.set(id, { resolve, reject, timer });
      this.worker.postMessage({ id, operation, ...data });
    });
  }
}
export function download(name, data, type = "application/octet-stream") {
  const a = document.createElement("a");
  const url = URL.createObjectURL(new Blob([data], { type }));
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 3000);
}
export function el(tag, attributes = {}, text) {
  const n = document.createElement(tag);
  for (const [key, value] of Object.entries(attributes))
    n.setAttribute(key, value);
  if (text !== undefined) n.textContent = text;
  return n;
}
export async function getJSON(file) {
  const r = await fetch(file);
  if (!r.ok) throw new Error("Impossibile caricare " + file);
  return r.json();
}
