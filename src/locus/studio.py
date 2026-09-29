"""Adattatore JSON dello Studio: compilatore reale, filesystem temporaneo isolato."""

import base64
import binascii
import json
from dataclasses import asdict
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from typing import Any

from locus.diagnostics import CompileError
from locus.ir import ProgramIR
from locus.media import (
    MAX_PROJECT_RESOURCE_BYTES,
    MAX_RESOURCE_BYTES,
    MAX_RESOURCES,
    MEDIA_FORMATS,
    valid_media_content,
    valid_resource_path,
)
from locus.player import Intent, parse_command
from locus.runtime import World, has_type, instantiate
from locus.stdlib import (
    CURRENCY,
    EAST,
    INSIDE,
    MERCHANDISE,
    MERCHANT,
    NORTH,
    NORTHEAST,
    ROOM,
    SIDE_A,
    SIDE_B,
    SOUTHEAST,
    UP,
    VEHICLE,
)
from locus.stdlib.authoring import compile_story_file
from locus.stdlib.game import Session, Transition, start, step
from locus.stdlib.render import render

# Collegamenti relativi al manuale incorporato nella distribuzione web.
_ERROR_HELP = {
    "E001": (
        "Carattere non riconosciuto",
        "Controlla accenti, virgolette e simboli.",
        "LANGUAGE_SPEC.md",
    ),
    "E002": (
        "Sintassi incompleta",
        "Controlla la parola attesa e la punteggiatura indicata.",
        "LANGUAGE_SPEC.md",
    ),
    "E003": (
        "Stringa non valida",
        "Chiudi le virgolette; usa solo gli escape supportati.",
        "docs/linguaggio/milestone-2.md",
    ),
    "E004": (
        "Intero troppo lungo",
        "Usa un intero di non oltre 1000 cifre.",
        "docs/linguaggio/milestone-2.md",
    ),
    "E101": (
        "Nome duplicato",
        "Dichiara ogni entità una sola volta, anche fra moduli.",
        "docs/linguaggio/milestone-4.md",
    ),
    "E102": (
        "Tipo sconosciuto",
        "Controlla il nome oppure dichiaralo con: Un nome è un tipo di cosa.",
        "docs/linguaggio/tipi-autore.md",
    ),
    "E103": (
        "Riferimento non dichiarato",
        "Controlla il nome e l'inclusione del file che lo dichiara.",
        "docs/linguaggio/milestone-4.md",
    ),
    "E113": (
        "Tipo duplicato",
        "Scegli un nome nuovo: anche i tipi della libreria sono già dichiarati.",
        "docs/linguaggio/tipi-autore.md",
    ),
    "E114": (
        "Ciclo fra tipi",
        "Ogni catena deve terminare in un tipo esistente senza tornare indietro.",
        "docs/linguaggio/tipi-autore.md",
    ),
    "E115": (
        "Tabella duplicata",
        "Scegli un nome univoco per ogni tabella del progetto.",
        "docs/linguaggio/tabelle-tipate.md",
    ),
    "E116": (
        "Schema di tabella non valido",
        "Dichiara da 1 a 64 colonne con nomi univoci.",
        "docs/linguaggio/tabelle-tipate.md",
    ),
    "E117": (
        "Riga di tabella non valida",
        "Fornisci un valore del tipo corretto per ogni colonna.",
        "docs/linguaggio/tabelle-tipate.md",
    ),
    "E118": (
        "Dialogo duplicato",
        "Usa un nome univoco e un solo dialogo per ciascuna persona.",
        "docs/linguaggio/dialoghi-strutturati.md",
    ),
    "E119": (
        "Grafo del dialogo non valido",
        "Controlla nodi, scelte, destinazioni e raggiungibilità.",
        "docs/linguaggio/dialoghi-strutturati.md",
    ),
    "E120": (
        "Partecipante del dialogo non valido",
        "Dichiara il partecipante come persona e verifica il suo nome.",
        "docs/linguaggio/dialoghi-strutturati.md",
    ),
    "E121": (
        "Scena duplicata",
        "Usa un nome univoco per ogni scena del progetto.",
        "docs/linguaggio/scene-tempo-punteggio.md",
    ),
    "E122": (
        "Scena non valida",
        "Controlla turni, testi obbligatori e punti assegnati.",
        "docs/linguaggio/scene-tempo-punteggio.md",
    ),
    "E123": (
        "Veicolo non valido",
        "Colloca ogni veicolo direttamente in una stanza.",
        "docs/linguaggio/veicoli.md",
    ),
    "E124": (
        "Commercio non valido",
        "Controlla valuta, saldo e prezzi positivi delle merci.",
        "docs/linguaggio/denaro-e-acquisti.md",
    ),
    "E125": (
        "Mercante o scorta non validi",
        "Controlla valuta, cassa, rivendita, venditore e posizione della merce.",
        "docs/linguaggio/mercanti-e-vendita.md",
    ),
    "E126": (
        "Risorsa multimediale non valida",
        "Controlla percorso, formato, presenza e dimensione del file nel progetto.",
        "docs/linguaggio/risorse-multimediali.md",
    ),
    "E310": (
        "Azione duplicata",
        "Scegli un nome che non appartenga già alla storia o alla libreria.",
        "docs/linguaggio/azioni-autore.md",
    ),
    "E311": (
        "Forma di comando non valida",
        "Usa da una a quattro parole e rimuovi duplicati o prefissi ambigui.",
        "docs/linguaggio/separatori-multiparola.md",
    ),
    "E312": (
        "Relazione dinamica non valida",
        "Usa una direzione cardinale dinamica fra due stanze distinte.",
        "docs/linguaggio/relazioni-dinamiche.md",
    ),
    "E313": (
        "Elemento di elenco non valido",
        "Controlla che la proprietà sia un elenco e che l'elemento abbia il tipo dichiarato.",
        "docs/linguaggio/liste-tipate.md",
    ),
    "E314": (
        "Operazione di tabella non valida",
        "Controlla nome della tabella, numero dei valori e tipi delle colonne.",
        "docs/linguaggio/tabelle-tipate.md",
    ),
    "E201": (
        "Mondo incoerente",
        "Verifica estremi e collegamenti della porta.",
        "docs/linguaggio/milestone-2.md",
    ),
    "E408": (
        "Metadato ripetuto",
        "Dichiara Titolo e Autore una sola volta nell'intero progetto.",
        "docs/linguaggio/metadati-vocabolario.md",
    ),
    "E409": (
        "Sinonimo in conflitto",
        "Scegli un alias che non sia già un nome o un altro sinonimo.",
        "docs/linguaggio/metadati-vocabolario.md",
    ),
}


