import os
import subprocess
import sys
from pathlib import Path
from typing import cast

import pytest

from locus.player import parse_command
from locus.runtime import instantiate
from locus.stdlib.authoring import compile_story_file
from locus.stdlib.game import Session, parse_session_command, start, step
from locus.stdlib.render import render
from locus.stdlib.validation import property_value

ROOT = Path(__file__).resolve().parents[1]
TUTORIAL = ROOT / "examples" / "tutorial"


@pytest.mark.parametrize("path", sorted(TUTORIAL.glob("*.locus")))
def test_lessons_compile(path: Path) -> None:
    start(instantiate(compile_story_file(path)))


def test_cli_solution_transcript() -> None:
    process = subprocess.run(
        [sys.executable, "-m", "locus", "gioca", str(TUTORIAL / "04_faro.locus")],
        input=(TUTORIAL / "04_faro.comandi").read_text(encoding="utf-8"),
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
        env={**os.environ, "PYTHONUTF8": "1"},
        timeout=10,
    )
    assert process.returncode == 0, process.stderr
    assert not process.stderr
    assert process.stdout == (TUTORIAL / "04_faro.atteso").read_text(encoding="utf-8")


def property_of(session: Session, name: str, suffix: str) -> str | int | bool:
    entity = next(e for e in session.world.entities if e.label == name)
    spec = next(p for p in session.world.property_specs if p.id.endswith(suffix))
    value = property_value(session.world, entity.id, spec.id)
    assert type(value) in {str, int, bool}
    return cast(str | int | bool, value)


def test_signal_reversibility_and_failed_repeat() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "03_segnale.locus")))
    initial_description = property_of(current, "Terrazza", "descrizione")
    for _ in range(3):
        opened = step(current, parse_command("apri lanterna"))
        assert property_of(opened.session, "lanterna", "segnale") is True
        assert "foschia" in render(step(opened.session, parse_command("guarda")))
        repeat = step(opened.session, parse_command("apri lanterna"))
        assert repeat.session is opened.session
        assert not repeat.trace  # L'azione fallita non raggiunge le regole dopo.
        current = step(opened.session, parse_command("chiudi lanterna")).session
        assert property_of(current, "lanterna", "segnale") is False
        assert property_of(current, "Terrazza", "descrizione") == initial_description


def test_container_failed_put_preserves_inventory() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "02_custodia.locus")))
    for command in ["apri custodia", "prendi chiave di rame", "chiudi custodia"]:
        current = step(current, parse_command(command)).session
    failed = step(current, parse_command("metti chiave di rame nella custodia"))
    assert failed.session is current
    assert len(current.inventory) == 1


def test_clue_list_tutorial_collects_deduces_and_removes() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "14_taccuino_indizi.locus")))
    failed = step(current, parse_command("deduci", current.world.actions))
    assert render(failed) == "Non hai ancora raccolto indizi sufficienti."
    for command in ("x impronta", "x lettera"):
        transition = step(current, parse_command(command, current.world.actions))
        current = transition.session
    solved = step(current, parse_command("formula deduzione", current.world.actions))
    assert "conducono alla serra" in render(solved)
    forgotten = step(
        solved.session,
        parse_command("dimentica impronta", solved.session.world.actions),
    )
    assert "Cancelli" in render(forgotten)
    assert "sufficienti" in render(
        step(
            forgotten.session,
            parse_command("deduci", forgotten.session.world.actions),
        )
    )


def test_table_tutorial_transfers_the_artifact_atomically() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "15_tabelle_reperti.locus")))
    before = step(current, parse_command("consulta deposito", current.world.actions))
    assert "attende nel deposito" in render(before)
    moved = step(
        before.session,
        parse_command("trasferisci astrolabio", before.session.world.actions),
    )
    assert "trasferito nella mostra" in render(moved)
    assert moved.session.world.tables[0].rows == (("maschera", 25, False),)
    assert moved.session.world.tables[1].rows == (("astrolabio", 40, True),)
    assert "vetrina centrale" in render(
        step(
            moved.session,
            parse_command("consulta mostra", moved.session.world.actions),
        )
    )
    repeated = step(
        moved.session,
        parse_command("trasferisci astrolabio", moved.session.world.actions),
    )
    assert repeated.session is moved.session
    assert render(repeated) == "L'astrolabio non è disponibile nel deposito."


