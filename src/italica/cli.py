"""Adattatore CLI e punto di composizione della libreria narrativa."""

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Never

from italica.compiler import compile_source
from italica.diagnostics import CompileError
from italica.parser import parse
from italica.stdlib import default_kinds

_USAGE = "uso: italica {controlla,ast,ir,compila} FILE\n"
_HELP = _USAGE + "\nControlla il sorgente o mostra AST/IR JSON. Opzioni: -h, --help.\n"


class _Arguments(argparse.ArgumentParser):
    def error(self, message: str) -> Never:
        self.exit(2, _USAGE + "Errore: indicare un comando valido e un file sorgente.\n")

    def format_help(self) -> str:
        return _HELP


def main(argv: list[str] | None = None) -> int:
    parser = _Arguments(prog="italica", allow_abbrev=False)
    parser.add_argument("command", choices=("controlla", "ast", "ir", "compila"))
    parser.add_argument("file", type=Path)
    args = parser.parse_args(argv)
    try:
        with args.file.open(encoding="utf-8", newline="") as source_file:
            text = source_file.read()
        if args.command == "ast":
            print(json.dumps(asdict(parse(text, str(args.file))), ensure_ascii=False, indent=2))
        else:
            program = compile_source(text, default_kinds(), str(args.file))
            if args.command == "controlla":
                print(f"Sorgente valido: {len(program.entities)} entità.")
            else:
                print(json.dumps(asdict(program), ensure_ascii=False, indent=2))
    except CompileError as error:
        print(error, file=sys.stderr)
        return 1
    except (OSError, UnicodeError):
        print(f"Impossibile leggere il file UTF-8: {args.file}.", file=sys.stderr)
        return 1
    return 0
