import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from locus.cli import main


@pytest.mark.parametrize("command", ["ast", "ir", "compila", "controlla"])
def test_commands(command: str, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    source = tmp_path / "storia.locus"
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
    source = tmp_path / "s.locus"
    source.write_text("Il cane è un animale.", encoding="utf-8")
    assert main(["ast", str(source)]) == 0
    assert main(["controlla", str(source)]) == 1


@pytest.mark.parametrize("data", [b"invalid", b"\xff"])
def test_invalid_input(data: bytes, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "s.locus"
    path.write_bytes(data)
    assert main(["controlla", str(path)]) == 1
    output = capsys.readouterr()
    assert output.err and not output.out
    assert "Traceback" not in output.err


def test_missing_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["controlla", str(tmp_path / "assente")]) == 1
    assert "Impossibile leggere" in capsys.readouterr().err


@pytest.mark.parametrize("args", [[], ["sconosciuto", "x"], ["controlla"], ["ir", "x", "y"]])
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
        [sys.executable, "-m", "locus", "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONUTF8": "1"},
        check=False,
    )
    assert result.returncode == 0
    assert "uso: locus" in result.stdout


def test_ast_offsets_preserve_crlf(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    source = tmp_path / "windows.locus"
    text = "La A è una cosa.\r\nLa B è una cosa."
    source.write_bytes(text.encode("utf-8"))
    assert main(["ast", str(source)]) == 0
    span = json.loads(capsys.readouterr().out)["declarations"][1]["span"]
    assert span["start"] == text.index("La B")
    assert span["line"] == 2


def test_game_cli_transcript(tmp_path: Path) -> None:
    source = tmp_path / "storia.locus"
    source.write_text(
        "La Cucina è una stanza. Il Corridoio è una stanza. "
        "Il Corridoio è a nord della Cucina. La chiave è una cosa nella Cucina.",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "-m", "locus", "gioca", str(source)],
        input="prendi la chiave\ninventario\nnord\nsud\nesci\n",
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONUTF8": "1"},
        check=False,
    )
    assert result.returncode == 0
    assert not result.stderr
    assert result.stdout.splitlines() == [
        "Cucina",
        "Vedi: chiave.",
        "Hai preso: chiave.",
        "Inventario: chiave.",
        "Corridoio",
        "Vedi: nessun oggetto.",
        "Cucina",
        "Vedi: nessun oggetto.",
        "A presto.",
    ]


def test_game_cli_resumes_an_ambiguous_command(tmp_path: Path) -> None:
    source = tmp_path / "chiavi.locus"
    source.write_text(
        "La Sala è una stanza. La chiave di rame è una cosa nella Sala. "
        "La chiave di ferro è una cosa nella Sala.",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "-m", "locus", "gioca", str(source)],
        input="prendi chiave\n2\nesci\n",
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONUTF8": "1"},
        check=False,
    )
    assert result.returncode == 0
    assert "Quale intendi? 1) chiave di rame; 2) chiave di ferro." in result.stdout
    assert "Hai preso: chiave di ferro." in result.stdout


def test_game_cli_accepts_a_pronoun_and_an_attached_clitic(tmp_path: Path) -> None:
    source = tmp_path / "lanterna.locus"
    source.write_text(
        "La Sala è una stanza. La lanterna è una cosa nella Sala.",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "-m", "locus", "gioca", str(source)],
        input="esamina lanterna\nprendila\nx essa\nesci\n",
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONUTF8": "1"},
        check=False,
    )
    assert result.returncode == 0
    assert "Hai preso: lanterna." in result.stdout
    assert result.stdout.count("lanterna\nNon noti nulla di particolare.") == 2


def test_game_cli_keeps_the_complement_after_an_attached_clitic(tmp_path: Path) -> None:
    source = tmp_path / "scatola.locus"
    source.write_text(
        "La Sala è una stanza. "
        'La scatola è un contenitore nella Sala. La scatola ha stato "aperto". '
        "La gemma è una cosa nella Sala.",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "-m", "locus", "gioca", str(source)],
        input="prendi gemma\nmettila nella scatola\nesci\n",
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONUTF8": "1"},
        check=False,
    )
    assert result.returncode == 0
    assert "Hai messo gemma dentro scatola." in result.stdout


def test_game_cli_accepts_a_double_clitic(tmp_path: Path) -> None:
    source = tmp_path / "scatola.locus"
    source.write_text(
        "La Sala è una stanza. "
        'La scatola è un contenitore nella Sala. La scatola ha stato "aperto". '
        "La gemma è una cosa nella Sala. La moneta è una cosa nella Sala.",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "-m", "locus", "gioca", str(source)],
        input="prendi gemma\nmetti gemma nella scatola\nprendi moneta\nmetticela\nesci\n",
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONUTF8": "1"},
        check=False,
    )
    assert result.returncode == 0
    assert "Hai messo moneta dentro scatola." in result.stdout


def test_game_cli_accepts_a_locative_clitic_with_an_explicit_object(tmp_path: Path) -> None:
    source = tmp_path / "scatola.locus"
    source.write_text(
        "La Sala è una stanza. "
        'La scatola è un contenitore nella Sala. La scatola ha stato "aperto". '
        "La gemma è una cosa nella Sala. La moneta è una cosa nella Sala.",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "-m", "locus", "gioca", str(source)],
        input=("prendi gemma\nmetti gemma nella scatola\nprendi moneta\nmettici la moneta\nesci\n"),
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONUTF8": "1"},
        check=False,
    )
    assert result.returncode == 0
    assert "Hai messo moneta dentro scatola." in result.stdout


def test_cli_executes_an_author_command(tmp_path: Path) -> None:
    source = tmp_path / "azione.locus"
    source.write_text(
        "La Sala è una stanza. "
        'Azione "meditare" senza oggetti con comando "medita" e sinonimo "fai silenzio". '
        'Regola "meditazione" per meditare nella fase invece: '
        'dì "Respiri lentamente."; Fine regola.',
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "-m", "locus", "gioca", str(source)],
        input="fai silenzio\nesci\n",
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONUTF8": "1"},
        check=False,
    )
    assert result.returncode == 0 and not result.stderr
    assert "Respiri lentamente." in result.stdout


def test_game_without_rooms(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    source = tmp_path / "vuoto.locus"
    source.write_text("", encoding="utf-8")
    assert main(["gioca", str(source)]) == 1
    assert "almeno una stanza" in capsys.readouterr().err


def test_game_eof(tmp_path: Path) -> None:
    source = tmp_path / "storia.locus"
    source.write_text("La A è una stanza.", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "locus", "gioca", str(source)],
        input="",
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONUTF8": "1"},
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout == "A\nVedi: nessun oggetto.\n"


def test_m2_cli_solution_outside_checkout(tmp_path: Path) -> None:
    example = Path(__file__).resolve().parents[1] / "examples" / "porte_e_contenitori.locus"
    result = subprocess.run(
        [sys.executable, "-m", "locus", "gioca", str(example)],
        cwd=tmp_path,
        input=(
            "apri scrigno\nprendi chiave di ottone\n"
            "apri porta rossa con chiave di ottone\nnord\nesci\n"
        ),
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONUTF8": "1"},
        check=False,
    )
    assert result.returncode == 0
    assert not result.stderr
    assert "Hai aperto: porta rossa." in result.stdout
    assert "Corridoio\n" in result.stdout


def test_cli_reports_narrative_validation_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "porta.locus"
    source.write_text("La Sala è una stanza. La porta è una porta.", encoding="utf-8")
    assert main(["controlla", str(source)]) == 1
    assert "E201" in capsys.readouterr().err