def diagnostic(error: CompileError, root: Path) -> dict[str, Any]:
    source = error.span.source
    try:
        source = str(Path(source).relative_to(root)).replace("\\", "/")
    except ValueError:
        pass
    code = error.code
    default = (
        "Errore semantico",
        "Consulta il vincolo indicato nel messaggio.",
        "LANGUAGE_SPEC.md",
    )
    if code.startswith("E3"):
        default = (
            "Regola non valida",
            "Controlla fase, azione, tipi e istruzioni della regola.",
            "docs/linguaggio/milestone-3.md",
        )
    elif code.startswith("E4"):
        default = (
            "Progetto non valido",
            "Controlla percorsi, inclusioni e punto iniziale.",
            "docs/linguaggio/milestone-4.md",
        )
    elif code.startswith("E1") and code not in _ERROR_HELP:
        default = (
            "Vincolo del modello",
            "Controlla relazioni e valori delle proprietà.",
            "docs/linguaggio/milestone-2.md",
        )
    title, hint, manual = _ERROR_HELP.get(code, default)
    return {
        "code": code,
        "title": title,
        "message": error.message.replace(str(root) + "/", ""),
        "file": source,
        "line": error.span.line,
        "column": error.span.column,
        "start": error.span.start,
        "end": error.span.end,
        "hint": hint,
        "manual": manual,
    }


