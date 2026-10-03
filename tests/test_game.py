from pathlib import Path

import pytest

from locus.compiler import compile_source
from locus.player import Intent, parse_command
from locus.runtime import Entity, World, instantiate
from locus.stdlib import ROOM, THING, default_kinds, default_relations
from locus.stdlib.authoring import compile_story
from locus.stdlib.game import Session, parse_session_command, start, step
from locus.stdlib.render import render

ROOT = Path(__file__).resolve().parents[1]


def make_session() -> Session:
    source = (ROOT / "examples" / "prima_storia.locus").read_text(encoding="utf-8")
    return start(
        instantiate(compile_source(source, default_kinds(), relations=default_relations()))
    )


@pytest.mark.parametrize(
    ("command", "intent"),
    [
        ("aiuto", Intent("help")),
        ("comandi", Intent("help")),
        ("help", Intent("help")),
        ("?", Intent("help")),
        ("ancora", Intent("repeat")),
        ("ripeti", Intent("repeat")),
        ("again", Intent("repeat")),
        ("g", Intent("repeat")),
        (" GUARDA ", Intent("look")),
        ("l", Intent("look")),
        ("look", Intent("look")),
        ("inventario", Intent("inventory")),
        ("i", Intent("inventory")),
        ("inv", Intent("inventory")),
        ("attendi", Intent("wait")),
        ("aspetta", Intent("wait")),
        ("z", Intent("wait")),
        ("wait", Intent("wait")),
        ("nord", Intent("north")),
        ("n", Intent("north")),
        ("sud", Intent("south")),
        ("s", Intent("south")),
        ("est", Intent("east")),
        ("e", Intent("east")),
        ("east", Intent("east")),
        ("ovest", Intent("west")),
        ("o", Intent("west")),
        ("w", Intent("west")),
        ("west", Intent("west")),
        ("nordest", Intent("northeast")),
        ("ne", Intent("northeast")),
        ("northeast", Intent("northeast")),
        ("sudest", Intent("southeast")),
        ("se", Intent("southeast")),
        ("southeast", Intent("southeast")),
        ("sudovest", Intent("southwest")),
        ("so", Intent("southwest")),
        ("southwest", Intent("southwest")),
        ("nordovest", Intent("northwest")),
        ("no", Intent("northwest")),
        ("nw", Intent("northwest")),
        ("northwest", Intent("northwest")),
        ("su", Intent("up")),
        ("alto", Intent("up")),
        ("u", Intent("up")),
        ("up", Intent("up")),
        ("giù", Intent("down")),
        ("giu", Intent("down")),
        ("basso", Intent("down")),
        ("d", Intent("down")),
        ("down", Intent("down")),
        ("dentro", Intent("inward")),
        ("interno", Intent("inward")),
        ("in", Intent("inward")),
        ("inside", Intent("inward")),
        ("fuori", Intent("outward")),
        ("esterno", Intent("outward")),
        ("out", Intent("outward")),
        ("outside", Intent("outward")),
        ("vai a nord", Intent("north")),
        ("cammina verso sudovest", Intent("southwest")),
        ("muoviti in alto", Intent("up")),
        ("dirigiti all'esterno", Intent("outward")),
        ("procedi dentro", Intent("inward")),
        ("go north", Intent("north")),
        ("move down", Intent("down")),
        ("walk to northwest", Intent("northwest")),
        ("indietro", Intent("back")),
        ("torna", Intent("back")),
        ("torna indietro", Intent("back")),
        ("vai indietro", Intent("back")),
        ("go back", Intent("back")),
        ("vai", Intent("missing_direction")),
        ("vai verso", Intent("missing_direction")),
        ("vai alla porta", Intent("invalid_direction")),
        ("vai nord sud", Intent("invalid_direction")),
        ("esci", Intent("quit")),
        ("q", Intent("quit")),
        ("prendi chiave", Intent("take", "chiave")),
        ("take the key", Intent("take", "key")),
        ("get chiave", Intent("take", "chiave")),
        ("x custodia", Intent("examine", "custodia")),
        ("examine custodia", Intent("examine", "custodia")),
        ("guarda la custodia", Intent("examine", "custodia")),
        ("osserva custodia", Intent("examine", "custodia")),
        ("ispeziona custodia", Intent("examine", "custodia")),
        ("controlla custodia", Intent("examine", "custodia")),
        ("look at the custodia", Intent("examine", "custodia")),
        ("inspect custodia", Intent("examine", "custodia")),
        ("prendi la chiave", Intent("take", "chiave")),
        ("prendi l’oggetto", Intent("take", "oggetto")),
        ("prendi il caffè", Intent("take", "caffè")),
        ("prendi lo scudo", Intent("take", "scudo")),
        ("prendi la chiave di ottone", Intent("take", "chiave di ottone")),
        ("prendila", Intent("take", "essa")),
        ("esaminalo", Intent("examine", "esso")),
        ("aprila", Intent("open", "essa")),
        ("chiudilo", Intent("close", "esso")),
        ("lasciala", Intent("drop", "essa")),
        ("mettila nella scatola", Intent("put", "essa", "scatola")),
        ("aprilo con chiave", Intent("open", "esso", "chiave")),
        ("bloccala con chiave", Intent("lock", "essa", "chiave")),
        ("metticelo", Intent("put", "esso", "ci")),
        ("metticela", Intent("put", "essa", "ci")),
        ("mettici la moneta", Intent("put", "moneta", "ci")),
        ("mettici", Intent("missing_noun")),
        ("mettici moneta nella scatola", Intent("unknown")),
        ("metti la moneta lì", Intent("put", "moneta", "ci")),
        ("metti moneta là", Intent("put", "moneta", "ci")),
        ("metti lì", Intent("missing_noun")),
        ("metti moneta lì nella scatola", Intent("unknown")),
        ("mettila", Intent("unknown")),
        ("bloccalo", Intent("unknown")),
        ("prendila subito", Intent("unknown")),
        ("metticela subito", Intent("unknown")),
        ("prendi la", Intent("unknown")),
        ("prendi", Intent("take")),
        ("x", Intent("examine")),
        ("", Intent("unknown")),
        ("raccoglila", Intent("unknown")),
        ("nord sud", Intent("unknown")),
    ],
)
def test_player_parser(command: str, intent: Intent) -> None:
    assert parse_command(command) == intent


