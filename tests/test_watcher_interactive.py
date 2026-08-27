import pytest

from kubelings.manifest import get_manifest
from kubelings.watcher import WatcherState, handle_keypress


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
