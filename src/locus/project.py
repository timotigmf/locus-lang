"""Caricamento dei sorgenti locali; nessun I/O nel compilatore o nel runtime."""

from collections.abc import Mapping
from pathlib import Path, PurePosixPath, PureWindowsPath

from locus.ast import Program
from locus.diagnostics import CompileError, Span
from locus.parser import parse


def load_project(
    path: Path,
    *,
    verbs: Mapping[str, str] | None = None,
    max_files: int = 256,
    max_depth: int = 64,
    allowed_root: Path | None = None,
) -> Program:
    """Unione in postordine: dipendenze prima del file che le include."""
    if max_files < 1 or max_depth < 1:
        raise ValueError("I limiti del progetto devono essere positivi.")
    active: list[Path] = []
    visited: set[Path] = set()
    units: list[Program] = []
    sources: list[str] = []

    def visit(candidate: Path, origin: Span | None = None) -> None:
        location = origin or Span(str(candidate), 0, 0, 1, 1)
        try:
            resolved = candidate.resolve(strict=True)
        except (OSError, RuntimeError, ValueError) as error:
            raise CompileError(
                "E402", f"Impossibile leggere il file UTF-8: {candidate}.", location
            ) from error
        if allowed_root is not None and not resolved.is_relative_to(allowed_root.resolve()):
            raise CompileError("E404", "L'inclusione esce dai file del progetto.", location)
        if resolved in active:
            chain = " → ".join(str(item) for item in (*active, resolved))
            raise CompileError("E403", f"Inclusione ciclica: {chain}.", location)
        if resolved in visited:
            return
        if len(active) >= max_depth or len(visited) + len(active) >= max_files:
            raise CompileError(
                "E405", "Superato il limite di file o profondità del progetto.", location
            )
        try:
            if not resolved.is_file():
                raise OSError("La sorgente deve essere un file regolare.")
            with resolved.open(encoding="utf-8", newline="") as stream:
                text = stream.read()
        except (OSError, UnicodeError) as error:
            raise CompileError(
                "E402", f"Impossibile leggere il file UTF-8: {resolved}.", location
            ) from error
        unit = parse(text, str(resolved), verbs=verbs)
        active.append(resolved)
        for inclusion in unit.inclusions:
            name = inclusion.path
            # Percorsi portabili, mai espansi come shell, URL o variabili d'ambiente.
            if (
                PurePosixPath(name).is_absolute()
                or PureWindowsPath(name).drive
                or "\\" in name
                or ":" in name
                or "\x00" in name
                or "\r" in name
            ):
                raise CompileError(
                    "E404", "Usa un percorso relativo con separatori '/'.", inclusion.span
                )
            visit(resolved.parent / name, inclusion.span)
        active.pop()
        visited.add(resolved)
        units.append(unit)
        sources.append(str(resolved))

    visit(path)
    return Program(
        declarations=tuple(item for unit in units for item in unit.declarations),
        kinds=tuple(item for unit in units for item in unit.kinds),
        relations=tuple(item for unit in units for item in unit.relations),
        properties=tuple(item for unit in units for item in unit.properties),
        assignments=tuple(item for unit in units for item in unit.assignments),
        rules=tuple(item for unit in units for item in unit.rules),
        entries=tuple(item for unit in units for item in unit.entries),
        source_order=tuple(sources),
        metadata=tuple(item for unit in units for item in unit.metadata),
        vocabulary=tuple(item for unit in units for item in unit.vocabulary),
        actions=tuple(item for unit in units for item in unit.actions),
    )
