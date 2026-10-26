"""Verify recorded games, or step through one of them.

    py -3.11 -m rl.replay runs/<run>/games                 # verify every game
    py -3.11 -m rl.replay runs/<run>/games --limit 100     # verify the first 100
    py -3.11 -m rl.replay runs/<run>/games/worker_00.jsonl --show 3   # print game on line 3
"""
from __future__ import annotations
import argparse
import sys
import time

from rl.records import iter_records, replay, ReplayMismatch
from rl.root_game import FACTION_NAMES


def _print_step(game, action):
    msg = game.gm.current_message
    from src.controllers.base_controllers.action_decoder import Decoder
    print(f"[turn {game.gm.turn_count:>2}] {FACTION_NAMES[game.current_agent]:<17} "
          f"{msg.type.name:<32} action {action:>3} -> {Decoder.decode(action, msg)}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", help=".jsonl files, globs or directories")
    ap.add_argument("--limit", type=int, default=None, help="verify at most this many games")
    ap.add_argument("--show", type=int, default=None, metavar="LINE",
                    help="print every decision of the game on this line (single file only)")
    args = ap.parse_args(argv)

    if args.show is not None:
        for path, line_no, record in iter_records(args.paths):
            if line_no == args.show:
                print(f"{path}:{line_no} seed={record['seed']} meta={record['meta']}")
                game = replay(record, on_step=_print_step)
                print("result:", game.result())
                return 0
        print("no such game", file=sys.stderr)
        return 1

    ok = bad = 0
    t = time.perf_counter()
    for path, line_no, record in iter_records(args.paths):
        if args.limit is not None and ok + bad >= args.limit:
            break
        try:
            replay(record)
            ok += 1
        except (ReplayMismatch, Exception) as err:  # report and keep going
            bad += 1
            print(f"MISMATCH {path}:{line_no} seed={record.get('seed')}: {err!r}")
    print(f"{ok} games replayed identically, {bad} mismatched ({time.perf_counter() - t:.1f}s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