def validate_project(project: Any) -> dict[str, Any]:
    if not isinstance(project, dict) or project.get("format") != "locus-project-1":
        raise ValueError("Formato del progetto non valido: atteso locus-project-1.")
    files = project.get("files")
    if not isinstance(files, dict) or not 1 <= len(files) <= 256:
        raise ValueError("Un progetto deve contenere da 1 a 256 file.")
    size = 0
    for name, source in files.items():
        if (
            not isinstance(name, str)
            or not name
            or "\\" in name
            or ":" in name
            or "\x00" in name
            or any(c in name for c in "\r\n")
            or PurePosixPath(name).is_absolute()
            or any(part in {"", ".", ".."} for part in name.split("/"))
            or not name.endswith(".locus")
            or not isinstance(source, str)
        ):
            raise ValueError(
                "I file devono avere percorsi relativi .locus senza '..' e testo UTF-8."
            )
        size += len(source.encode("utf-8"))
    if size > 2_000_000:
        raise ValueError("Progetto troppo grande: massimo 2 MB di sorgenti.")
    assets = project.get("assets", {})
    if not isinstance(assets, dict) or len(assets) > MAX_RESOURCES:
        raise ValueError(f"Un progetto ammette al massimo {MAX_RESOURCES} risorse.")
    asset_size = 0
    for name, encoded in assets.items():
        if (
            not isinstance(name, str)
            or not valid_resource_path(name)
            or PurePosixPath(name).suffix.casefold() not in MEDIA_FORMATS
            or not isinstance(encoded, str)
        ):
            raise ValueError("Percorso, formato o contenuto della risorsa non valido.")
        try:
            content = base64.b64decode(encoded, validate=True)
        except (ValueError, binascii.Error) as error:
            raise ValueError(f"La risorsa {name} non contiene dati Base64 validi.") from error
        if len(content) > MAX_RESOURCE_BYTES:
            raise ValueError(f"La risorsa {name} supera 5 MB.")
        media_type = MEDIA_FORMATS[PurePosixPath(name).suffix.casefold()]
        if not valid_media_content(media_type, content[:12]):
            raise ValueError(f"Il contenuto della risorsa {name} non corrisponde al formato.")
        asset_size += len(content)
    if asset_size > MAX_PROJECT_RESOURCE_BYTES:
        raise ValueError("Le risorse del progetto superano 20 MB.")
    if project.get("entry") not in files:
        raise ValueError("Seleziona un file principale presente nel progetto.")
    return project


def map_data(model: ProgramIR | World) -> dict[str, Any]:
    world = instantiate(model) if isinstance(model, ProgramIR) else model
    rooms = [asdict(entity) for entity in world.entities if has_type(world, entity.type_id, ROOM)]
    link_directions = {
        NORTH: "nord",
        EAST: "est",
        NORTHEAST: "nordest",
        SOUTHEAST: "sudest",
        UP: "su",
    }
    links = [
        {
            "from": edge.source_id,
            "to": edge.target_id,
            "direction": link_directions[edge.predicate_id],
        }
        for edge in world.relations
        if edge.predicate_id in link_directions
    ]
    doors = []
    for entity in world.entities:
        sides = {
            edge.predicate_id: edge.target_id
            for edge in world.relations
            if edge.source_id == entity.id and edge.predicate_id in {SIDE_A, SIDE_B}
        }
        if len(sides) == 2:
            doors.append(
                {"id": entity.id, "label": entity.label, "from": sides[SIDE_A], "to": sides[SIDE_B]}
            )
    vehicles = [
        {
            "id": entity.id,
            "label": entity.label,
            "room": next(
                (
                    edge.target_id
                    for edge in world.relations
                    if edge.source_id == entity.id and edge.predicate_id == INSIDE
                ),
                None,
            ),
        }
        for entity in world.entities
        if has_type(world, entity.type_id, VEHICLE)
    ]
    return {
        "rooms": rooms,
        "links": links,
        "doors": doors,
        "vehicles": vehicles,
        "entry": world.entry_id or (rooms[0]["id"] if rooms else None),
    }


