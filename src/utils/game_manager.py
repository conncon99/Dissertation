from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import numpy as np
if TYPE_CHECKING:
    from src.utils.game_settings import GameSettings
    from src.factions.faction import Faction
from src.board.classic_map import ClassicMap
from src.utils.root_types import Items, GamePhase, Factions, Suits
from src.utils.callback_handler import CallbackTimes
from src.utils.game_state import GameState
from src.utils.colour_utils import set_print_colour, RESET, original_print
from src.actions.cards.claim_dominance_action import ClaimDominanceAction
from src.controllers.nn_controllers.observation_space_encoder import ObservationSpace
from src.actions.action_group_registry import ActionGroupRegistry
from src.pieces.piece_with_id import PieceWithID
from src.controllers.nn_controllers.mask import Mask
from src.factions.vagabond.vagabond import Vagabond
import types
import itertools
import logging


class GameManager:

    def __init__(self, settings: GameSettings, turn_limit: int) -> None:
        self._initialized = True
        self.settings = settings
        self.winner = None
        self.done = False
        self.masker = Mask()
        self.game_phase = GamePhase.BIRDSONG
        self.game_state = GameState()
        self.game_state.turn_limit = turn_limit
        self.turn_order = self.settings.randomize_turn_order()
        self.turn_count = 0
        self.current_message = None
        self.turn_limit = turn_limit
        self.craftable_items = [Items.BAG, Items.BAG, Items.BOOTS, Items.BOOTS, Items.SWORD, Items.SWORD, Items.HAMMER,
                                Items.HAMMER, Items.TEA, Items.TEA, Items.COINS, Items.COINS, Items.CROSSBOW, Items.CROSSBOW]
        self.setup_complete = False
        self.current_group = None
        self.setup_order = []
        self.current_faction_setup_index = 0
        self.current_faction_index = 0
        self.current_time_index = 0
        self.current_group_index = 0
        self.faction_setup_iter = None
        self.action_group_iter = None
        self.logger = logging.getLogger()

        self._initialize_game_state()
        self.create_map()
        self.setup_game()
        self._initialize_faction_setup()

        self.faction_iterator = itertools.cycle(self.turn_order)

### * SETUP *###

    def _initialize_game_state(self):
        self.game_state.faction_list = self.settings.faction_list
        self.game_state.turn_limit = self.turn_limit
        self.game_state.craftable_items = self.craftable_items
        self.game_state.use_manual_rolling = self.settings.use_manual_rolling
        self.game_state.marquise = self._get_faction_by_id(
            Factions.MARQUISE_DE_CAT.value)
        self.game_state.eyrie_dynasties = self._get_faction_by_id(
            Factions.EYRIE_DYNASTY.value)
        self.game_state.woodland_alliance = self._get_faction_by_id(
            Factions.WOODLAND_ALLIANCE.value)
        self.game_state.vagabond = self._get_faction_by_id(
            Factions.VAGABOND.value)

    def create_map(self):
        self.map = ClassicMap(self.game_state)
        self.game_state.board = self.map
        from src.cards.deck import Deck
        self.deck = Deck(self.map, self.settings.use_manual_card_draw)
        self.game_state.deck = self.deck

    def _initialize_faction_setup(self):

        # self.faction_setup_iter = iter([
        #     (faction, faction.setup_faction(
        #         self.game_state.board, self.game_state.deck, self.game_state))
        #     for faction in self.settings.get_setup_order()
        # ])

        self.pending_setup_faction = None
        self.pending_setup_gen = None

        for faction in self.game_state.faction_list:
            for action_group in faction.actions[CallbackTimes.IN_DAYLIGHT]:
                action_group.actions.append(ClaimDominanceAction())

    def setup_game(self):
        self.setup_order = self.settings.get_setup_order()
        self.deck.shuffle()
        for faction in self.setup_order:
            faction.hand.extend(self.deck.draw(3))


### Iterators ###

