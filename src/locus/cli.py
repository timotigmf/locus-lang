"""Adattatore CLI e punto di composizione della libreria narrativa."""

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Never

from locus.compiler import relation_verbs
from locus.diagnostics import CompileError
from locus.player import Intent, parse_command
from locus.project import load_project
from locus.runtime import instantiate
from locus.stdlib import default_relations
from locus.stdlib.authoring import compile_story_file
from locus.stdlib.game import Transition, start, step
from locus.stdlib.render import render

_USAGE = "uso: locus {controlla,ast,ir,compila,gioca,debug} FILE\n"
_HELP = _USAGE + "\nControlla il sorgente o mostra AST/IR JSON. Opzioni: -h, --help.\n"


class _Arguments(argparse.ArgumentParser):
    def error(self, message: str) -> Never:
        self.exit(2, _USAGE + "Errore: indicare un comando valido e un file sorgente.\n")

    def format_help(self) -> str:
        return _HELP


def main(argv: list[str] | None = None) -> int:
    parser = _Arguments(prog="locus", allow_abbrev=False)
    parser.add_argument("command", choices=("controlla", "ast", "ir", "compila", "gioca", "debug"))
    parser.add_argument("file", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "ast":
            print(
                json.dumps(
                    asdict(load_project(args.file, verbs=relation_verbs(default_relations()))),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            program = compile_story_file(args.file)
            if args.command in {"gioca", "debug"}:
                session = start(instantiate(program))
                initial = step(session, Intent("look"))
                session = initial.session
                _show(initial, args.command == "debug")
                while True:
                    try:
                        command = input("> " if sys.stdin.isatty() else "")
                    except EOFError:
                        break
                    transition = step(
                        session,
                        parse_command(
                            command,
                            session.world.actions,
                            dialogue_enabled=bool(session.world.dialogues),
                        ),
                    )
                    session = transition.session
                    _show(transition, args.command == "debug")
                    if transition.event.kind == "quit":
                        break
            elif args.command == "controlla":
                print(f"Sorgente valido: {len(program.entities)} entità.")
            else:
                print(json.dumps(asdict(program), ensure_ascii=False, indent=2))
    except CompileError as error:
        print(error, file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nSessione interrotta.", file=sys.stderr)
        return 130
    except UnicodeError:
        print(f"Impossibile leggere il file UTF-8: {args.file}.", file=sys.stderr)
        return 1
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1
    except OSError:
        print(f"Impossibile leggere il file UTF-8: {args.file}.", file=sys.stderr)
        return 1
    return 0


def _show(transition: Transition, debug: bool) -> None:
    print(render(transition))
    if debug:
        for item in transition.trace:
            print(
                f"[{item.phase}; priorità {item.priority}] {item.name}: {item.outcome} "
                f"({item.origin.source}:{item.origin.line}:{item.origin.column})",
                file=sys.stderr,
            )
        for dialogue_step in transition.dialogue:
            choice = f"; scelta {dialogue_step.choice_label}" if dialogue_step.choice_label else ""
            print(
                f"[dialogo] {dialogue_step.dialogue_label}: "
                f"nodo {dialogue_step.node_label}{choice}",
                file=sys.stderr,
            )