def test_complete_solution_transcript_and_replay() -> None:
    commands = [
        "guarda",
        "prendi la chiave",
        "prendi la chiave",
        "inventario",
        "nord",
        "nord",
        "sud",
        "guarda",
        "inventario",
        "esci",
    ]
    expected = [
        "Cucina\nVedi: chiave.",
        "Hai preso: chiave.",
        "Hai già questo oggetto.",
        "Inventario: chiave.",
        "Corridoio\nVedi: nessun oggetto.",
        "Non c'è alcun passaggio in quella direzione.",
        "Cucina\nVedi: nessun oggetto.",
        "Cucina\nVedi: nessun oggetto.",
        "Inventario: chiave.",
        "A presto.",
    ]
    for _ in range(2):
        session = make_session()
        initial = session
        actual = []
        for command in commands:
            result = step(session, parse_command(command))
            session = result.session
            actual.append(render(result))
        assert actual == expected
        assert initial.inventory == ()
        assert session.inventory == ("e3",)
        assert session.room_id == initial.room_id
        assert session.world is not initial.world
        assert len(initial.world.relations) == 3
        assert len(session.world.relations) == 2


def test_absent_and_unreachable_objects_do_not_change_state() -> None:
    session = make_session()
    for command, kind in [
        ("prendi fantasma", "not_here"),
        ("prendi Cucina", "not_portable"),
        ("sud", "no_exit"),
        ("e", "no_exit"),
        ("o", "no_exit"),
        ("ne", "no_exit"),
        ("se", "no_exit"),
        ("so", "no_exit"),
        ("no", "no_exit"),
        ("u", "no_exit"),
        ("d", "no_exit"),
        ("dentro", "no_exit"),
        ("fuori", "no_exit"),
        ("salta", "unknown"),
    ]:
        result = step(session, parse_command(command))
        assert result.event.kind == kind
        assert result.session is session
    north = step(session, Intent("north")).session
    assert step(north, Intent("take", "chiave")).event.kind == "not_here"
    assert render(step(session, Intent("inventory"))) == "Inventario: vuoto."


