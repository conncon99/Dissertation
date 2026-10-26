"""Asynchronous, shared-memory vector of RootGame worker processes.

Each worker runs exactly one game at a time in its own process. The engine keeps state in
module-level objects, so separate processes are what keep games isolated (and replayable).

All data moves through shared memory. A worker writes the next observation, mask, acting
faction and the rewards earned since its previous decision, sets its ``status`` flag and
releases the shared ``ready`` semaphore; the trainer finds every flagged game with one numpy
scan, writes their actions and releases each game's own semaphore. Workers never wait for
each other, so the trainer can batch whichever games are ready onto the GPU. (Pipes with
``multiprocessing.connection.wait`` were several times slower on Windows.)

This module must not import torch: it is the entry point of every worker process.
"""
from __future__ import annotations
import json
import multiprocessing as mp
import os
import time
import traceback
from multiprocessing.shared_memory import SharedMemory

import numpy as np

from rl.records import GameRecordWriter
from rl.root_game import RootGame, NUM_FACTIONS, OBS_DIM, ACTION_DIM

_QUIT = -1


def _layout(num_envs: int) -> dict:
    W, F = num_envs, NUM_FACTIONS
    return {
        "obs": ((W, OBS_DIM), np.float32),
        "mask": ((W, ACTION_DIM), np.bool_),
        "agent": ((W,), np.int64),
        "reward": ((W, F), np.float32),
        "done": ((W,), np.bool_),
        "action": ((W,), np.int64),
        # 1 while a worker's report is waiting for the trainer
        "status": ((W,), np.uint8),
        # Statistics of the game that just finished (valid when done)
        "ep_return": ((W, F), np.float32),
        "ep_vp": ((W, F), np.float32),
        "ep_win": ((W, F), np.bool_),
        "ep_decisions": ((W,), np.int32),
        "ep_turns": ((W,), np.int32),
        "ep_error": ((W,), np.bool_),
        # Trainer -> workers: current policy update, stored in game records
        "update": ((1,), np.int64),
    }


class SharedArrays:
    def __init__(self, num_envs: int, names: dict | None = None) -> None:
        self._shm = {}
        self.names = {}
        for key, (shape, dtype) in _layout(num_envs).items():
            size = max(1, int(np.prod(shape)) * np.dtype(dtype).itemsize)
            if names is None:
                shm = SharedMemory(create=True, size=size)
            else:
                shm = SharedMemory(name=names[key])
            self._shm[key] = shm
            self.names[key] = shm.name
            setattr(self, key, np.ndarray(shape, dtype=dtype, buffer=shm.buf))
            if names is None:
                getattr(self, key)[...] = 0

    def close(self, unlink: bool = False) -> None:
        for key in list(self._shm):
            delattr(self, key)
        for shm in self._shm.values():
            shm.close()
            if unlink:
                shm.unlink()
        self._shm.clear()


def game_seed(run_seed: int, session: int, worker: int, game: int) -> int:
    return int(np.random.SeedSequence([run_seed, session, worker, game]).generate_state(1)[0])


def _worker_main(worker: int, ready_sem, act_sem, names: dict, num_envs: int, cfg: dict) -> None:
    shared = SharedArrays(num_envs, names)
    game = RootGame(turn_limit=cfg["turn_limit"], settle_terminal_rewards=cfg["settle_terminal_rewards"])
    writer = GameRecordWriter(os.path.join(cfg["games_dir"], f"worker_{worker:03d}.jsonl")) if cfg["record"] else None
    errors = GameRecordWriter(os.path.join(cfg["games_dir"], "errors", f"worker_{worker:03d}.jsonl"))
    game_index = 0
    start_update = 0

    def new_game():
        nonlocal game_index, start_update
        while True:
            seed = game_seed(cfg["run_seed"], cfg["session"], worker, game_index)
            game_index += 1
            start_update = int(shared.update[0])
            try:
                game.reset(seed)
                game.pop_rewards()  # rewards before anyone's first decision have no transition
                return
            except Exception:
                errors.write({"seed": seed, "actions": [], "error": traceback.format_exc(),
                              "meta": {"worker": worker, "session": cfg["session"]}})

    def publish():
        shared.obs[worker] = game.obs
        shared.mask[worker] = game.mask
        shared.agent[worker] = game.current_agent
        shared.status[worker] = 1
        ready_sem.release()

    def finish(error: bool):
        result = game.result()
        shared.ep_return[worker] = result["returns"]
        shared.ep_vp[worker] = result["vp"]
        shared.ep_win[worker] = False
        shared.ep_win[worker, result["winners"]] = True
        shared.ep_decisions[worker] = result["decisions"]
        shared.ep_turns[worker] = result["turns"]
        shared.ep_error[worker] = error

    try:
        new_game()
        shared.reward[worker] = 0.0
        shared.done[worker] = False
        publish()
        while True:
            act_sem.acquire()
            action = int(shared.action[worker])
            if action == _QUIT:
                break
            error = None
            try:
                game.step(action)
            except Exception:
                error = traceback.format_exc()
            reward = game.pop_rewards()
            if error is not None or game.done:
                meta = {"worker": worker, "session": cfg["session"], "game": game_index - 1,
                        "start_update": start_update, "end_update": int(shared.update[0])}
                if error is not None:
                    # Seed + actions reproduce the crash with rl.records.replay(..., check=False)
                    errors.write({"format": 1, "seed": game.seed, "turn_limit": game.turn_limit,
                                  "settle_terminal_rewards": game.settle_terminal_rewards,
                                  "actions": game.actions, "actors": "".join(map(str, game.actors)),
                                  "error": error, "meta": meta})
                    finish(error=True)
                else:
                    if writer is not None:
                        writer.write(game.record(**meta))
                    finish(error=False)
                shared.reward[worker] = reward
                shared.done[worker] = True
                new_game()
            else:
                shared.reward[worker] = reward
                shared.done[worker] = False
            publish()
    except KeyboardInterrupt:
        pass
    finally:
        if writer is not None:
            writer.close()
        errors.close()
        shared.close()




