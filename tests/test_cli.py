import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from italica.cli import main


@pytest.mark.parametrize("command", ["ast", "ir", "compila", "controlla"])
def test_commands(command: str, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    source = tmp_path / "storia.ita"
    source.write_text("La Cucina è una stanza.", encoding="utf-8")
    assert main([command, str(source)]) == 0
    output = capsys.readouterr()
    assert not output.err
    if command == "controlla":
        assert output.out == "Sorgente valido: 1 entità.\n"
    elif command == "ast":
        assert json.loads(output.out)["declarations"][0]["name"] == "Cucina"
    else:
        assert json.loads(output.out)["entities"][0]["type_id"] == "mondo.stanza"


def test_ast_does_not_require_semantic_validation(tmp_path: Path) -> None:
    source = tmp_path / "s.ita"
    source.write_text("Il cane è un animale.", encoding="utf-8")
    assert main(["ast", str(source)]) == 0
    assert main(["controlla", str(source)]) == 1


@pytest.mark.parametrize("data", [b"invalid", b"\xff"])
def test_invalid_input(data: bytes, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "s.ita"
    path.write_bytes(data)
    assert main(["controlla", str(path)]) == 1
    output = capsys.readouterr()
    assert output.err and not output.out
    assert "Traceback" not in output.err


def test_missing_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["controlla", str(tmp_path / "assente")]) == 1
    assert "Impossibile leggere" in capsys.readouterr().err


@pytest.mark.parametrize("args", [[], ["gioca", "x"], ["controlla"], ["ir", "x", "y"]])
def test_usage_errors(args: list[str], capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as error:
        main(args)
    assert error.value.code == 2
    assert "Errore: indicare" in capsys.readouterr().err


def test_help(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as error:
        main(["--help"])
    assert error.value.code == 0
    assert "Controlla il sorgente" in capsys.readouterr().out


def test_module_entrypoint_outside_checkout(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "italica", "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONUTF8": "1"},
        check=False,
    )
    assert result.returncode == 0
    assert "uso: italica" in result.stdout


def test_ast_offsets_preserve_crlf(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    source = tmp_path / "windows.ita"
    text = "La A è una cosa.\r\nLa B è una cosa."
    source.write_bytes(text.encode("utf-8"))
    assert main(["ast", str(source)]) == 0
    span = json.loads(capsys.readouterr().out)["declarations"][1]["span"]
    assert span["start"] == text.index("La B")
    assert span["line"] == 2