def test_sessions_are_independent() -> None:
    session = make_session()
    assert step(session, Intent("take", "chiave")).session.inventory
    assert make_session() == session


def test_wait_has_an_explicit_default_without_changing_the_world() -> None:
    session = make_session()
    result = step(session, parse_command("attendi"))
    assert result.event.kind == "waited"
    assert result.session.world is session.world
    assert result.session.last_intent == Intent("wait")
    assert render(result) == "Il tempo passa."


def test_help_is_turnless_and_lists_authored_commands() -> None:
    current = start(
        instantiate(
            compile_story(
                "La Sala è una stanza. La campana è una cosa nella Sala. "
                'Azione "suonare" su una cosa con comando "suona". '
                'Scena "prova" dal turno 1 al turno 2: '
                'Inizio "Inizia.". Fine "Finisce.". Fine scena.'
            )
        )
    )
    result = step(current, parse_session_command(current, "aiuto"))
    text = render(result)
    assert result.event.kind == "help"
    assert result.session is current
    assert result.session.turn == 0
    assert "Comandi principali:" in text
    assert "- storia: turno, punteggio;" in text
    assert "azioni della storia: suona NOME." in text
    assert parse_session_command(current, "aiuto movimento") == Intent("unknown")


def test_repeat_replays_the_last_successful_command_without_remembering_failures() -> None:
    current = make_session()
    missing = step(current, parse_session_command(current, "ancora"))
    assert missing.event.kind == "no_previous_command"
    assert missing.session is current

    taken = step(current, parse_session_command(current, "prendi chiave"))
    assert taken.event.kind == "taken"
    assert taken.session.last_intent == Intent("take", "chiave")

    unknown = step(taken.session, parse_session_command(taken.session, "salta"))
    assert unknown.session.last_intent == taken.session.last_intent
    repeated = step(unknown.session, parse_session_command(unknown.session, "g"))
    assert repeated.event.kind == "already_carried"
    assert repeated.session.last_intent == taken.session.last_intent

    helped = step(repeated.session, parse_session_command(repeated.session, "aiuto"))
    assert helped.session.last_intent == taken.session.last_intent


def test_repeat_advances_scenes_for_each_replayed_wait() -> None:
    current = start(
        instantiate(
            compile_story(
                "La Sala è una stanza. "
                'Scena "prova" dal turno 1 al turno 3: '
                'Inizio "Inizia.". Fine "Finisce.". Fine scena.'
            )
        )
    )
    waited = step(current, parse_session_command(current, "attendi"))
    repeated = step(waited.session, parse_session_command(waited.session, "again"))
    assert waited.session.turn == 1
    assert repeated.event.kind == "waited"
    assert repeated.session.turn == 2


def test_repeat_reuses_the_object_selected_during_clarification() -> None:
    current = start(
        instantiate(
            compile_story(
                "La Sala è una stanza. La chiave di rame è una cosa nella Sala. "
                "La chiave di ferro è una cosa nella Sala."
            )
        )
    )
    asked = step(current, parse_session_command(current, "esamina chiave"))
    asked_again = step(asked.session, parse_session_command(asked.session, "ripeti"))
    assert asked_again.event.kind == "ambiguous"
    assert asked_again.session.clarification is not None

    selected = step(asked_again.session, parse_session_command(asked_again.session, "2"))
    assert selected.event.entities == ("e3",)
    assert selected.session.last_intent == Intent("examine", "chiave", noun_id="e3")
    repeated = step(selected.session, parse_session_command(selected.session, "g"))
    assert repeated.event.kind == "examined"
    assert repeated.event.entities == ("e3",)


