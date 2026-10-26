from __future__ import annotations
from src.utils.root_types import Factions
from pettingzoo.utils.env import AECEnv
from pettingzoo.utils import wrappers
import numpy as np
from gymnasium.spaces import Box, Dict, Discrete
from src.utils.game_manager import GameManager
from src.utils.game_settings import GameSettings
from src.factions.marquise_de_cat import Marquise
from src.factions.eyrie_dynasties import EyrieDynasties
from src.factions.woodland_alliance import WoodlandAlliance
from src.factions.vagabond.vagabond import Vagabond
from src.utils.colour_utils import original_print
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

    def __init__(self, render_mode=None):
        super().__init__()

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

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]

    def observe(self, agent):
        return self.observations.get(agent, self.gm.get_observation())

    def reset(self, seed=None, options=None):
        if seed is not None:
            np.random.seed(seed)
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
        self.gm = GameManager(settings, turn_limit=30)
        self.gm.reset_ids()

        self.agent_selection = self._faction_to_agent(
            settings.get_setup_order()[0])
        self.gm.game_state.current_player = self.gm.setup_order[0]
        self.gm.game_state.active_player = self.gm.setup_order[0]
        self.observations[self.agent_selection] = self.gm.get_observation()

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

        if self.gm.game_state.active_player:
            self._update_agent_selection_from_gm()
        # Just means the program is done as all agents terminate at the same time
        if self.terminations[self.agent_selection] or self.truncations[self.agent_selection]:
            self.agents = []
            return

        self.logger.debug(f"Agent Selection: {self.agent_selection}")
        # Play move
        if not self.gm.current_message:
            self.logger.debug("Performing None Step")
            assert self._faction_to_agent(
                self.gm.game_state.active_player) == self.agent_selection
            obs, reward, done, info = self.gm.step(None)
            self.observations[self.agent_selection] = obs
            self.infos[self.agent_selection] = info
            self.rewards[self.agent_selection] += reward
            self._cumulative_rewards[self.agent_selection] += reward
        else:
            self.logger.debug(f"Action: {action}")
            mask = self.gm.masker.create_mask(self.gm.current_message)
            self.logger.debug(mask[action])
            if mask[action] == 0:
                self.logger.warning(f"Chosen action not allowed by mask!")
            else:
                assert self._faction_to_agent(
                    self.gm.game_state.active_player) == self.agent_selection
                # Convert move into correct format
                self.logger.debug("Mask Allows action")
                action = Decoder.decode(action, self.gm.current_message)
                self.logger.debug(f"Decoded Action: {action}")
                obs, reward, done, info = self.gm.step(action)
                self.observations[self.agent_selection] = obs
                self.infos[self.agent_selection] = info
                self.rewards[self.agent_selection] += reward
                self._cumulative_rewards[self.agent_selection] += reward

        if self.render_mode == "human":
            self.render()

        if self.gm.done:
            if self.gm.turn_count >= self.gm.turn_limit:
                self.truncations = {
                    agent: True for agent in self.possible_agents
                }
            else:
                self.terminations = {
                    agent: self.gm.done for agent in self.possible_agents}
            self.agents = []
            for agent in self.possible_agents:
                self.logger.debug(
                    f"{agent} Cumulative Rewards: {self._cumulative_rewards[agent]}")
            return None

    def close(self):
        pass

    def _update_agent_selection_from_gm(self):
        active_faction = self.gm.game_state.active_player
        self.agent_selection = self._faction_to_agent(active_faction)

    def _faction_to_agent(self, faction: Faction):
        faction_ids = {Factions.MARQUISE_DE_CAT.value: "marquise", Factions.EYRIE_DYNASTY.value: "eyrie",
                       Factions.WOODLAND_ALLIANCE.value: "woodland_alliance", Factions.VAGABOND.value: "vagabond"}
        return faction_ids[faction.faction_id]
