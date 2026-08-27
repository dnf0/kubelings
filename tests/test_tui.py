"""Tests for Interactive Terminal TUI Dashboard."""

from kubelings.manifest import get_manifest
from kubelings.tui import TuiApp, TuiState


def test_tui_state_navigation():
    manifest = get_manifest()
    state = TuiState(manifest=manifest)
    assert state.selected_exercise_index == 0
    assert state.current_exercise.name == "pods01"

    # Navigation down
    state.move_down()
    assert state.selected_exercise_index == 1
    assert state.current_exercise.name == "pods02"

    # Navigation up
    state.move_up()
    assert state.selected_exercise_index == 0
    assert state.current_exercise.name == "pods01"


def test_tui_hint_toggle():
    manifest = get_manifest()
    state = TuiState(manifest=manifest)
    assert state.active_hint_index == 0

    state.reveal_next_hint()
    assert state.active_hint_index == 1


def test_tui_layout_generation():
    manifest = get_manifest()
    app = TuiApp(manifest=manifest)
    layout = app.generate_layout()
    assert layout is not None