class AsyncRootVecEnv:
    """Trainer-side handle on the worker processes."""

    def __init__(self, num_envs: int, games_dir: str, run_seed: int, turn_limit: int = 30,
                 settle_terminal_rewards: bool = True, record: bool = True, session: int | None = None) -> None:
        self.num_envs = num_envs
        self.session = int(time.time()) if session is None else session
        os.makedirs(os.path.join(games_dir, "errors"), exist_ok=True)
        cfg = {"turn_limit": turn_limit, "settle_terminal_rewards": settle_terminal_rewards,
               "record": record, "games_dir": games_dir, "run_seed": run_seed, "session": self.session}
        with open(os.path.join(games_dir, f"session_{self.session}.json"), "w") as f:
            json.dump({"num_envs": num_envs, **cfg}, f, indent=2)

        self.shared = SharedArrays(num_envs)
        self._cfg = cfg
        self._ctx = mp.get_context("spawn")
        self._ready = self._ctx.Semaphore(0)
        self._act = [None] * num_envs
        self._procs = [None] * num_envs
        self._restarts = 0
        self._closing = False
        self._last_check = time.monotonic()
        self.restarted: list[int] = []
        for w in range(num_envs):
            self._spawn(w)
        self._outstanding = np.ones(num_envs, dtype=np.bool_)

    def _spawn(self, w: int) -> None:
        cfg = dict(self._cfg)
        # A replacement worker must not reuse the seeds of the games its predecessor played
        cfg["session"] = self._cfg["session"] + 1_000_000 * self._restarts
        self._act[w] = self._ctx.Semaphore(0)
        self._procs[w] = self._ctx.Process(target=_worker_main, daemon=True,
                                           args=(w, self._ready, self._act[w], self.shared.names, self.num_envs, cfg))
        self._procs[w].start()

    @property
    def num_outstanding(self) -> int:
        return int(self._outstanding.sum())

    def set_update(self, update: int) -> None:
        self.shared.update[0] = update

    def _check_alive(self, max_restarts: int = 20) -> None:
        """Replace crashed workers. Their unfinished game is lost; ``restarted`` lists them."""
        self._last_check = time.monotonic()
        for w, p in enumerate(self._procs):
            if not p.is_alive() and self._closing:
                self._outstanding[w] = False
            elif not p.is_alive():
                self._restarts += 1
                if self._restarts > max_restarts:
                    raise RuntimeError(f"worker {w} exited with code {p.exitcode}; too many worker restarts")
                print(f"worker {w} exited with code {p.exitcode}; restarting it", flush=True)
                self.shared.status[w] = 0
                self.restarted.append(w)
                self._spawn(w)

    def poll(self, block: bool = True) -> np.ndarray:
        """Games that have reported a new decision (or finished) since they were last sent an action."""
        while True:
            if time.monotonic() - self._last_check > 5.0:
                self._check_alive()
            ready = np.flatnonzero(self._outstanding & (self.shared.status == 1))
            if len(ready) or not block or not self._outstanding.any():
                break
            # Each report releases the semaphore once; extra releases just cause an empty scan
            if not self._ready.acquire(timeout=5):
                self._check_alive()
        self.shared.status[ready] = 0
        self._outstanding[ready] = False
        return ready

    def drain(self) -> np.ndarray:
        """Wait for every game that is still computing; returns the ones that reported."""
        envs = []
        while self._outstanding.any():
            envs.append(self.poll())
        return np.concatenate(envs) if envs else np.empty(0, dtype=np.int64)

    def send(self, envs: np.ndarray, actions: np.ndarray) -> None:
        self.shared.action[envs] = actions
        self._outstanding[envs] = True
        for e in envs.tolist():
            self._act[e].release()

    def close(self) -> None:
        self._closing = True
        try:
            self.drain()
        except RuntimeError:
            pass
        self.shared.action[:] = _QUIT
        for sem in self._act:
            sem.release()
        for p in self._procs:
            p.join(timeout=10)
            if p.is_alive():
                p.terminate()
        self.shared.close(unlink=True)
