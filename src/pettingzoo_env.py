import functools
from __future__ import annotations
from utils.root_types import Factions
from pettingzoo.utils.env import AECEnv
from pettingzoo.utils import wrappers
import numpy as np
from gym import spaces
from pettingzoo.utils import agent_selector
from utils.game_manager import GameManager
from utils.game_settings import GameSettings
from factions.marquise_de_cat import Marquise
from factions.eyrie_dynasties import EyrieDynasties
from factions.woodland_alliance import WoodlandAlliance
from factions.vagabond.vagabond import Vagabond
from utils.colour_utils import original_print
from controllers.base_controllers.action_decoder import Decoder

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from factions.faction import Faction


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

        action_size = 56
        obs_dim = 774
        self.action_spaces = {agent: spaces.Box(low=0, high=1, shape=(
            action_size,), dtype=np.float32) for agent in self.agents}

        self.observation_spaces = {agent: spaces.Box(low=0, high=1, shape=(
            obs_dim,), dtype=np.float32) for agent in self.agents}

        self.render_mode = render_mode

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]

    def observe(self, agent):
        return np.array(self.observations[agent])

    def reset(self, seed=None, options=None):
        self.agents = self.possible_agents[:]
        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self.terminations = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        # TODO: Maybe replace None with actual state/observation
        self.observations = {agent: None for agent in self.agents}

        # Set up Factions and Game Manager
        # TODO: Sort out valid controllers/decoders
        marquise = Marquise(controller=None)
        eyrie = EyrieDynasties(controller=None)
        woodland_alliance = WoodlandAlliance(controller=None)
        vagabond = Vagabond(controller=None)

        settings = GameSettings([marquise, eyrie, woodland_alliance, vagabond])
        self.gm = GameManager(settings, turn_limit=100)

        self.setup_agent_selector = agent_selector(
            [self._faction_to_agent(faction) for faction in settings.get_setup_order()])

        self.standard_agent_selector = agent_selector(
            [self._faction_to_agent(faction) for faction in settings.randomize_turn_order()])

        self.current_agent_selector = self._get_current_agent_selector()
        self.current_agent_selector.next()
        # TODO: Maybe remove - unsure
        self.gm.step()

    def render(self):
        for faction in self.gm.settings.faction_list:
            if faction.dominance:
                if faction.faction_id == Factions.VAGABOND.value:
                    original_print(
                        f"{faction} is in a coalition with {faction.dominance}")
                else:
                    original_print(
                        f"{faction} is working towards {faction.dominance.name.capitalize()} Dominance")
            else:
                original_print(f"{faction} VP: {faction.victory_points}")

    def step(self, action):

        if self.current_agent_selector == self.setup_agent_selector and self.gm.setup_complete:
            self.current_agent_selector = self._get_current_agent_selector()
            self.current_agent_selector.next()

        # Just means the program is done as all agents terminate at the same time
        if self.terminations[self.agent_selection] or self.truncations[self.agent_selection]:
            return self._was_dead_step(action)

        # Play move
        assert self.gm.current_message
        # Convert move into correct format
        action = Decoder.decode(action, self.gm.current_message.type,
                                self.gm.current_message.game_state, self.gm.current_message.action_group)
        obs, reward, done, info = self.gm.step(action)
        self.observations[self.agent_selection] = obs
        self.infos[self.agent_selection] = info
        self.rewards[self.agent_selection] += reward

        if done:
            self.terminations = {agent: True for agent in self.agents}

        # Change agent when the game master has a different agent to the env
        if self._faction_to_agent(self.gm.get_current_faction()) != self.agent_selection:
            self._cumulative_rewards[self.agent_selection] = 0
            self.agent_selection = self.current_agent_selector.next()
            self._accumulate_rewards()

        if self.render_mode == "human":
            self.render()

    def close(self):
        pass

    def _faction_to_agent(self, faction: Faction):
        faction_ids = {Factions.MARQUISE_DE_CAT.value: "marquise", Factions.EYRIE_DYNASTY.value: "eyrie",
                       Factions.WOODLAND_ALLIANCE.value: "woodland_alliance", Factions.VAGABOND.value: "vagabond"}
        return faction_ids[faction.faction_id]

    def _get_current_agent_selector(self):
        assert self.gm
        return self.standard_agent_selector if self.gm.setup_complete else self.setup_agent_selector
