from pathlib import Path

import pytest

from kubelings.manifest import get_manifest
from kubelings.models import Chapter, Exercise, Manifest
from kubelings.runner import ExerciseRunner
from kubelings.watcher import (
    WatchEngine,
    WatcherState,
    find_next_incomplete_exercise,
    handle_keypress,
)


def test_handle_keypress_hint():
    state = WatcherState(exercise=get_manifest().chapters[0].exercises[0])
    assert state.current_hint_index == 0

    new_hint = handle_keypress("h", state)
    assert new_hint == 1
    assert state.current_hint_index == 1


def test_handle_keypress_quit():
    state = WatcherState(exercise=get_manifest().chapters[0].exercises[0])
    with pytest.raises(KeyboardInterrupt):
        handle_keypress("q", state)


def test_handle_keypress_rerun():
    state = WatcherState(exercise=get_manifest().chapters[0].exercises[0])
    assert state.force_rerun is False
    handle_keypress("r", state)
    assert state.force_rerun is True


def test_handle_keypress_unknown():
    state = WatcherState(exercise=get_manifest().chapters[0].exercises[0])
    handle_keypress("z", state)
    assert state.current_hint_index == 0


def test_handle_keypress_next_and_prev():
    """Verify handle_keypress sets action for n, enter, p, and l keys."""
    state = WatcherState(exercise=get_manifest().chapters[0].exercises[0])
    assert state.action is None

    handle_keypress("n", state)
    assert state.action == "next"

    state.action = None
    handle_keypress("\n", state)
    assert state.action == "next"

    state.action = None
    handle_keypress("\r", state)
    assert state.action == "next"

    state.action = None
    handle_keypress("p", state)
    assert state.action == "prev"

    state.action = None
    handle_keypress("l", state)
    assert state.action == "list"


def test_watcher_engine_handle_input_key_navigation(tmp_path: Path):
    """Verify WatchEngine handle_input_key supports n, p, enter, r, h, and q keys."""
    f1 = tmp_path / "ex1.py"
    f1.write_text("assert False, 'failing 1'\n")
    f2 = tmp_path / "ex2.py"
    f2.write_text("assert False, 'failing 2'\n")
    f3 = tmp_path / "ex3.py"
    f3.write_text("assert False, 'failing 3'\n")

    ex1 = Exercise("ex1", "Ex 1", str(f1), "ch1", hints=["Hint 1"])
    ex2 = Exercise("ex2", "Ex 2", str(f2), "ch1", hints=["Hint 2"])
    ex3 = Exercise("ex3", "Ex 3", str(f3), "ch1", hints=["Hint 3"])

    manifest = Manifest(chapters=[Chapter(1, "ch1", "Ch 1", "Desc", [ex1, ex2, ex3])])
    engine = WatchEngine(manifest=manifest, runner=ExerciseRunner())

    assert engine.current_exercise == ex1

    # Advance with 'n'
    res = engine.handle_input_key("n")
    assert res == ex2
    assert engine.current_exercise == ex2

    # Advance with '\n'
    res = engine.handle_input_key("\n")
    assert res == ex3
    assert engine.current_exercise == ex3

    # Go back with 'p'
    res = engine.handle_input_key("p")
    assert res == ex2
    assert engine.current_exercise == ex2

    # Rerun with 'r'
    res = engine.handle_input_key("r")
    assert res == ex2

    # Request hint with 'h'
    res = engine.handle_input_key("h")
    assert res == ex2

    # Quit with 'q'
    with pytest.raises(KeyboardInterrupt):
        engine.handle_input_key("q")


def test_watcher_engine_next_prev_exercise(tmp_path: Path):
    """Verify next_exercise and prev_exercise sequence switching in WatchEngine."""
    f1 = tmp_path / "ex1.py"
    f1.write_text("assert False, 'ex1'\n")
    f2 = tmp_path / "ex2.py"
    f2.write_text("assert False, 'ex2'\n")

    ex1 = Exercise("ex1", "Ex 1", str(f1), "ch1")
    ex2 = Exercise("ex2", "Ex 2", str(f2), "ch1")

    manifest = Manifest(chapters=[Chapter(1, "ch1", "Ch 1", "Desc", [ex1, ex2])])
    engine = WatchEngine(manifest=manifest, runner=ExerciseRunner())

    assert engine.current_exercise == ex1

    # At start, prev_exercise should return None and keep current
    assert engine.prev_exercise() is None
    assert engine.current_exercise == ex1

    # next_exercise advances to ex2
    assert engine.next_exercise() == ex2
    assert engine.current_exercise == ex2

    # At end, next_exercise should return None
    assert engine.next_exercise() is None
    assert engine.current_exercise == ex2

    # prev_exercise returns to ex1
    assert engine.prev_exercise() == ex1
    assert engine.current_exercise == ex1


def test_find_next_incomplete_exercise_pure_validation(tmp_path: Path):
    """Verify find_next_incomplete_exercise evaluates strictly based on run_exercise passed status."""
    f1 = tmp_path / "ex1.py"
    f1.write_text("print('pass 1')\n")
    f2 = tmp_path / "ex2.py"
    f2.write_text("# I AM NOT DONE\nassert False, 'failed'\n")
    f3 = tmp_path / "ex3.py"
    f3.write_text("print('pass 3')\n")

    ex1 = Exercise("ex1", "Ex 1", str(f1), "ch1")
    ex2 = Exercise("ex2", "Ex 2", str(f2), "ch1")
    ex3 = Exercise("ex3", "Ex 3", str(f3), "ch1")

    manifest = Manifest(chapters=[Chapter(1, "ch1", "Ch 1", "Desc", [ex1, ex2, ex3])])
    runner = ExerciseRunner()

    next_ex = find_next_incomplete_exercise(manifest, runner)
    assert next_ex is not None
    assert next_ex.name == "ex2"

    # When ex2 passes, find_next_incomplete_exercise returns None
    f2.write_text("print('pass 2')\n")
    next_ex = find_next_incomplete_exercise(manifest, runner)
    assert next_ex is None