class Studio:
    def __init__(self) -> None:
        self.program: ProgramIR | None = None
        self.session: Session | None = None
        self.ended = False

    def compile(self, project: Any) -> dict[str, Any]:
        # Una compilazione fallita invalida la precedente: niente gioco di una versione vecchia.
        self.program = None
        self.session = None
        self.ended = False
        project = validate_project(project)
        with TemporaryDirectory(prefix="locus-studio-") as directory:
            root = Path(directory).resolve()
            for name, source in project["files"].items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(source, encoding="utf-8", newline="")
            for name, encoded in project.get("assets", {}).items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(base64.b64decode(encoded, validate=True))
            try:
                program = compile_story_file(root / project["entry"], allowed_root=root)
            except CompileError as error:
                return {"ok": False, "diagnostics": [diagnostic(error, root)]}
            # I percorsi delle origini vengono resi portabili per trace e navigazione nell'editor.
            from dataclasses import replace

            program = replace(
                program,
                rules=tuple(
                    replace(
                        rule,
                        origin=replace(
                            rule.origin,
                            source=str(Path(rule.origin.source).relative_to(root)).replace(
                                "\\", "/"
                            ),
                        ),
                    )
                    for rule in program.rules
                ),
            )
        self.program = program
        world = instantiate(program)
        return {
            "ok": True,
            "diagnostics": [],
            "ir": asdict(program),
            "map": map_data(program),
            "entities": len(program.entities),
            "rules": len(program.rules),
            "actions": len(program.actions),
            "dialogues": len(program.dialogues),
            "scenes": len(program.scenes),
            "vehicles": sum(has_type(world, entity.type_id, VEHICLE) for entity in world.entities),
            "currencies": sum(
                has_type(world, entity.type_id, CURRENCY) for entity in world.entities
            ),
            "merchandise": sum(
                has_type(world, entity.type_id, MERCHANDISE) for entity in world.entities
            ),
            "merchants": sum(
                has_type(world, entity.type_id, MERCHANT) for entity in world.entities
            ),
            "resources": len(program.resources),
            "title": program.title,
            "author": program.author,
        }

    def _output(self, transition: Transition) -> dict[str, Any]:
        media_entity = None
        if transition.event.kind in {"look", "examined"} and transition.event.entities:
            media_entity = transition.event.entities[0]
        return {
            "ok": True,
            "text": render(transition),
            "trace": [asdict(item) for item in transition.trace],
            "room": transition.session.room_id,
            "inventory": list(transition.session.inventory),
            "vehicle": transition.session.vehicle_id,
            "owned": list(transition.session.owned_ids),
            "ended": transition.event.kind == "quit",
            "map": map_data(transition.session.world),
            "properties": [asdict(item) for item in transition.session.world.properties],
            "relations": [asdict(item) for item in transition.session.world.relations],
            "tables": [asdict(item) for item in transition.session.world.tables],
            "dialogue": [asdict(item) for item in transition.dialogue],
            "active_dialogue": transition.session.dialogue_id,
            "active_dialogue_node": transition.session.dialogue_node_id,
            "visited_dialogue_nodes": list(transition.session.visited_dialogue_nodes),
            "turn": transition.session.turn,
            "score": transition.session.score,
            "active_scenes": list(transition.session.active_scene_ids),
            "completed_scenes": list(transition.session.completed_scene_ids),
            "score_log": [asdict(item) for item in transition.session.score_log],
            "scenes": [asdict(item) for item in transition.scenes],
            "media": [
                asdict(item)
                for item in transition.session.world.resources
                if item.entity_id == media_entity
            ],
        }

    def restart(self) -> dict[str, Any]:
        if self.program is None:
            raise ValueError("Compila un progetto valido prima di avviare la storia.")
        transition = step(start(instantiate(self.program)), Intent("look"), advance_time=False)
        self.session = transition.session
        self.ended = False
        return self._output(transition)

    def command(self, command: str) -> dict[str, Any]:
        if self.session is None or self.ended:
            raise ValueError("Avvia o riavvia la storia prima di inviare un comando.")
        if len(command) > 2000:
            raise ValueError("Comando troppo lungo.")
        transition = step(
            self.session,
            parse_command(
                command,
                self.session.world.actions,
                dialogue_enabled=bool(self.session.world.dialogues),
                scene_enabled=bool(self.session.world.scenes),
                vehicle_enabled=any(
                    has_type(self.session.world, entity.type_id, VEHICLE)
                    for entity in self.session.world.entities
                ),
                commerce_enabled=any(
                    has_type(self.session.world, entity.type_id, CURRENCY)
                    for entity in self.session.world.entities
                ),
            ),
        )
        self.session = transition.session
        self.ended = transition.event.kind == "quit"
        return self._output(transition)

    def test(self, commands: list[str], expected: str | None = None) -> dict[str, Any]:
        if self.program is None:
            raise ValueError("Compila un progetto valido prima di eseguire i test.")
        if (
            not isinstance(commands, list)
            or len(commands) > 500
            or any(not isinstance(c, str) or len(c) > 2000 for c in commands)
        ):
            raise ValueError("Un test ammette al massimo 500 comandi di 2000 caratteri.")
        runner = Studio()
        runner.program = self.program
        outputs = [runner.restart()["text"]]
        steps = []
        for command in commands:
            result = runner.command(command)
            outputs.append(result["text"])
            steps.append({"command": command, **result})
            if result["ended"]:
                break
        actual = "\n".join(outputs) + "\n"
        passed = None if expected is None else actual == expected.replace("\r\n", "\n")
        return {
            "ok": True,
            "actual": actual,
            "passed": passed,
            "steps": steps,
            "executed": len(steps),
            "requested": len(commands),
        }

    def dispatch(self, request: str) -> str:
        try:
            data = json.loads(request)
            operation = data["operation"]
            if operation == "compile":
                result = self.compile(data["project"])
            elif operation == "restart":
                result = self.restart()
            elif operation == "command":
                result = self.command(data["command"])
            elif operation == "test":
                result = self.test(data["commands"], data.get("expected"))
            else:
                raise ValueError("Operazione dello Studio non riconosciuta.")
        except (ValueError, TypeError, KeyError) as error:
            result = {"ok": False, "message": str(error)}
        return json.dumps(result, ensure_ascii=False)