def test_east_west_movement_and_inverse() -> None:
    world = instantiate(
        compile_source(
            "La Sala è una stanza. La Serra è una stanza. La Serra è a est della Sala.",
            default_kinds(),
            relations=default_relations(),
        )
    )
    current = start(world)
    moved = step(current, parse_command("e"))
    assert moved.event.kind == "look"
    assert next(e.label for e in world.entities if e.id == moved.session.room_id) == "Serra"
    returned = step(moved.session, parse_command("o"))
    assert returned.event.kind == "look"
    assert returned.session.room_id == current.room_id


@pytest.mark.parametrize(
    ("predicate", "outbound", "inbound", "destination"),
    [
        ("nordest", "ne", "so", "Belvedere"),
        ("sudest", "se", "no", "Darsena"),
    ],
)
def test_diagonal_movement_and_inverse(
    predicate: str, outbound: str, inbound: str, destination: str
) -> None:
    world = instantiate(
        compile_source(
            f"La Sala è una stanza. La {destination} è una stanza. "
            f"La {destination} è a {predicate} della Sala.",
            default_kinds(),
            relations=default_relations(),
        )
    )
    current = start(world)
    moved = step(current, parse_command(outbound))
    assert next(e.label for e in world.entities if e.id == moved.session.room_id) == destination
    returned = step(moved.session, parse_command(inbound))
    assert returned.session.room_id == current.room_id


def test_vertical_movement_and_inverse() -> None:
    world = instantiate(
        compile_story(
            "La Sala è una stanza. La Soffitta è una stanza. La Soffitta sovrasta la Sala."
        )
    )
    current = start(world)
    moved = step(current, parse_command("u"))
    assert next(e.label for e in world.entities if e.id == moved.session.room_id) == "Soffitta"
    returned = step(moved.session, parse_command("d"))
    assert returned.session.room_id == current.room_id


def test_inward_outward_movement_and_inverse() -> None:
    world = instantiate(
        compile_story("La Villa è una stanza. L'Atrio è una stanza. La Villa racchiude l'Atrio.")
    )
    current = start(world)
    moved = step(current, parse_command("dentro"))
    assert next(e.label for e in world.entities if e.id == moved.session.room_id) == "Atrio"
    returned = step(moved.session, parse_command("fuori"))
    assert returned.session.room_id == current.room_id


def test_one_way_passage_has_no_automatic_return() -> None:
    world = instantiate(
        compile_story(
            "La Sala è una stanza. La Cripta è una stanza. Dalla Sala si va a nord verso la Cripta."
        )
    )
    current = start(world)
    moved = step(current, parse_command("nord"))
    assert next(e.label for e in world.entities if e.id == moved.session.room_id) == "Cripta"
    blocked = step(moved.session, parse_command("sud"))
    assert blocked.event.kind == "no_exit"
    assert blocked.session is moved.session


def test_world_without_rooms_compiles_but_cannot_start_game() -> None:
    world = instantiate(compile_source("La chiave è una cosa.", default_kinds()))
    with pytest.raises(ValueError, match="almeno una stanza"):
        start(world)


