import { EditorView, keymap } from "@codemirror/view";
import { EditorState } from "@codemirror/state";
import { basicSetup } from "codemirror";
import {
  StreamLanguage,
  syntaxHighlighting,
  HighlightStyle,
} from "@codemirror/language";
import { tags } from "@lezer/highlight";
import { autocompletion } from "@codemirror/autocomplete";
import { setDiagnostics } from "@codemirror/lint";
const words = [
  "Titolo",
  "Autore",
  "Comprendi",
  "Azione",
  "Tabella",
  "Colonna",
  "Riga",
  "Dialogo",
  "Nodo",
  "Scelta",
  "Scena",
  "Inizio",
  "Punti",
  "dal",
  "al",
  "turno",
  "veicolo",
  "valuta",
  "mercante",
  "merce",
  "prodotto",
  "dice",
  "porta",
  "termina",
  "comando",
  "sinonimo",
  "separatore",
  "senza",
  "oggetti",
  "su",
  "come",
  "La",
  "Il",
  "Lo",
  "è",
  "una",
  "un",
  "uno",
  "tipo",
  "scenario",
  "visibile",
  "elenco",
  "testi",
  "numeri",
  "logici",
  "di",
  "nella",
  "nel",
  "della",
  "ha",
  "collega",
  "crea",
  "rimuovi",
  "relazione",
  "da",
  "apre",
  "vende",
  "Includi",
  "Inizia",
  "Regola",
  "per",
  "fase",
  "prima",
  "invece",
  "verifica",
  "esegui",
  "dopo",
  "descrivi",
  "quando",
  "priorità",
  "non",
  "e",
  "o",
  "dì",
  "imposta",
  "aumenta",
  "diminuisci",
  "aggiungi",
  "contiene",
  "riga",
  "tabella",
  "continua",
  "interrompi",
  "fallisci",
  "sostituisci",
  "restituisci",
  "Fine",
  "regola",
];
const language = StreamLanguage.define({
  token(stream) {
    if (stream.eatSpace()) return null;
    if (stream.match(/"(?:[^"\\]|\\.)*"/)) return "string";
    if (stream.match(/-?\d+/)) return "number";
    if (stream.match(/[\p{L}\p{M}]+/u)) {
      const word = stream.current();
      if (["vero", "falso"].includes(word)) return "bool";
      return words.some((w) => w.toLowerCase() === word.toLowerCase())
        ? "keyword"
        : null;
    }
    stream.next();
    return "punctuation";
  },
});
const translations = {
  Find: "Cerca",
  Replace: "Sostituisci",
  "Replace all": "Sostituisci tutto",
  next: "successivo",
  previous: "precedente",
  all: "tutti",
  "match case": "distingui maiuscole",
  regexp: "espressione regolare",
  "by word": "parola intera",
  close: "chiudi",
  "Go to line": "Vai alla riga",
  go: "vai",
  "Fold line": "Comprimi riga",
  "Unfold line": "Espandi riga",
  to: "a",
  "folded code": "codice compresso",
  unfold: "espandi",
  "Folded lines": "Righe compresse",
  "Unfolded lines": "Righe espanse",
  Diagnostics: "Diagnostica",
  "No diagnostics": "Nessuna diagnosi",
  "Control character": "Carattere di controllo",
};
export function makeEditor(parent, onChange, onRun, onCursor) {
  const extensions = [
    basicSetup,
    language,
    syntaxHighlighting(
      HighlightStyle.define([
        { tag: tags.keyword, color: "#32796c", fontWeight: "600" },
        { tag: tags.string, color: "#967034" },
        { tag: tags.number, color: "#9a5180" },
        { tag: tags.bool, color: "#9a5180" },
      ]),
    ),
    EditorState.phrases.of(translations),
    EditorView.lineWrapping,
    EditorView.contentAttributes.of({
      "aria-label": "Codice LOCUS",
      spellcheck: "false",
    }),
    autocompletion({
      override: [
        (ctx) => {
          const word = ctx.matchBefore(/[\p{L}]+/u);
          if (!word && !ctx.explicit) return null;
          return {
            from: word?.from ?? ctx.pos,
            options: words.map((label) => ({ label, type: "keyword" })),
          };
        },
      ],
    }),
    keymap.of([
      {
        key: "Mod-Enter",
        run: () => {
          onRun();
          return true;
        },
      },
    ]),
    EditorView.updateListener.of((u) => {
      if (u.docChanged) onChange(u.state.doc.toString());
      if (u.selectionSet || u.docChanged) {
        const pos = u.state.selection.main.head;
        const line = u.state.doc.lineAt(pos);
        onCursor(line.number, pos - line.from + 1);
      }
    }),
  ];
  const states = new Map();
  let current;
  const view = new EditorView({
    state: EditorState.create({ doc: "", extensions }),
    parent,
  });
  return {
    view,
    open(name, text) {
      if (current) states.set(current, view.state);
      current = name;
      const saved = states.get(name);
      view.setState(
        saved && saved.doc.toString() === text
          ? saved
          : EditorState.create({ doc: text, extensions }),
      );
    },
    clear() {
      states.clear();
      current = null;
    },
    diagnostics(items) {
      const text = view.state.doc.toString();
      const offset = (n) => Array.from(text).slice(0, n).join("").length;
      view.dispatch(
        setDiagnostics(
          view.state,
          items.map((d) => ({
            from: Math.min(offset(d.start), text.length),
            to: Math.min(
              Math.max(offset(d.start) + 1, offset(d.end)),
              text.length,
            ),
            severity: "error",
            message: `${d.code} · ${d.message}`,
          })),
        ),
      );
    },
    go(line, column) {
      const l = view.state.doc.line(
        Math.min(Math.max(line, 1), view.state.doc.lines),
      );
      const pos = Math.min(
        l.to,
        l.from +
          Array.from(l.text)
            .slice(0, column - 1)
            .join("").length,
      );
      view.dispatch({
        selection: { anchor: pos },
        effects: EditorView.scrollIntoView(pos, { y: "center" }),
      });
      view.focus();
    },
  };
}
