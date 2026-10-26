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

`tests/data/golden_games.jsonl` holds 20 games (random legal actions) recorded with
`py -3.11 -m tools.bench_sim --games 20 --record ...`. The speedups below were verified
against games recorded with the original engine; the file was then regenerated after the
behaviour fixes in the last section, so it now guards that behaviour. Any change that makes
these games replay differently changes the game, the observations or the rewards.

## Simulator speedups (no behaviour change)

Single-core decisions per second, random legal actions:

| Change | Decisions/s |
|---|---|
| Original `RootEnv` | ~850 |
| `RootGame` (no fake "None" steps) | ~1,250 |
| Skip observations that `GameManager.step` computed and threw away, and the eagerly evaluated `.get` default in `RootEnv.observe` | ~2,500 |
| Faster `Clearing.get_owner`, cached ownership in Marquise wood searches, encoder constant lookups | ~3,700 |
| Per-space piece counts in the observation encoder | ~3,800 |

`RootEnv` (still used by `main.py`) benefits too: about 960 → 3,800 env steps/s (since the
fixes below, every `RootEnv` step is a real decision).

## Behaviour fixes

These were first left alone because they change behaviour, then fixed together; the golden
games were regenerated afterwards.

1. **Eyrie scored ~0 VP in every game** (even with random play for everyone), because of
   engine bugs rather than the rules:
   - Bird decree cards are wild, but the decree recruit/move/battle/build actions only
     matched clearings of exactly the card's suit. No clearing is a bird clearing, so the two
     Royal Viziers (both birds) could never be resolved and every Eyrie turn ended in
     turmoil before any roost was built.
   - Turmoil reset `decree_cards` but not the decree's actions in the daylight action
     groups, so every card ever added stayed on the decree.
   - Turmoil cancelled every daylight decree group, including ones already played that
     turn; the stale cancel flag then skipped that column on the next turn.
   - `DecreeBuildAction.can_perform` raised `TypeError` (`len(roosts < max_roosts)`), which
     the bare `except:` in `GameManager._run_game_step` silently turned into skipping the
     group. `GameManager` now only catches `StopIteration`, so engine errors surface.
   - `DecreeBattleAction.perform` called `self.battle(...)` without `yield from`, so decree
     battles never happened.
   - `DecreeRecruitAction` used the `DECREE_MOVE_*` action ids.

   With random legal actions for every faction the Eyrie scored 0 VP in each of 10 diagnostic
   games and never built a second roost (decree action lists grew to 10-36 entries). After
   the fixes it averages 15.3 VP over 200 games (12.5 over the 20 golden games, winning 3).
2. **`RootEnv` gave agents the wrong observations.** `step` stored the new observation under
   the agent that had just acted and only updated `agent_selection` at the start of the next
   `step`, so the previous faction's policy chose with the new faction's mask. Agents were
   also asked to act on steps needing no decision, and the `rewards` dict was never cleared
   between steps. `RootEnv` now advances no-decision steps internally like `RootGame`; after
   every step `agent_selection` is the faction the game is waiting on, `observe` returns its
   observation and mask (other agents get an all-zero mask), and `rewards` holds this step's
   rewards per faction. `tests/test_pettingzoo_env.py` checks this, that `RootEnv` and
   `RootGame` play identical games, and that it runs under Tianshou's `PettingZooEnv`.
3. **Rewards were discarded and only reached the last active faction.**
   `GameManager._run_game_step` computed `_calculate_reward` (which advances `prev_vp`) on
   several paths and threw the value away, so VP gained there was never rewarded. Every
   computed reward is now accumulated per faction and read with `GameManager.pop_rewards()`
   (the reward returned by `step` is unchanged: the last value computed). The end-of-game
   reward (win/loss bonus, turn-limit penalty) is given at most once per faction, and
   `GameManager.settle_terminal_rewards()` gives it to every faction that has not had it
   (used by `RootGame` and `RootEnv` with `settle_terminal_rewards`, the default). Because the
   reward includes a potential-VP shaping term on every computation, factions now also
   receive that term at the end of each action group, not only at decisions.
4. **Observation features that saturated or never changed** (OBS_DIM is still 896). These
   were found by recording the unclipped encoding over 20 random games:
   - Piece locations were `(index + 1) / 12 + 1`, always above 1, so every placed piece
     clipped to `1.0`. They are now `(index + 1) / 12`, with `0` meaning not on the board.
   - Turn-order features were `faction_list.index(f) / 4 - 1` (always ≤ 0, and
     `faction_list` is not the turn order). They are now the position in
     `GameManager.turn_order` (as `game_state.turn_order`) scaled to [0, 1].
   - The Woodland Alliance base features reused the last sympathy loop index as a piece ID
     and were always 0. Each base's location is now read from `woodland_alliance.bases`.
   - `game_state.turn_count` and `game_state.current_phase` were never updated (constant 0
     and Birdsong); `CallbackTimes.get_phase` always returned Birdsong.
   - `GameManager.current_group` was never set, so the action-group section (group id,
     ordered, can abort, uses, available actions) was always 0.
   - `GameManager.reset_ids` reset `ActionGroupRegistry` after the factions had registered
     their groups, so the group id feature divided by an empty registry.

   Still clipped, but left alone because they are only out of range at the extremes: VP / 30
   (above 30 VP), the battle roll / 3 (rolls plus extra hits above 3) and the raw battle
   damage modifiers (`-999` means "ignore hits").
5. **The Rainbow setup in `main.py` used `num_atoms=340`** (the action count). `main.py`
   and `NNController` now share the standard 51 atoms (v_min -10, v_max 25). Checkpoints
   trained with 340 atoms no longer load.