def test_tutorial_accepts_classic_abbreviation_and_unique_partial_name() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "02_custodia.locus")))
    examined = step(current, parse_command("x custodia"))
    assert examined.event.kind == "examined"
    opened = step(examined.session, parse_command("open custodia"))
    taken = step(opened.session, parse_command("take chiave"))
    assert taken.event.kind == "taken"
    assert "chiave di rame" in render(taken)


def test_help_tutorial_lists_story_actions_without_advancing_time() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "39_aiuto_in_partita.locus")))
    helped = step(current, parse_session_command(current, "aiuto"))
    assert helped.session is current
    assert helped.session.turn == 0
    assert "azioni della storia: suona." in render(helped)
    rung = step(helped.session, parse_session_command(helped.session, "suona campana"))
    assert "rintocco attraversa la torre" in render(rung)
    assert parse_session_command(current, "aiuto movimento").verb == "unknown"


def test_repeat_tutorial_replays_authored_action_and_wait() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "40_ripetere_comando.locus")))
    missing = step(current, parse_session_command(current, "g"))
    assert missing.event.kind == "no_previous_command"
    assert missing.session is current

    rung = step(current, parse_session_command(current, "suona campana"))
    repeated_rung = step(rung.session, parse_session_command(rung.session, "ancora"))
    assert "rintocco profondo" in render(rung)
    assert "rintocco profondo" in render(repeated_rung)

    waited = step(repeated_rung.session, parse_session_command(repeated_rung.session, "attendi"))
    repeated_wait = step(waited.session, parse_session_command(waited.session, "ripeti"))
    assert repeated_wait.event.kind == "waited"
    assert repeated_wait.session.turn == waited.session.turn + 1


def test_compass_rose_tutorial_traverses_all_diagonals() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "23_direzioni_diagonali.locus")))
    assert step(current, parse_command("nord")).event.kind == "no_exit"
    for outbound, destination, inbound in (
        ("ne", "Vedetta", "so"),
        ("se", "Darsena", "no"),
        ("so", "Forgia", "ne"),
        ("no", "Giardino", "se"),
    ):
        moved = step(current, parse_command(outbound))
        assert (
            next(
                entity.label
                for entity in moved.session.world.entities
                if entity.id == moved.session.room_id
            )
            == destination
        )
        returned = step(moved.session, parse_command(inbound))
        assert returned.session.room_id == current.room_id


def test_vertical_levels_tutorial_moves_up_and_down() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "24_livelli_verticali.locus")))
    terrace = step(current, parse_command("su"))
    assert "Terrazza" in render(terrace)
    center = step(terrace.session, parse_command("giù"))
    assert center.session.room_id == current.room_id
    cistern = step(center.session, parse_command("d"))
    assert "Cisterna" in render(cistern)
    returned = step(cistern.session, parse_command("u"))
    assert returned.session.room_id == current.room_id


def test_inward_outward_tutorial_enters_and_leaves_the_lantern_room() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "25_dentro_fuori.locus")))
    lantern = step(current, parse_command("dentro"))
    assert "Lanterna" in render(lantern)
    returned = step(lantern.session, parse_command("fuori"))
    assert returned.session.room_id == current.room_id


def test_one_way_tutorial_does_not_create_the_inverse_exit() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "33_senso_unico.locus")))
    crypt = step(current, parse_command("d"))
    assert "Cripta" in render(crypt)
    assert step(crypt.session, parse_command("u")).event.kind == "no_exit"


def test_dynamic_one_way_tutorial_reveals_a_drop_without_return() -> None:
    current = start(
        instantiate(compile_story_file(TUTORIAL / "34_passaggio_unidirezionale_segreto.locus"))
    )
    assert step(current, parse_command("d")).event.kind == "no_exit"
    revealed = step(current, parse_command("esamina leva"))
    crypt = step(revealed.session, parse_command("d"))
    assert "Cripta" in render(crypt)
    assert step(crypt.session, parse_command("u")).event.kind == "no_exit"


