"""Recorded games must replay identically: guards determinism and simulator optimisations.

tests/data/golden_games.jsonl holds games recorded with random legal actions
(tools.bench_sim --record); every observation, reward total and final result must still match
it exactly. Regenerate it only for an intended behaviour change.
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


def test_writer_rotates_to_gzip_and_reader_reads_both(tmp_path):
    from rl.records import GameRecordWriter
    records = list(iter_records([GOLDEN]))
    path = str(tmp_path / "worker_000.jsonl")
    writer = GameRecordWriter(path, rotate_bytes=20_000)
    for _, _, record in records:
        writer.write(record)
    writer.close()
    files = sorted(p.name for p in tmp_path.iterdir())
    assert any(f.endswith(".jsonl.gz") for f in files)
    assert [r for _, _, r in iter_records([str(tmp_path)])] == [r for _, _, r in records]
