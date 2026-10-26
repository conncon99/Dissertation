"""Benchmark the simulator by playing games with uniformly random legal actions.

    py -3.11 -m tools.bench_sim --games 20                       # time RootGame
    py -3.11 -m tools.bench_sim --games 50 --record golden.jsonl # also record the games
    py -3.11 -m tools.bench_sim --env                            # time the PettingZoo RootEnv
"""
import argparse
import time

import numpy as np


def play_root_game(game, seed, rng):
    game.reset(seed)
    while not game.done:
        game.step(int(rng.choice(np.flatnonzero(game.mask))))
    return len(game.actions)


def play_env(env, rng):
    env.reset()
    steps = 0
    while env.agents:
        legal = np.flatnonzero(env.observe(env.agent_selection)["action_mask"])
        env.step(int(rng.choice(legal)) if len(legal) else 0)
        steps += 1
    return steps


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=20)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--record", default=None, help="write game records to this .jsonl file")
    ap.add_argument("--env", action="store_true", help="benchmark RootEnv instead of RootGame")
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    t = time.perf_counter()
    if args.env:
        from src.pettingzoo_env import RootEnv
        np.random.seed(args.seed)
        env = RootEnv()
        total = sum(play_env(env, rng) for _ in range(args.games))
    else:
        from rl.root_game import RootGame
        from rl.records import GameRecordWriter
        game = RootGame()
        writer = GameRecordWriter(args.record) if args.record else None
        total = 0
        for i in range(args.games):
            total += play_root_game(game, args.seed * 1_000_003 + i, rng)
            if writer:
                writer.write(game.record(source="bench_sim", game=i))
        if writer:
            writer.close()
    dt = time.perf_counter() - t
    print(f"{args.games} games, {total} steps, {dt:.2f}s, {total / dt:.0f} steps/s, {args.games / dt:.2f} games/s")