def test_author_room_container_key_and_thing_types_keep_their_capabilities() -> None:
    source = (
        "Un santuario è un tipo di stanza. "
        "Un reliquiario è un tipo di contenitore. "
        "Una chiave rituale è un tipo di chiave. "
        "Una reliquia è un tipo di cosa. "
        "La Cripta è un santuario. "
        'Inizia nella "Cripta". '
        'La Cripta ha descrizione "Una camera votiva.". '
        "Il cofano è un reliquiario nella Cripta. "
        'Il cofano ha stato "bloccato". '
        "La chiave di bronzo è una chiave rituale nella Cripta. "
        "La chiave di bronzo apre il cofano. "
        "Il rubino è una reliquia nel cofano. "
        'Regola "eco" per prendere "rubino" nella fase dopo: '
        'imposta "descrizione" di "Cripta" a "Il cofano è vuoto."; Fine regola.'
    )
    current = start(instantiate(compile_story(source)))
    assert "Una camera votiva." in render(step(current, parse_command("guarda")))
    current = step(current, parse_command("prendi chiave")).session
    current = step(current, parse_command("apri cofano con chiave")).session
    taken = step(current, parse_command("prendi rubino"))
    assert taken.event.kind == "taken"
    assert "rubino" in render(taken)
    assert "Il cofano è vuoto." in render(step(taken.session, parse_command("guarda")))


def test_unplaced_objects_are_not_accessible() -> None:
    world = instantiate(compile_source("La A è una stanza. La chiave è una cosa.", default_kinds()))
    assert step(start(world), Intent("take", "chiave")).event.kind == "not_here"


def test_ambiguous_intent_on_world_constructed_by_host() -> None:
    world = World(
        (Entity("r", "Sala", ROOM), Entity("a", "chiave", THING), Entity("b", "chiave", THING))
    )
    session = Session(world, "r", ("a", "b"))
    result = step(session, Intent("take", "chiave"))
    assert result.event.kind == "ambiguous"
    assert result.session.inventory == session.inventory
    assert result.session.clarification is not None


def test_partial_name_resolves_only_when_unique_in_current_scope() -> None:
    world = World(
        (
            Entity("r", "Sala", ROOM),
            Entity("a", "chiave di rame", THING),
            Entity("b", "chiave di ferro", THING),
        )
    )
    one_key = Session(world, "r", ("a",))
    taken = step(one_key, parse_command("prendi chiave"))
    assert taken.event.kind == "already_carried"
    assert taken.event.entities == ("a",)

    two_keys = Session(world, "r", ("a", "b"))
    ambiguous = step(two_keys, parse_command("prendi chiave"))
    assert ambiguous.event.kind == "ambiguous"
    assert render(ambiguous) == (
        "Quale intendi? 1) chiave di rame; 2) chiave di ferro. "
        "Rispondi con il numero o il nome, oppure scrivi «annulla»."
    )


def test_ambiguity_can_be_resolved_on_the_next_turn_by_number_or_partial_name() -> None:
    world = World(
        (
            Entity("r", "Sala", ROOM),
            Entity("a", "chiave di rame", THING),
            Entity("b", "chiave di ferro", THING),
        )
    )
    initial = Session(world, "r", ("a", "b"))
    asked = step(initial, parse_session_command(initial, "prendi chiave"))
    assert asked.session.turn == 0
    assert asked.session.clarification is not None

    helped = step(asked.session, parse_session_command(asked.session, "?"))
    assert helped.event.kind == "help"
    assert helped.session.clarification == asked.session.clarification
    assert helped.session.turn == 0

    invalid = step(helped.session, parse_session_command(helped.session, "legno"))
    assert invalid.event.kind == "invalid_clarification"
    assert invalid.session.clarification == asked.session.clarification
    assert invalid.session.turn == 0

    selected = step(invalid.session, parse_session_command(invalid.session, "ferro"))
    assert selected.event.kind == "already_carried"
    assert selected.event.entities == ("b",)
    assert selected.session.clarification is None

    asked_again = step(initial, parse_session_command(initial, "prendi chiave"))
    first = step(asked_again.session, parse_session_command(asked_again.session, "1"))
    assert first.event.kind == "already_carried"
    assert first.event.entities == ("a",)