def test_natural_movement_tutorial_uses_the_same_directional_intents() -> None:
    current = start(
        instantiate(compile_story_file(TUTORIAL / "35_comandi_naturali_movimento.locus"))
    )
    lantern = step(current, parse_command("vai a nord"))
    assert "Lanterna" in render(lantern)
    dock = step(lantern.session, parse_command("cammina verso sud"))
    assert "Banchina" in render(dock)
    invalid = step(dock.session, parse_command("vai alla cambusa"))
    assert invalid.session is dock.session
    assert invalid.event.kind == "invalid_direction"


def test_back_tutorial_returns_normally_but_not_after_the_one_way_drop() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "36_tornare_indietro.locus")))
    assert step(current, parse_command("indietro")).event.kind == "no_previous_room"
    lantern = step(current, parse_command("nord"))
    dock = step(lantern.session, parse_command("torna indietro"))
    assert "Banchina" in render(dock)
    lantern_again = step(dock.session, parse_command("back"))
    crypt = step(lantern_again.session, parse_command("giù"))
    blocked = step(crypt.session, parse_command("indietro"))
    assert blocked.event.kind == "cannot_return"
    assert blocked.session is crypt.session


def test_clarification_tutorial_accepts_a_synonym_on_the_next_turn() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "26_chiarimenti.locus")))
    asked = step(current, parse_session_command(current, "prendi chiave"))
    assert asked.event.kind == "ambiguous"
    assert asked.session.clarification is not None
    taken = step(asked.session, parse_session_command(asked.session, "scura"))
    assert taken.event.kind == "taken"
    assert "chiave di ferro" in render(taken)


def test_pronoun_tutorial_reuses_the_last_direct_object() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "27_pronomi_e_clitici.locus")))
    examined = step(current, parse_session_command(current, "esamina lanterna"))
    taken = step(examined.session, parse_session_command(examined.session, "prendila"))
    assert taken.event.kind == "taken"
    repeated = step(taken.session, parse_session_command(taken.session, "x essa"))
    assert repeated.event.kind == "examined"
    assert "lanterna di vetro" in render(repeated)


def test_clitic_complement_tutorial_keeps_the_second_object() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "28_clitici_con_complemento.locus")))
    current = step(current, parse_session_command(current, "prendi chiave")).session
    current = step(current, parse_session_command(current, "esamina cofano")).session
    opened = step(current, parse_session_command(current, "aprilo con chiave"))
    assert opened.event.kind == "opened"
    taken = step(opened.session, parse_session_command(opened.session, "prendi gemma"))
    put = step(taken.session, parse_session_command(taken.session, "mettila nel cofano"))
    assert put.event.kind == "put"


def test_double_clitic_tutorial_reuses_the_destination() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "29_clitici_doppi.locus")))
    current = step(current, parse_session_command(current, "prendi gemma")).session
    current = step(
        current,
        parse_session_command(current, "metti gemma nella scatola"),
    ).session
    current = step(current, parse_session_command(current, "prendi moneta")).session
    put = step(current, parse_session_command(current, "metticela"))
    assert put.event.kind == "put"


def test_locative_clitic_tutorial_keeps_the_explicit_object() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "30_clitico_locativo.locus")))
    current = step(current, parse_session_command(current, "prendi gettone rosso")).session
    current = step(
        current,
        parse_session_command(current, "metti gettone rosso nella cassetta"),
    ).session
    current = step(current, parse_session_command(current, "prendi gettone blu")).session
    put = step(current, parse_session_command(current, "mettici il gettone blu"))
    assert put.event.kind == "put"


def test_locative_adverb_tutorial_reuses_the_destination() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "31_avverbi_locativi.locus")))
    current = step(current, parse_session_command(current, "prendi bussola")).session
    current = step(
        current,
        parse_session_command(current, "metti bussola nel baule"),
    ).session
    current = step(current, parse_session_command(current, "prendi sestante")).session
    put = step(current, parse_session_command(current, "metti il sestante lì"))
    assert put.event.kind == "put"