# Iterate through factions ->
# For each faction, iterate through each Callback Time
# For each Callback Time, iterate through each action group
# For each action group, iterate through each action (where an ActionChoiceMessage counts as a distinct step)
# For each action, iterate through each step of it (whenever send_game_message() is called)

    def get_observation(self):
        obs = {}
        if self.current_message is None:
            obs["observations"] = ObservationSpace.encode_game_state(
                self.game_state, None, self.current_group).clip(0, 1).astype(np.float32)
            obs["action_mask"] = np.zeros(
                self.masker.action_size, dtype=np.float32).clip(0, 1)
            obs["action_mask"][59] = 1
            assert np.isfinite(obs["observations"]).all(
            ), f"observations has a NaN or inf: {obs['observations']}"
            assert np.isfinite(obs["action_mask"]).all(
            ), f"action mask has a NaN or inf: {obs['action_mask']}"
            self.logger.debug("No Message Available")
            return obs
        self.logger.debug(
            f"{self.game_state.active_player} Requiring message of type {self.current_message.type}")
        obs["observations"] = ObservationSpace.encode_game_state(
            self.game_state, self.current_message.type, self.current_group).clip(0, 1).astype(np.float32)

        obs["action_mask"] = np.array(self.masker.create_mask(
            self.current_message), dtype=np.float32).clip(0, 1)

        assert np.isfinite(obs["observations"]).all(
        ), f"observations has a NaN or inf: {obs['observations']}"
        assert np.isfinite(obs["action_mask"]).all(
        ), f"action mask has a NaN or inf: {obs['action_mask']}"

        enabled_actions = [i for i, val in enumerate(
            obs["action_mask"]) if val == 1]
        self.logger.debug(f"Enabled Actions: {enabled_actions}")

        return obs

    def _calculate_reward(self):
        reward = 0.0
        player = self.game_state.active_player
        # VP Reward
        if not player.dominance:
            vp_diff = player.victory_points - player.prev_vp
            player.prev_vp = player.victory_points
            reward += vp_diff
            player.last_vp_change = vp_diff
        elif player.faction_id == Factions.VAGABOND.value:
            if player.dominance.dominance:
                reward += player.dominance.last_dominance_change
            else:
                reward += player.dominance.last_vp_change
        else:
            if player.dominance != Suits.BIRD:
                dominance_clearings_ruled = sum(1 if clearing.get_owner() == player.faction_id and clearing.get_suit(
                ) == player.dominance else 0 for clearing in self.game_state.board.clearings)
                dominance_diff = (dominance_clearings_ruled -
                                  player.prev_dominance_clearings_controlled) * 10
                reward += dominance_diff
                player.prev_dominance_clearings_controlled = dominance_clearings_ruled
                player.last_dominance_change = dominance_diff
            else:

                dominance_clearings_ruled = sum(1 if clearing.get_owner(
                ) == player.faction_id and clearing in self.game_state.board.corner_clearings else 0 for clearing in self.game_state.board.clearings)
                dominance_diff = (
                    dominance_clearings_ruled - player.prev_dominance_clearings_controlled) * 10
                reward += dominance_diff
                player.prev_dominance_clearings_controlled = dominance_clearings_ruled
                player.last_dominance_change = dominance_diff

        # Potential VP Rewards

        if not player.dominance or player.dominance and player.faction_id == Factions.VAGABOND.value:
            DISCOUNT_FACTOR = 0.02
            REMAINING_TURN_MULTIPLIER = (
                len(CallbackTimes) - self.current_time_index)  # Potential is higher the earlier in your turn you are
            potential_reward = player.get_potential_vp(
                self.game_state) * DISCOUNT_FACTOR * REMAINING_TURN_MULTIPLIER
            self.logger.info(
                f"{player} has earned a potential reward of {potential_reward}")
            reward += potential_reward

        if isinstance(self.winner, list):
            if player in self.winner:
                reward += 20
            else:
                reward -= 5
        elif self.winner is not None:
            if player == self.winner:
                reward += 20
            else:
                reward -= 5
        self.logger.debug(
            f"{self.game_state.active_player} gained reward of {reward}")

        if self.turn_count >= self.turn_limit:
            reward -= 5

        return np.clip(reward, -50, 50)

    def _check_win_conditions(self):
        winners = []

        for faction in self.settings.faction_list:
            if faction.dominance and faction.faction_id != Factions.VAGABOND:
                needed_clearings = 2 if faction.dominance == Suits.BIRD else 3
                if faction.dominance == Suits.BIRD:
                    current_clearings = sum(1 if clearing.get_owner(
                    ) == faction.faction_id and clearing in self.game_state.board.corner_clearings else 0 for clearing in self.game_state.board.clearings)
                else:
                    current_clearings = sum(1 if clearing.get_owner() == faction.faction_id and clearing.get_suit(
                    ) == faction.dominance else 0 for clearing in self.game_state.board.clearings)

                self.logger.info(
                    f"{faction} is working towards {faction.dominance} dominance ({current_clearings}/{needed_clearings})")
            elif faction.dominance and faction.faction_id == Factions.VAGABOND:
                self.logger.info(
                    f"{faction} is in a coalition with {faction.dominance}")
            else:
                self.logger.info(f"{faction} VP: {faction.victory_points}")

        for faction in self.settings.faction_list:
            if faction.dominance and faction.has_won:
                winners.append(faction)
            elif faction.victory_points >= 30:
                winners.append(faction)

        # Coalition win check (for Vagabond)
        for faction in self.settings.faction_list:
            if faction.faction_id == Factions.VAGABOND.value and faction.dominance:
                coalition_partner = faction.dominance
                if coalition_partner in winners and faction not in winners:
                    winners.append(faction)

        if winners:
            self.winner = winners  # list of factions
            self.done = True

