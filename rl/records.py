"""Writing, reading and replaying game records (one JSON object per line)."""
from __future__ import annotations
import glob
import json
import os
from typing import Iterable, Iterator

from rl.root_game import RootGame, RECORD_FORMAT


class ReplayMismatch(AssertionError):
    pass


class GameRecordWriter:
    """Appends records to a .jsonl file, flushing each line so a crash loses at most one game."""

    def __init__(self, path: str) -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self.path = path
        self._file = open(path, "a", encoding="utf-8")

    def write(self, record: dict) -> None:
        self._file.write(json.dumps(record, separators=(",", ":")) + "\n")
        self._file.flush()

    def close(self) -> None:
        self._file.close()


def iter_records(paths: Iterable[str]) -> Iterator[tuple[str, int, dict]]:
    """Yields (file, line number, record) for every record in the given files/globs/directories."""
    files = []
    for p in paths:
        if os.path.isdir(p):
            files.extend(sorted(glob.glob(os.path.join(p, "**", "*.jsonl"), recursive=True)))
        else:
            files.extend(sorted(glob.glob(p)) or [p])
    for path in files:
        with open(path, encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    yield path, line_no, json.loads(line)


def replay(record: dict, check: bool = True, on_step=None) -> RootGame:
    """Recreate a game from its record. With ``check``, verify it matches what was recorded.

    ``on_step(game, action)`` is called before each recorded action is applied, which can be
    used to inspect the game state at every decision.
    """
    if record.get("format") != RECORD_FORMAT:
        raise ValueError(f"unsupported record format {record.get('format')}")
    game = RootGame(turn_limit=record["turn_limit"],
                    settle_terminal_rewards=record["settle_terminal_rewards"],
                    digest=check and record.get("obs_digest") is not None)
    game.reset(record["seed"])

    actors = record["actors"]
    for i, action in enumerate(record["actions"]):
        if game.done:
            raise ReplayMismatch(f"game ended after {i} decisions, record has {len(record['actions'])}")
        if check and game.current_agent != int(actors[i]):
            raise ReplayMismatch(
                f"decision {i}: faction {game.current_agent} to act, record says {actors[i]}")
        if on_step is not None:
            on_step(game, action)
        game.step(action)

    if check:
        if not game.done:
            raise ReplayMismatch("game did not end after the recorded actions")
        turn_order = [f.faction_id - 1 for f in game.gm.turn_order]
        if turn_order != record["turn_order"]:
            raise ReplayMismatch(f"turn order {turn_order} != {record['turn_order']}")
        result = game.result()
        if result != record["result"]:
            raise ReplayMismatch(f"result {result} != {record['result']}")
        if record.get("obs_digest") and game._hasher.hexdigest() != record["obs_digest"]:
            raise ReplayMismatch("observation digest differs")
    return game