def test_clarification_can_be_cancelled_or_replaced_by_a_new_command() -> None:
    world = World(
        (
            Entity("r", "Sala", ROOM),
            Entity("a", "chiave di rame", THING),
            Entity("b", "chiave di ferro", THING),
        )
    )
    initial = Session(world, "r", ("a", "b"))
    asked = step(initial, parse_session_command(initial, "prendi chiave"))
    cancelled = step(asked.session, parse_session_command(asked.session, "annulla"))
    assert cancelled.event.kind == "clarification_cancelled"
    assert cancelled.session.clarification is None
    assert cancelled.session.turn == 0

    asked_again = step(initial, parse_session_command(initial, "prendi chiave"))
    looked = step(asked_again.session, parse_session_command(asked_again.session, "guarda"))
    assert looked.event.kind == "look"
    assert looked.session.clarification is None


def test_pronouns_and_clitics_reuse_the_last_direct_object() -> None:
    initial = make_session()
    missing = step(initial, parse_session_command(initial, "prendila"))
    assert missing.event.kind == "no_referent"
    assert missing.session is initial
    assert render(missing) == "Non c'è ancora un oggetto a cui riferire il pronome."

    examined = step(initial, parse_session_command(initial, "esamina chiave"))
    assert examined.session.pronoun_id == examined.event.entities[0]
    looked = step(examined.session, parse_session_command(examined.session, "guarda"))
    assert looked.session.pronoun_id == examined.session.pronoun_id
    taken = step(looked.session, parse_session_command(looked.session, "prendila"))
    assert taken.event.kind == "taken"
    assert taken.event.entities == (examined.session.pronoun_id,)
    dropped = step(taken.session, parse_session_command(taken.session, "drop it"))
    assert dropped.event.kind == "dropped"


def test_pronoun_in_each_role_uses_the_matching_referent() -> None:
    world = World(
        (
            Entity("r", "Sala", ROOM),
            Entity("a", "oggetto", THING),
            Entity("b", "destinazione", THING),
        )
    )
    session = Session(world, "r", pronoun_id="a", indirect_pronoun_id="b")
    assert parse_session_command(session, "metti essa in essa") == Intent(
        "put",
        "oggetto",
        "destinazione",
        "a",
        "b",
    )


def test_disambiguated_object_becomes_the_pronoun_referent() -> None:
    world = World(
        (
            Entity("r", "Sala", ROOM),
            Entity("a", "chiave di rame", THING),
            Entity("b", "chiave di ferro", THING),
        )
    )
    initial = Session(world, "r", ("a", "b"))
    asked = step(initial, parse_session_command(initial, "esamina chiave"))
    selected = step(asked.session, parse_session_command(asked.session, "2"))
    assert selected.event.kind == "examined"
    assert selected.session.pronoun_id == "b"
    again = step(selected.session, parse_session_command(selected.session, "esaminala"))
    assert again.event.entities[0] == "b"


def test_missing_object_gets_a_specific_prompt() -> None:
    assert render(step(make_session(), parse_command("x"))) == (
        "Indica quale oggetto vuoi esaminare o manipolare."
    )


def test_look_with_an_object_examines_it_while_bare_look_describes_the_room() -> None:
    session = make_session()
    assert step(session, parse_command("guarda")).event.kind == "look"
    examined = step(session, parse_command("guarda chiave"))
    assert examined.event.kind == "examined"
    assert examined.event.entities == ("e3",)
    assert render(examined).startswith("chiave\n")
    assert step(session, parse_command("osserva")).event.kind == "missing_noun"


def test_natural_movement_errors_are_specific_and_turnless() -> None:
    current = make_session()
    missing = step(current, parse_command("vai"))
    assert missing.session is current
    assert render(missing) == "Indica in quale direzione vuoi andare."
    invalid = step(current, parse_command("vai verso il molo"))
    assert invalid.session is current
    assert render(invalid).startswith("Direzione non riconosciuta.")