def test_role_pronoun_tutorial_reuses_the_last_instrument() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "32_pronomi_per_ruolo.locus")))
    current = step(current, parse_session_command(current, "prendi chiave")).session
    opened = step(current, parse_session_command(current, "apri cofano con chiave"))
    assert opened.event.kind == "opened"
    closed = step(opened.session, parse_session_command(opened.session, "chiudilo"))
    repeated = step(closed.session, parse_session_command(closed.session, "aprilo con essa"))
    assert repeated.event.kind == "opened"


def test_dungeon_tutorial_awards_points_once_after_the_puzzle() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "06_sotterraneo.locus")))
    for command in [
        "apri scatola",
        "prendi chiave",
        "n",
        "apri porta di pietra con chiave",
        "e",
        "prendi reliquia",
    ]:
        result = step(current, parse_command(command))
        assert result.event.kind not in {"unknown", "not_found", "blocked"}
        current = result.session
    assert property_of(current, "registro", "punti") == 10
    repeated = step(current, parse_command("prendi statua"))
    assert repeated.session is current
    assert property_of(repeated.session, "registro", "punti") == 10
    for _ in range(3):
        dropped = step(current, parse_command("lascia reliquia"))
        assert dropped.event.kind == "dropped"
        retaken = step(dropped.session, parse_command("prendi statua"))
        assert retaken.event.kind == "taken"
        assert property_of(retaken.session, "registro", "punti") == 10
        assert "ottenuto dieci punti" not in render(retaken)
        current = retaken.session


def test_author_action_tutorial_checks_types_and_updates_state() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "08_azioni.locus")))

    def command(text: str) -> str:
        nonlocal current
        result = step(current, parse_command(text, current.world.actions))
        current = result.session
        return render(result)

    assert "prudente" in command("saluta custode")
    assert "riconosce il sigillo" in command("mostra sigillo al custode")
    assert property_of(current, "custode", "fiducia") == 1
    assert "ospite atteso" in command("saluta custode")
    assert command("saluta sigillo") == "Questo comando non si applica a quell'elemento."
    assert property_of(current, "custode", "fiducia") == 1


def test_action_synonym_tutorial_accepts_all_declared_forms() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "09_sinonimi_azioni.locus")))

    def command(text: str) -> str:
        nonlocal current
        result = step(current, parse_command(text, current.world.actions))
        current = result.session
        return render(result)

    for text in ("saluta custode", "riverisci custode", "inchinati custode"):
        assert "ricambia" in command(text)
    assert "riconosce" in command("esibisci amuleto verso il custode")
    assert property_of(current, "custode", "fiducia") == 1
    assert "storia" in command("parla custode dell'amuleto")
    assert "storia" in command("racconta custode sull'amuleto")


def test_multiword_command_tutorial_consumes_fixed_prefixes() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "10_comandi_multiparola.locus")))

    def command(text: str) -> str:
        result = step(current, parse_command(text, current.world.actions))
        return render(result)

    assert "silenzio" in command("fai silenzio")
    assert "silenzio" in command("resta immobile")
    assert "china il capo" in command("saluta solennemente custode")
    assert "china il capo" in command("onora custode")
    assert "riconosce" in command("fai vedere amuleto al custode")
    assert "riconosce" in command("porta in vista amuleto verso il custode")
    assert parse_command("fai", current.world.actions).verb == "unknown"


def test_multiword_separator_tutorial_accepts_articulated_endings() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "11_separatori_multiparola.locus")))

    def command(text: str) -> str:
        nonlocal current
        result = step(current, parse_command(text, current.world.actions))
        current = result.session
        return render(result)

    assert "registra lo scambio" in command("scambia moneta in cambio della chiave di vetro")
    assert "registra lo scambio" in command("dai in pegno moneta insieme alla chiave di vetro")
    assert property_of(current, "mercante", "fiducia") == 2
    assert "sigillo" in command("interroga mercante a proposito dell'amuleto")
    assert parse_command("scambia moneta in chiave", current.world.actions).verb == "unknown"


