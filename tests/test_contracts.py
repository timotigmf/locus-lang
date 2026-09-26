import ast
import re
from pathlib import Path

import pytest

from locus.stdlib.authoring import compile_story, compile_story_file

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN = sorted(ROOT.glob("*.md")) + sorted((ROOT / "docs").rglob("*.md"))
EXAMPLES = [
    pytest.param(source, str(path), id=f"{path.relative_to(ROOT)}:{index}")
    for path in MARKDOWN
    for index, source in enumerate(
        re.findall(r"^```(?:ita|locus)\n(.*?)^```", path.read_text(encoding="utf-8"), re.M | re.S)
    )
]


@pytest.mark.parametrize(("source", "path"), EXAMPLES)
def test_documentation_examples(source: str, path: str) -> None:
    compile_story(source, path)


@pytest.mark.parametrize("path", sorted((ROOT / "examples").glob("*.locus")))
def test_example_files(path: Path) -> None:
    compile_story_file(path)


@pytest.mark.parametrize(
    ("module", "forbidden"),
    [
        ("compiler", {"stdlib", "runtime", "cli"}),
        ("parser", {"stdlib", "runtime", "compiler", "cli"}),
        ("lexer", {"stdlib", "runtime", "compiler", "parser", "cli"}),
        ("runtime", {"stdlib", "compiler", "parser", "lexer", "ast", "cli"}),
        ("player", {"compiler", "parser", "lexer", "ast", "cli"}),
        ("ir", {"stdlib", "compiler", "parser", "lexer", "ast", "runtime", "cli"}),
    ],
)
def test_dependency_boundaries(module: str, forbidden: set[str]) -> None:
    tree = ast.parse((ROOT / "src" / "locus" / f"{module}.py").read_text(encoding="utf-8"))
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
        elif isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
    for imported in imports:
        assert not any(
            imported == f"locus.{name}" or imported.startswith(f"locus.{name}.")
            for name in forbidden
        )