def test_back_returns_to_the_previous_room_and_can_toggle() -> None:
    current = make_session()
    missing = step(current, parse_command("indietro"))
    assert missing.session is current
    assert render(missing) == "Non hai ancora lasciato un luogo a cui tornare."

    corridor = step(current, parse_command("nord"))
    assert corridor.session.previous_room_id == current.room_id
    kitchen = step(corridor.session, parse_command("torna indietro"))
    assert kitchen.session.room_id == current.room_id
    assert kitchen.session.previous_room_id == corridor.session.room_id
    assert "Cucina" in render(kitchen)
    again = step(kitchen.session, parse_command("back"))
    assert again.session.room_id == corridor.session.room_id


def test_back_respects_a_one_way_passage() -> None:
    current = start(
        instantiate(
            compile_story(
                "La Terrazza è una stanza. La Cripta è una stanza. "
                "Dalla Terrazza si va giù verso la Cripta."
            )
        )
    )
    crypt = step(current, parse_command("giù"))
    blocked = step(crypt.session, parse_command("indietro"))
    assert blocked.session is crypt.session
    assert render(blocked) == "Non puoi tornare indietro da qui."


def test_author_synonyms_resolve_in_scope_and_can_be_ambiguous() -> None:
    source = (
        "La Sala è una stanza. La custodia è una cosa nella Sala. "
        "La cassa blu è una cosa nella Sala. "
        'Comprendi "forziere" come "custodia". '
        'Comprendi "cassa rossa" come "custodia". '
        'Comprendi "baule" come "cassa blu".'
    )
    state = start(
        instantiate(compile_source(source, default_kinds(), relations=default_relations()))
    )
    assert step(state, parse_command("x forziere")).event.entities == ("e2",)
    assert step(state, parse_command("prendi baule")).event.entities == ("e3",)
    ambiguous = step(state, parse_command("x cassa"))
    assert ambiguous.event.kind == "ambiguous"


@pytest.mark.parametrize("with_dialogue", [False, True])
@pytest.mark.parametrize("answer", ["scegli 2", "scegli ferro", "SCEGLI   scura"])
def test_explicit_choice_resumes_clarification_with_or_without_dialogues(
    with_dialogue: bool, answer: str
) -> None:
    source = (
        "La Sala è una stanza. La chiave di rame è una chiave nella Sala. "
        "La chiave di ferro è una chiave nella Sala. "
        'Comprendi "scura" come "chiave di ferro".'
    )
    if with_dialogue:
        source += (
            'La guida è una persona nella Sala. Dialogo "saluto" con "guida": '
            'Nodo "inizio" dice "Buongiorno.": Fine nodo. Fine dialogo.'
        )
    current = start(instantiate(compile_story(source)))
    assert parse_session_command(current, "scegli 2").verb == (
        "dialogue_choice" if with_dialogue else "unknown"
    )
    current = step(current, parse_session_command(current, "prendi chiave")).session
    for invalid in ("scegli", "scegli 99", "scegli chiave"):
        result = step(current, parse_session_command(current, invalid))
        assert result.event.kind == "invalid_clarification"
        assert result.session is current
    result = step(current, parse_session_command(current, answer))
    assert result.event.kind == "taken"
    assert "chiave di ferro" in render(result)
    assert result.session.clarification is None


def test_dialogue_choice_named_like_command_requires_prefix_or_number() -> None:
    current = start(
        instantiate(
            compile_story(
                "La Sala è una stanza. La guida è una persona nella Sala. "
                'Dialogo "prova" con "guida": Nodo "inizio" dice "Decidi.": '
                'Scelta "Aiuto" termina. Fine nodo. Fine dialogo.'
            )
        )
    )
    current = step(current, parse_session_command(current, "parla con guida")).session
    helped = step(current, parse_session_command(current, "aiuto"))
    assert helped.event.kind == "help"
    assert helped.session is current
    selected = step(current, parse_session_command(current, "scegli Aiuto"))
    assert selected.event.kind == "dialogue_end"
    assert selected.session.dialogue_id is None


