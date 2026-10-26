"""Recorded games must replay identically: guards determinism and simulator optimisations.

tests/data/golden_games.jsonl was recorded (random legal actions) before the simulator was
optimised; every observation, reward total and final result must still match it exactly.
"""
import os

import numpy as np
import pytest

from rl.records import iter_records, replay
from rl.root_game import RootGame

GOLDEN = os.path.join(os.path.dirname(__file__), "data", "golden_games.jsonl")


@pytest.mark.parametrize("path,line_no,record", list(iter_records([GOLDEN])),
                         ids=lambda v: str(v) if isinstance(v, int) else None)
def test_golden_game_replays(path, line_no, record):
    replay(record)


def _play(seed, action_seed):
    rng = np.random.default_rng(action_seed)
    game = RootGame()
    game.reset(seed)
    while not game.done:
        game.step(int(rng.choice(np.flatnonzero(game.mask))))
    return game.record()


def test_game_is_independent_of_previous_games():
    first = _play(seed=123, action_seed=1)
    _play(seed=999, action_seed=2)  # leaves global state behind
    again = _play(seed=123, action_seed=1)
    assert first == again
    replay(first)
