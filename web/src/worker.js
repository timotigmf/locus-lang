import { loadPyodide } from "./runtime/pyodide.mjs";
const ready = (async () => {
  const py = await loadPyodide({
    indexURL: new URL("./runtime/", import.meta.url).href,
  });
  const response = await fetch(new URL("./locus-python.zip", import.meta.url));
  if (!response.ok) throw new Error("Pacchetto LOCUS non disponibile.");
  py.unpackArchive(await response.arrayBuffer(), "zip", {
    extractDir: "/home/pyodide",
  });
  py.runPython("from locus.studio import Studio\n_studio = Studio()");
  return py;
})();
let queue = Promise.resolve();
self.onmessage = ({ data }) => {
  queue = queue.then(async () => {
    try {
      const py = await ready;
      if (data.operation === "ready") {
        postMessage({ id: data.id, result: { ok: true } });
        return;
      }
      py.globals.set("_request", JSON.stringify(data));
      const result = JSON.parse(py.runPython("_studio.dispatch(_request)"));
      postMessage({ id: data.id, result });
    } catch (error) {
      postMessage({
        id: data.id,
        result: { ok: false, message: "Errore del motore: " + error.message },
      });
    }
  });
};