@pytest.mark.parametrize(
    "answer",
    [
        "la chiave di ferro",
        "scegli la chiave di ferro",
        '"chiave di ferro"',
        'scegli "chiave di ferro"',
    ],
)
def test_clarification_accepts_articles_and_quoted_names(answer: str) -> None:
    current = start(
        instantiate(
            compile_story(
                "La Sala è una stanza. La chiave di rame è una chiave nella Sala. "
                "La chiave di ferro è una chiave nella Sala."
            )
        )
    )
    current = step(current, parse_session_command(current, "prendi chiave")).session
    result = step(current, parse_session_command(current, answer))
    assert result.event.kind == "taken"
    assert "chiave di ferro" in render(result)


def test_clarification_article_alone_does_not_select_an_object() -> None:
    current = start(
        instantiate(
            compile_story(
                "La Sala è una stanza. La chiave di rame è una chiave nella Sala. "
                "La chiave di ferro è una chiave nella Sala."
            )
        )
    )
    current = step(current, parse_session_command(current, "prendi chiave")).session
    for answer in ("la", "scegli la", "la chiave", '"chiave'):
        result = step(current, parse_session_command(current, answer))
        assert result.event.kind == "invalid_clarification"
        assert result.session is current


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("l’anello", "anello"),
        ('"la luna"', "la luna"),
        ("la", None),
        ("  LA   chiave  ", "chiave"),
    ],
)
def test_standalone_noun_phrase_uses_player_article_and_quote_rules(
    text: str, expected: str | None
) -> None:
    from locus.player import parse_noun_phrase

    assert parse_noun_phrase(text) == expected


@pytest.mark.parametrize(
    "command",
    [
        "guardalo",
        "guardala",
        "osservalo",
        "osservala",
        "ispezionalo",
        "ispezionala",
        "controllalo",
        "controllala",
    ],
)
def test_natural_examination_clitics_reuse_the_last_object(command: str) -> None:
    current = make_session()
    assert step(current, parse_session_command(current, command)).event.kind == "no_referent"
    examined = step(current, parse_session_command(current, "x chiave"))
    assert examined.event.kind == "examined"
    repeated = step(examined.session, parse_session_command(examined.session, command))
    assert repeated.event.kind == "examined"
    assert repeated.event.entities == examined.event.entities
    assert parse_command(command + " chiave").verb == "unknown"


@pytest.mark.parametrize("answer", ['"Aiuto"', '"La chiave"'])
def test_quoted_dialogue_answers_preserve_literal_choice_labels(answer: str) -> None:
    current = start(
        instantiate(
            compile_story(
                "La Sala è una stanza. La guida è una persona nella Sala. "
                'Dialogo "scelte" con "guida": Nodo "inizio" dice "Decidi.": '
                'Scelta "Aiuto" termina. Scelta "La chiave" termina. Fine nodo. Fine dialogo.'
            )
        )
    )
    current = step(current, parse_session_command(current, "parla con guida")).session
    for invalid in ('"Aiuto', '"assente"'):
        result = step(current, parse_session_command(current, invalid))
        assert result.event.kind == "invalid_choice"
        assert result.session is current
    selected = step(current, parse_session_command(current, answer))
    assert selected.event.kind == "dialogue_end"
    assert selected.dialogue[0].choice_label == answer.strip('"')


@pytest.mark.parametrize("answer", ["scegli la chiave", 'scegli "La chiave"', "la chiave"])
def test_dialogue_exact_label_with_article_precedes_shorter_label(answer: str) -> None:
    current = start(
        instantiate(
            compile_story(
                "La Sala è una stanza. La guida è una persona nella Sala. "
                'Dialogo "titoli" con "guida": Nodo "inizio" dice "Scegli un titolo.": '
                'Scelta "La chiave" termina. Scelta "Chiave" termina. Fine nodo. Fine dialogo.'
            )
        )
    )
    current = step(current, parse_session_command(current, "parla con guida")).session
    selected = step(current, parse_session_command(current, answer))
    assert selected.event.kind == "dialogue_end"
    assert selected.dialogue[0].choice_label == "La chiave"
