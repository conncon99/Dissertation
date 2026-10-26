# Parallel PPO training and game recording

All commands are run from the repository root with the Python that has CUDA torch
installed (`py -3.11` on this machine).

```bash
py -3.11 -m rl.train_ppo --run-name my_run                     # train (Ctrl+C saves and stops)
py -3.11 -m rl.train_ppo --resume runs/my_run/checkpoints/latest.pt
py -3.11 -m tensorboard.main --logdir runs                     # watch training
py -3.11 -m rl.evaluate runs/my_run/checkpoints/latest.pt --games 500
py -3.11 -m rl.replay runs/my_run/games                        # verify every recorded game
py -3.11 -m rl.replay runs/my_run/games/worker_000.jsonl --show 3   # step through one game
py -3.11 -m tools.bench_sim --games 20                         # simulator speed
py -3.11 -m pytest tests                                       # determinism + GAE tests
```

`py -3.11 -m rl.train_ppo --help` lists every hyperparameter.

## What runs where

| Component | Process | Notes |
|---|---|---|
| `rl/root_game.py` `RootGame` | worker | One seeded game; skips steps that need no decision; credits rewards to the faction they were computed for |
| `rl/vec_env.py` | workers + trainer | One game per worker process (the engine keeps module-level state, so processes isolate games). Observations, masks and rewards go through shared memory; signalling uses OS semaphores |
| `rl/model.py` | trainer (GPU) | Separate actor and critic MLPs per faction, stored as an ensemble so a batch with mixed factions is one batched matmul per layer |
| `rl/ppo.py` | trainer | Asynchronous collection (whichever games are waiting are batched onto the GPU), per-faction GAE, clipped PPO with masked logits |

Default: `6 x CPU threads` workers (96 here). On the RTX 4070 Ti SUPER / 16-thread machine this
collects about 32k decisions/s and trains at about 25k decisions/s overall (including the PPO update).
For comparison, the original single-process `RootEnv` managed about 850 real decisions/s.

### Multi-agent bookkeeping

Factions act in an irregular order, so each faction's transitions inside a game form a chain
(`Rollout.next_idx`). Rewards arriving between two of a faction's decisions are added to its
latest transition. At the end of a rollout, unfinished chains are bootstrapped with that
faction's critic on the current state. Advantages are normalised per faction.

Rewards are scaled per faction by a running estimate of the discounted return's standard
deviation (`--no-normalize-rewards` disables it).

## Game records

Each finished game is one JSON line in `runs/<run>/games/worker_XXX.jsonl`. When a file
passes 64 MB it is compressed into `worker_XXX.NNNNN.jsonl.gz` (about 1 KB per game). A
record contains:

| Field | Meaning |
|---|---|
| `seed` | Seeds numpy's global RNG at game start. All randomness in the engine comes from it |
| `turn_limit`, `settle_terminal_rewards` | Game settings |
| `actions` | The action index chosen at each decision |
| `actors` | Which faction (0 marquise, 1 eyrie, 2 alliance, 3 vagabond) made each decision |
| `turn_order` | Faction order (checked on replay) |
| `obs_digest` | BLAKE2 hash of every observation and mask seen, so replays are verified exactly |
| `result` | Turns, VP, winners and total reward per faction |
| `meta` | Worker, session, game index and the policy update in use when the game started and ended |

`rl.records.replay(record)` rebuilds the game from the seed and actions and raises
`ReplayMismatch` if anything differs. Pass `on_step=` to inspect the game state at every
decision. Games that crash the engine are written to `games/errors/` with a traceback, and
`replay(record, check=False)` reproduces the crash.

Making games reproducible required three engine fixes. None of them changes the rules:
- **Shared global state.** Card singletons (`owner`, `action`, `game_state`) and the
  `PieceWithID`/`ActionGroupRegistry` registries carried state from one game into the next.
  `src/utils/global_state.reset_global_state` restores them before each game.
- **Unstable set ordering.** `Space` objects hashed by memory address, so iteration over
  `set`s of clearings varied between runs. That changed Woodland Alliance and Eyrie
  potential-VP rewards. Spaces now hash by board index.
- **Unreliable `RootEnv.reset` order.** `RootEnv.reset` cleared the ID registries after
  building pieces, so piece IDs depended on the previous game. `RootGame` resets them before
  building as well.

`tests/data/golden_games.jsonl` was recorded with the original engine code. Its games still
replay bit-for-bit, which shows the speedups did not change behaviour.

## Simulator speedups (no behaviour change)

Single-core decisions per second, random legal actions:

| Change | Decisions/s |
|---|---|
| Original `RootEnv` | ~850 |
| `RootGame` (no fake "None" steps) | ~1,250 |
| Skip observations that `GameManager.step` computed and threw away, and the eagerly evaluated `.get` default in `RootEnv.observe` | ~2,500 |
| Faster `Clearing.get_owner`, cached ownership in Marquise wood searches, encoder constant lookups | ~3,700 |
| Per-space piece counts in the observation encoder | ~3,800 |

`RootEnv` (still used by `main.py`) benefits too: about 960 → 3,000 env steps/s.

## Issues found but deliberately not changed

Fixing these would change behaviour, so it's your call:

1. **`RootEnv` gives agents stale or wrong observations.** `step` stores the new observation
   under the agent that just acted, but `agent_selection` only updates at the start of the
   next `step`. So when the turn passes to another faction, the previous faction's policy
   picks an action using the new faction's mask, and that action is then played for the new
   faction. Agents are also asked to act on steps where `current_message is None`, and those
   actions are ignored. `RootGame` avoids both problems.
2. **Only the last active faction receives the end-of-game win/loss reward** from
   `GameManager`. `RootGame` (with `settle_terminal_rewards`, the default) runs
   `_calculate_reward` once more for each other faction when the game ends.
3. **Rewards computed on paths that `continue` are discarded**
   (`GameManager._run_game_step`). `_calculate_reward` still updates `prev_vp`, so VP gained
   there never shows up as reward.
4. **Most observation features saturate:**
   - `_encode_id_clearing` returns `(index + 1) / 12 + 1`, which is always above 1, so after
     `clip(0, 1)` every placed piece encodes as `1.0` and its location is lost.
   - The turn-order features (`index / 4 - 1`) are always ≤ 0, so they clip to `0`.
5. **The Woodland Alliance base features reuse the last loop index** from the sympathy loop
   (`_encode_woodland_alliance_data`), so they look up the wrong base IDs.
6. **The Rainbow setup in `main.py` uses `num_atoms=340`** (the usual value is 51). With
   340 actions that makes the final layer about 59M weights per agent.
