"""A lean, seeded, recordable wrapper around GameManager for RL training.

Differences from ``src.pettingzoo_env.RootEnv`` (the game rules and reward function are untouched):
  * Steps where the game needs no decision (``current_message is None``) are advanced
    internally instead of being handed to an agent whose action is then ignored.
  * Every reward ``_calculate_reward`` computes is credited to the faction it was computed for
    (``GameManager.pop_rewards``), rather than whichever agent happened to be selected.
  * Optionally, when the game ends every faction (not only the last active one) receives its
    final ``_calculate_reward`` so the win/loss bonus reaches all players
    (``GameManager.settle_terminal_rewards``; the bonus is given at most once per faction).
  * Every game is fully determined by its seed and action list, and produces a record that
    ``rl.records.replay`` can use to recreate and verify it.
"""
from __future__ import annotations
import hashlib

import numpy as np

from src.utils.global_state import reset_global_state
from src.utils.game_manager import GameManager
from src.utils.game_settings import GameSettings
from src.factions.marquise_de_cat import Marquise
from src.factions.eyrie_dynasties import EyrieDynasties
from src.factions.woodland_alliance import WoodlandAlliance
from src.factions.vagabond.vagabond import Vagabond
from src.controllers.base_controllers.action_decoder import Decoder

RECORD_FORMAT = 1
FACTION_NAMES = ["marquise", "eyrie", "woodland_alliance", "vagabond"]
NUM_FACTIONS = 4
OBS_DIM = 896
ACTION_DIM = 340


def faction_index(faction) -> int:
    # Faction ids are 1..4 in the same order as FACTION_NAMES
    return faction.faction_id - 1


class IllegalActionError(RuntimeError):
    pass


class RootGame:

    def __init__(self, turn_limit: int = 30, settle_terminal_rewards: bool = True, digest: bool = True) -> None:
        self.turn_limit = turn_limit
        self.settle_terminal_rewards = settle_terminal_rewards
        self.digest = digest
        self.gm: GameManager | None = None
        self.done = True

    # ---------------------------------------------------------------- lifecycle

    def reset(self, seed: int) -> None:
        self.seed = int(seed)
        reset_global_state(self.seed)

        # Same construction sequence as RootEnv.reset
        marquise = Marquise(controller=None)
        eyrie = EyrieDynasties(controller=None)
        woodland_alliance = WoodlandAlliance(controller=None)
        vagabond = Vagabond(controller=None)
        settings = GameSettings([marquise, eyrie, woodland_alliance, vagabond])
        self.gm = GameManager(settings, turn_limit=self.turn_limit)
        self.gm.compute_observations = False
        self.gm.reset_ids()
        self.gm.game_state.current_player = self.gm.setup_order[0]
        self.gm.game_state.active_player = self.gm.setup_order[0]

        self.done = False
        self.rewards = np.zeros(NUM_FACTIONS, dtype=np.float64)
        self.returns = np.zeros(NUM_FACTIONS, dtype=np.float64)
        self.actions: list[int] = []
        self.actors: list[int] = []
        self._hasher = hashlib.blake2b(digest_size=16) if self.digest else None
        self.obs = None
        self.mask = None
        self.current_agent = -1
        self._advance()

    def step(self, action: int) -> None:
        if self.done:
            raise RuntimeError("step() called on a finished game")
        action = int(action)
        if not self.mask[action]:
            raise IllegalActionError(
                f"action {action} not allowed for {FACTION_NAMES[self.current_agent]} "
                f"(seed {self.seed}, decision {len(self.actions)})")
        self.actions.append(action)
        self.actors.append(self.current_agent)
        self._gm_step(Decoder.decode(action, self.gm.current_message))
        self._advance()

    def pop_rewards(self) -> np.ndarray:
        """Rewards earned by each faction since the previous call."""
        rewards, self.rewards = self.rewards, np.zeros(NUM_FACTIONS, dtype=np.float64)
        return rewards

    # ---------------------------------------------------------------- internals

    def _gm_step(self, action) -> None:
        self.gm.step(action)
        self._collect_rewards()

    def _collect_rewards(self) -> None:
        # Every reward the step computed, credited to the faction it was computed for
        rewards = self.gm.pop_rewards()
        self.rewards += rewards
        self.returns += rewards

    def _advance(self) -> None:
        """Run the game forward until a faction must make a decision, or the game ends."""
        gm = self.gm
        while not gm.done:
            # Mirrors RootEnv: past the turn limit the next step ends the game, ignoring the action
            if gm.current_message is None or gm.turn_count >= gm.turn_limit:
                self._gm_step(None)
            else:
                break

        if gm.done:
            self._finish()
            return

        obs = gm.get_observation()
        self.obs = obs["observation"]
        self.mask = obs["action_mask"] > 0
        self.current_agent = faction_index(gm.game_state.active_player)
        if not self.mask.any():
            raise IllegalActionError(
                f"no legal actions for {FACTION_NAMES[self.current_agent]} on "
                f"{gm.current_message.type} (seed {self.seed}, decision {len(self.actions)})")
        if self._hasher is not None:
            self._hasher.update(self.obs.tobytes())
            self._hasher.update(self.mask.tobytes())

    def _finish(self) -> None:
        gm = self.gm
        if self.settle_terminal_rewards:
            # Final reward for every faction that has not yet had its end-of-game reward
            gm.settle_terminal_rewards()
            self._collect_rewards()
        self.done = True
        self.obs = None
        self.mask = None
        self.current_agent = -1

    # ---------------------------------------------------------------- recording

    def result(self) -> dict:
        gm = self.gm
        factions = sorted(gm.settings.faction_list, key=faction_index)
        winners = gm.winner if isinstance(gm.winner, list) else ([gm.winner] if gm.winner else [])
        return {
            "turns": gm.turn_count,
            "decisions": len(self.actions),
            "vp": [f.victory_points for f in factions],
            "winners": sorted(faction_index(w) for w in winners),
            "truncated": not winners,
            "returns": [round(float(r), 6) for r in self.returns],
        }

    def record(self, **meta) -> dict:
        """A compact description that is sufficient to recreate this game exactly."""
        if not self.done:
            raise RuntimeError("record() requires a finished game")
        return {
            "format": RECORD_FORMAT,
            "seed": self.seed,
            "turn_limit": self.turn_limit,
            "settle_terminal_rewards": self.settle_terminal_rewards,
            "turn_order": [faction_index(f) for f in self.gm.turn_order],
            "actions": self.actions,
            "actors": "".join(map(str, self.actors)),
            "obs_digest": self._hasher.hexdigest() if self._hasher is not None else None,
            "result": self.result(),
            "meta": meta,
        }