def test_secret_passage_tutorial_changes_navigation_both_ways() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "12_passaggio_segreto.locus")))
    assert step(current, parse_command("nord")).event.kind == "no_exit"
    revealed = step(current, parse_command("x leva"))
    assert "rivela un passaggio" in render(revealed)
    assert len(revealed.session.world.relations) == len(current.world.relations) + 2
    crypt = step(revealed.session, parse_command("nord"))
    assert "camera nascosta" in render(crypt)
    returned = step(crypt.session, parse_command("sud"))
    hidden = step(
        returned.session,
        parse_command("nascondi passaggio", returned.session.world.actions),
    )
    assert "richiude" in render(hidden)
    assert step(hidden.session, parse_command("nord")).event.kind == "no_exit"


def test_scenery_tutorial_reveals_a_real_object() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "13_scenario_nascosto.locus")))
    assert "chiave" not in render(step(current, parse_command("guarda")))
    assert step(current, parse_command("prendi chiave")).event.kind == "not_here"
    assert step(current, parse_command("prendi cielo")).event.kind == "not_portable"
    revealed = step(current, parse_command("x cielo"))
    assert "cade sul pavimento" in render(revealed)
    assert "chiave d'argento" in render(step(revealed.session, parse_command("guarda")))
    assert step(revealed.session, parse_command("prendi chiave")).event.kind == "taken"


def test_dialogue_tutorial_branches_cycles_and_ends() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "16_dialogo_guardiana.locus")))

    def command(text: str) -> str:
        nonlocal current
        transition = step(
            current,
            parse_command(text, current.world.actions, dialogue_enabled=True),
        )
        current = transition.session
        return render(transition)

    assert "Chiedi della tempesta" in command("parla con guardiana")
    dialogue_id = current.dialogue_id
    assert "Comandi principali:" in command("aiuto")
    assert current.dialogue_id == dialogue_id
    assert "tre notti" in command("1")
    assert "posa il registro" in command("scegli torna alle domande")
    assert "sotto la campana" in command("scegli chiave")
    assert current.dialogue_id is None
    assert len(current.visited_dialogue_nodes) == 3


def test_scene_tutorial_tracks_turns_and_awards_points_once() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "17_tempesta_e_punteggio.locus")))

    def command(text: str) -> str:
        nonlocal current
        transition = step(
            current,
            parse_command(text, current.world.actions, scene_enabled=True),
        )
        current = transition.session
        return render(transition)

    assert command("turno") == "Turno: 0."
    assert "tempesta è iniziata" in command("guarda")
    assert command("inventario") == "Inventario: vuoto."
    assert "nuvole si aprono" in command("esamina orologio")
    assert command("punteggio") == "Punteggio: 10."
    assert current.turn == 3
    assert len(current.score_log) == 1


def test_wait_tutorial_advances_the_storm_and_awards_points() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "37_aspettare.locus")))

    def command(text: str) -> str:
        nonlocal current
        transition = step(
            current,
            parse_command(text, current.world.actions, scene_enabled=True),
        )
        current = transition.session
        return render(transition)

    first = command("attendi")
    assert "Il tempo passa." in first
    assert "Conti le gocce" in first
    assert "Un tuono" in first
    assert current.turn == 1
    assert "La pioggia si allontana" in command("z")
    assert command("punteggio") == "Punteggio: 2."
    assert current.turn == 2


def test_natural_examination_tutorial_shares_resolution_and_clarification() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "38_guardare_oggetti.locus")))
    looked = step(current, parse_session_command(current, "guarda"))
    assert looked.event.kind == "look"
    examined = step(looked.session, parse_session_command(looked.session, "guarda custodia"))
    assert examined.event.kind == "examined"
    assert "Cuoio scuro" in render(examined)
    asked = step(
        examined.session,
        parse_session_command(examined.session, "osserva medaglione"),
    )
    assert asked.event.kind == "ambiguous"
    selected = step(asked.session, parse_session_command(asked.session, "argento"))
    assert selected.event.kind == "examined"
    assert "luna" in render(selected)


def test_vehicle_tutorial_moves_vehicle_with_player() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "18_bicicletta_in_movimento.locus")))

    def command(text: str) -> str:
        nonlocal current
        transition = step(
            current,
            parse_command(text, current.world.actions, vehicle_enabled=True),
        )
        current = transition.session
        return render(transition)

    assert "campanello" in command("sali sulla saetta")
    assert "Piazza" in command("est")
    assert current.vehicle_id is not None
    assert "cavalletto" in command("scendi")
    assert current.vehicle_id is None