### * STEP *###

    def step(self, action=None):
        self.logger.debug("GM STEP")
        if self.done or self.turn_count >= self.turn_limit:  # If the game is already done, just return
            self.done = True
            return self.get_observation(), self._calculate_reward(), True, {}

        if not self.setup_complete:  # Handle Setup First
            return self._run_setup_step(action)
        else:  # Do normal step
            return self._run_game_step(action)

    def _run_setup_step(self, action):
        while not self.setup_complete:
            current_faction = self.setup_order[self.current_faction_setup_index]
            self.game_state.current_player = self.setup_order[self.current_faction_setup_index]
            self.game_state.active_player = current_faction
            set_print_colour(current_faction.print_colour)

            if not self.faction_setup_iter:
                gen = iter(current_faction.setup_faction(
                    self.map, self.deck, self.game_state))

                if isinstance(gen, types.GeneratorType):
                    self.faction_setup_iter = gen
                    try:
                        self.current_message = next(self.faction_setup_iter)
                        if self.current_message is not None:
                            return self.get_observation(), self._calculate_reward(), False, {}
                    except:
                        # Faction setup completed immediately
                        self._advance_setup_index()
                        if self.setup_complete:
                            return self._run_game_step(None)
                        continue
                else:
                    # There were no yields
                    self._advance_setup_index()
                    if self.setup_complete:
                        return self._run_game_step(None)
                    continue

            # Iterate through setup order
            try:
                self.current_message = self.faction_setup_iter.send(action)
                if self.current_message is not None:
                    return self.get_observation(), self._calculate_reward(), False, {}
                else:
                    continue
            except StopIteration:
                self._advance_setup_index()
                if self.setup_complete:
                    return self._run_game_step(None)
                continue
        return self.get_observation(), self._calculate_reward(), False, {}

    def _advance_setup_index(self):
        self.current_faction_setup_index += 1
        self.current_message = None
        self.faction_setup_iter = None
        if self.current_faction_setup_index >= len(self.setup_order):
            self.setup_complete = True

    def _run_game_step(self, action):
        starting_faction_index = self.current_faction_index
        while not self.done:
            current_faction = self.turn_order[self.current_faction_index]
            self.game_state.current_player = current_faction
            self.game_state.active_player = current_faction
            set_print_colour(current_faction.print_colour)
            current_time = list(CallbackTimes)[self.current_time_index]
            current_group_set = current_faction.actions[current_time]
            current_group = current_group_set[self.current_group_index]

            # Action Group handles messages here
            if not self.action_group_iter:
                gen = iter(current_group.step_action_group(
                    current_faction, self.game_state))

                if isinstance(gen, types.GeneratorType):
                    self.action_group_iter = gen
                    try:
                        self.current_message = next(self.action_group_iter)
                        self._check_win_conditions()
                        if self.current_message is not None:
                            return self.get_observation(), self._calculate_reward(), False, {}
                        else:
                            continue
                    except:
                        self._check_win_conditions()
                        obs = self.get_observation()
                        reward = self._calculate_reward()
                        self._advance_step_indexes()
                        # if self.current_faction_index != starting_faction_index:
                        #     return obs, reward, False, {}
                        continue
                else:
                    # There were no yields
                    self._check_win_conditions()
                    obs = self.get_observation()
                    reward = self._calculate_reward()
                    self._advance_step_indexes()
                    if self.current_faction_index != starting_faction_index:
                        return obs, reward, False, {}
                    continue

            # Iterate through turn order
            try:
                self.current_message = self.action_group_iter.send(action)
                if self.current_message is not None:
                    return self.get_observation(), self._calculate_reward(), False, {}
                else:
                    continue
            except StopIteration:
                self._check_win_conditions()
                obs = self.get_observation()
                reward = self._calculate_reward()
                self._advance_step_indexes()
                if self.current_faction_index != starting_faction_index:
                    return obs, reward, False, {}
                continue
        return self.get_observation(), self._calculate_reward(), True, {}

    def _advance_step_indexes(self):
        self.current_message = None
        current_faction = self.turn_order[self.current_faction_index]
        self.game_state.current_player = current_faction
        self.game_state.active_player = current_faction
        set_print_colour(current_faction.print_colour)
        current_time = list(CallbackTimes)[self.current_time_index]
        current_group_set = current_faction.actions[current_time]

        self.action_group_iter = None
        self.current_group_index += 1
        if self.current_group_index >= len(current_group_set):
            self.current_group_index = 0
            self.current_time_index += 1
            if self.current_time_index >= len(list(CallbackTimes)):
                self.current_time_index = 0
                self.current_faction_index += 1
                if self.current_faction_index >= len(self.turn_order):
                    self.current_faction_index = 0
                    self.turn_count += 1
                    self.logger.info(f"Turn: {self.turn_count}")

    def _get_faction_by_id(self, faction_id: int) -> Faction:
        for faction in self.settings.faction_list:
            if faction.faction_id == faction_id:
                return faction
        return None

    def reset_ids(self):
        PieceWithID.reset_ids()
        ActionGroupRegistry.reset()

    def get_current_faction(self):
        if self.setup_complete and self.current_faction_setup_index < len(self.setup_order):
            return self.setup_order[self.current_faction_setup_index]
        else:
            return self.turn_order[self.current_faction_index]
