from __future__ import annotations
from src.utils.root_types import Factions
from pettingzoo.utils.env import AECEnv
from pettingzoo.utils import wrappers
import numpy as np
from gymnasium.spaces import Box, Dict, Discrete
from src.utils.game_manager import GameManager
from src.utils.global_state import reset_global_state
from src.utils.game_settings import GameSettings
from src.factions.marquise_de_cat import Marquise
from src.factions.eyrie_dynasties import EyrieDynasties
from src.factions.woodland_alliance import WoodlandAlliance
from src.factions.vagabond.vagabond import Vagabond
from src.controllers.base_controllers.action_decoder import Decoder
import logging

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.factions.faction import Faction


class RootEnv(AECEnv):
    metadata = {
        "render_modes": ["human"],
        "name": "root_v0",
    }

    def __init__(self, render_mode=None, turn_limit=30, settle_terminal_rewards=True):
        """settle_terminal_rewards: when the game ends, every faction (not only the last one to
        act) receives its final reward, so the win/loss bonus reaches all players"""
        super().__init__()
        self.turn_limit = turn_limit
        self.settle_terminal_rewards = settle_terminal_rewards
        self._faction_id_to_agent = {
            Factions.MARQUISE_DE_CAT.value: "marquise", Factions.EYRIE_DYNASTY.value: "eyrie",
            Factions.WOODLAND_ALLIANCE.value: "woodland_alliance", Factions.VAGABOND.value: "vagabond"}

        self.possible_agents = ["marquise", "eyrie",
                                "woodland_alliance", "vagabond"]
        self.agents = self.possible_agents[:]
        self.logger = logging.getLogger()

        action_size = 340
        obs_dim = 896
        self.action_spaces = {agent: Discrete(
            action_size) for agent in self.agents}

        agent_obs_space = Dict({
            "observation": Box(low=0.0, high=1.0, shape=(obs_dim,), dtype=np.float32),
            "action_mask": Box(low=0.0, high=1.0, shape=(action_size,), dtype=np.float32)
        })

        self.observation_spaces = {
            agent: agent_obs_space for agent in self.agents}

        self.render_mode = render_mode
        self._zero_mask = np.zeros(action_size, dtype=np.float32)
        self._empty_observation = {"observation": np.zeros(obs_dim, dtype=np.float32),
                                   "action_mask": self._zero_mask}
        self.observations = {}

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]

    def observe(self, agent):
        """The observation for agent. Only agent_selection has a non-empty action mask; other
        agents get the observation from their last decision with an all-zero mask"""
        obs = self.observations.get(agent)
        if obs is None:
            return self._empty_observation
        if agent == self.agent_selection and not self.gm.done:
            return obs
        return {"observation": obs["observation"], "action_mask": self._zero_mask}

    def reset(self, seed=None, options=None):
        # Restores module-level card singletons and ID registries, and reseeds numpy if a
        # seed is given, so a game only depends on its seed and actions
        reset_global_state(seed)
        self.logger.debug("Reset Called")
        self.agents = self.possible_agents[:]
        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self.truncations = {agent: False for agent in self.agents}
        self.terminations = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        self.observations = {}

        # Set up Factions and Game Manager
        marquise = Marquise(controller=None)
        eyrie = EyrieDynasties(controller=None)
        woodland_alliance = WoodlandAlliance(controller=None)
        vagabond = Vagabond(controller=None)

        settings = GameSettings([marquise, eyrie, woodland_alliance, vagabond])
        self.gm = GameManager(settings, turn_limit=self.turn_limit)
        # Observations are only encoded for the faction that has to decide (in _advance)
        self.gm.compute_observations = False
        self.gm.reset_ids()

        self.agent_selection = self._faction_to_agent(
            settings.get_setup_order()[0])
        self.gm.game_state.current_player = self.gm.setup_order[0]
        self.gm.game_state.active_player = self.gm.setup_order[0]
        # Rewards computed during setup (before the first decision) are credited too
        self.rewards = self._rewards_dict(self._advance())
        self._accumulate_rewards()

    def render(self):
        for faction in self.gm.settings.faction_list:
            if faction.dominance:
                if faction.faction_id == Factions.VAGABOND.value:
                    print(
                        f"{faction} is in a coalition with {faction.dominance}")
                else:
                    print(
                        f"{faction} is working towards {faction.dominance.name.capitalize()} Dominance")
            else:
                print(f"{faction} VP: {faction.victory_points}")

    def step(self, action):
        # All agents terminate at the same time, so the game is over
        if self.terminations[self.agent_selection] or self.truncations[self.agent_selection]:
            self.agents = []
            return

        agent = self.agent_selection
        assert self._faction_to_agent(self.gm.game_state.active_player) == agent
        self.logger.debug(f"Agent Selection: {agent} Action: {action}")
        # The agent's earlier rewards were reported by the previous last()
        self._cumulative_rewards[agent] = 0

        if not self.observations[agent]["action_mask"][action]:
            self.logger.warning(f"Chosen action not allowed by mask!")
            rewards = np.zeros(len(self.possible_agents))
        else:
            self.gm.step(Decoder.decode(action, self.gm.current_message))
            rewards = self._advance()

        # Rewards produced by this step (including the steps advanced internally), credited
        # to the faction each one was computed for
        self.rewards = self._rewards_dict(rewards)
        self._accumulate_rewards()

        if self.render_mode == "human":
            self.render()

        if self.gm.done:
            self.agents = []
            for agent in self.possible_agents:
                self.logger.debug(
                    f"{agent} Cumulative Rewards: {self._cumulative_rewards[agent]}")

    def _advance(self) -> np.ndarray:
        """Run the game until a faction must make a decision (which becomes agent_selection)
        or the game ends, and return the rewards computed on the way (index faction_id - 1).

        Steps where no decision is needed (current_message is None) are played here instead of
        being handed to an agent whose action would be ignored."""
        gm = self.gm
        while not gm.done:
            # Past the turn limit the next step ends the game, ignoring the action
            if gm.current_message is None or gm.turn_count >= gm.turn_limit:
                gm.step(None)
            else:
                break
        rewards = gm.pop_rewards()

        if gm.done:
            if self.settle_terminal_rewards:
                gm.settle_terminal_rewards()
                rewards += gm.pop_rewards()
            if gm.turn_count >= gm.turn_limit:
                self.truncations = {agent: True for agent in self.possible_agents}
            else:
                self.terminations = {agent: True for agent in self.possible_agents}
            return rewards

        self.agent_selection = self._faction_to_agent(gm.game_state.active_player)
        self.observations[self.agent_selection] = gm.get_observation()
        return rewards

    def _rewards_dict(self, rewards: np.ndarray):
        return {self._faction_id_to_agent[i + 1]: float(r) for i, r in enumerate(rewards)}

    def close(self):
        pass

    def _faction_to_agent(self, faction: Faction):
        return self._faction_id_to_agent[faction.faction_id]