def test_commerce_tutorial_spends_currency_atomically() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "19_mercato_del_faro.locus")))

    def command(text: str) -> str:
        nonlocal current
        transition = step(
            current,
            parse_command(text, current.world.actions, commerce_enabled=True),
        )
        current = transition.session
        return render(transition)

    assert "Saldo: 15" in command("denaro")
    assert "prima comprare" in command("prendi bussola")
    assert "registro" in command("compra bussola")
    assert "Saldo: 8" in command("denaro")
    before = current
    assert "Fondi insufficienti" in command("compra corda")
    assert current == before


def test_merchant_tutorial_transfers_stock_and_cash_atomically() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "20_bottegaia_e_rivendita.locus")))

    def command(text: str) -> str:
        nonlocal current
        transition = step(
            current,
            parse_command(text, current.world.actions, commerce_enabled=True),
        )
        current = transition.session
        return render(transition)

    assert "registra sette crediti" in command("compra bussola da Ada")
    assert property_of(current, "credito portuale", "saldo") == 13
    assert property_of(current, "Ada", "cassa") == 32
    assert "di nuovo nella sua scorta" in command("vendi bussola a Ada")
    assert property_of(current, "credito portuale", "saldo") == 16
    assert property_of(current, "Ada", "cassa") == 29
    assert not current.inventory
    assert not current.owned_ids


def test_final_world_matches_story() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "04_faro.locus")))
    for command in (TUTORIAL / "04_faro.comandi").read_text(encoding="utf-8").splitlines():
        current = step(current, parse_command(command)).session
    assert property_of(current, "lanterna", "segnale") is False
    assert len(current.inventory) == 1
    assert next(e.label for e in current.world.entities if e.id == current.room_id) == "Terrazza"


@pytest.mark.parametrize(
    ("filename", "command", "first_text", "repeat_text"),
    [
        ("12_passaggio_segreto.locus", "x leva", "La leva scatta", "Il passaggio è già aperto."),
        ("13_scenario_nascosto.locus", "x cielo", "cade sul pavimento", "Il piccolo vano"),
        (
            "34_passaggio_unidirezionale_segreto.locus",
            "x leva",
            "La lastra ruota",
            "La botola è già aperta.",
        ),
    ],
)
def test_discovery_tutorials_separate_first_and_later_messages(
    filename: str, command: str, first_text: str, repeat_text: str
) -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / filename)))
    first = step(current, parse_session_command(current, command))
    assert first_text in render(first)
    assert repeat_text not in render(first)
    for text in (command, "g"):
        repeated = step(first.session, parse_session_command(first.session, text))
        assert repeat_text in render(repeated)
        assert first_text not in render(repeated)


def test_second_observation_solution_counts_only_successful_examinations() -> None:
    current = start(instantiate(compile_story_file(TUTORIAL / "13b_seconda_osservazione.locus")))
    for text in ("guarda", "prendi chiave", "x assente", "aiuto"):
        current = step(current, parse_session_command(current, text)).session
        assert property_of(current, "mosaico", "osservazioni") == 0
    first = step(current, parse_session_command(current, "x mosaico"))
    assert "La luna sembra mobile" in render(first)
    assert "rivela una chiave" not in render(first)
    assert property_of(first.session, "chiave", "visibile") is False
    missing = step(first.session, parse_session_command(first.session, "prendi chiave"))
    assert missing.event.kind == "not_here"
    second = step(missing.session, parse_session_command(missing.session, "g"))
    assert "rivela una chiave" in render(second)
    assert "già aperto" not in render(second)
    assert property_of(second.session, "mosaico", "osservazioni") == 2
    taken = step(second.session, parse_session_command(second.session, "prendi chiave"))
    assert taken.event.kind == "taken"
    repeated = step(taken.session, parse_session_command(taken.session, "x mosaico"))
    assert "Il vano è già aperto." in render(repeated)
    assert "rivela una chiave" not in render(repeated)
    assert property_of(repeated.session, "mosaico", "osservazioni") == 2
    assert repeated.session.inventory == taken.session.inventory
