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

_CALLBACK_TIMES = list(CallbackTimes)
_CALLBACK_PHASES = {time: time.get_phase() for time in CallbackTimes}


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
        self.game_state.turn_order = self.turn_order
        self.turn_count = 0
        self.current_message = None
        self.last_reward_player = None
        # Every reward _calculate_reward computes, per faction (index faction_id - 1), since the
        # last pop_rewards() call. A single step() can produce rewards for several factions
        self.pending_rewards = np.zeros(len(self.settings.faction_list), dtype=np.float64)
        # Factions that have already received their end-of-game (win/loss/turn limit) reward
        self._terminal_rewarded = set()
        self.compute_observations = True
        self.turn_limit = turn_limit
        # Item supply (5.1.5): 2 boots, 2 bags, 1 crossbow, 1 hammer, 2 swords, 2 teas, 2 coins
        self.craftable_items = [Items.BAG, Items.BAG, Items.BOOTS, Items.BOOTS, Items.SWORD, Items.SWORD, Items.HAMMER,
                                Items.TEA, Items.TEA, Items.COINS, Items.COINS, Items.CROSSBOW]
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
        obs["observation"] = ObservationSpace.encode_game_state(
            self.game_state, self.current_message.type if self.current_message else None, self.current_group).clip(0, 1).astype(np.float32)

        if self.current_message is not None:
            obs["action_mask"] = np.array(self.masker.create_mask(
                self.current_message)).clip(0, 1).astype(np.float32)
        else:
            obs["action_mask"] = np.zeros(
                self.masker.action_size, dtype=np.float32).clip(0, 1)
        return obs

    def _step_observation(self):
        # Encoding is the most expensive part of a step; callers that build their own
        # observation (e.g. rl.root_game) switch this off
        return self.get_observation() if self.compute_observations else None

    def _calculate_reward(self):
        reward = 0.0
        player = self.game_state.active_player
        # Lets callers attribute the returned reward to the right faction
        self.last_reward_player = player
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

        # End-of-game rewards are given at most once per faction, however many times the
        # reward is computed after the game has been decided
        game_decided = self.winner is not None or self.turn_count >= self.turn_limit
        if game_decided and player.faction_id not in self._terminal_rewarded:
            self._terminal_rewarded.add(player.faction_id)
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

            if self.turn_count >= self.turn_limit:
                reward -= 5
        self.logger.debug(
            f"{self.game_state.active_player} gained reward of {reward}")

        reward = np.clip(reward, -50, 50)
        self.pending_rewards[player.faction_id - 1] += reward
        return reward

    def pop_rewards(self) -> np.ndarray:
        """Rewards computed for each faction (index faction_id - 1) since the previous call.

        Unlike the reward returned by step(), which is only the last value computed (for
        last_reward_player), this includes every reward computed during the step, including
        those for action groups that ended without handing control to another faction."""
        rewards = self.pending_rewards
        self.pending_rewards = np.zeros_like(rewards)
        return rewards

    def settle_terminal_rewards(self) -> None:
        """Once the game is over, compute a final reward for every faction that has not had its
        end-of-game reward yet, so the win/loss bonus reaches all players (see pop_rewards)"""
        active_player = self.game_state.active_player
        last_reward_player = self.last_reward_player
        for faction in self.settings.faction_list:
            if faction.faction_id not in self._terminal_rewarded:
                self.game_state.active_player = faction
                self._calculate_reward()
        self.game_state.active_player = active_player
        self.last_reward_player = last_reward_player

    def _check_win_conditions(self):
        winners = []

        for faction in self.settings.faction_list:
            if faction.dominance and faction.faction_id != Factions.VAGABOND.value:
                needed_clearings = 2 if faction.dominance == Suits.BIRD else 3
                if faction.dominance == Suits.BIRD:
                    current_clearings = sum(1 if clearing.get_owner(
                    ) == faction.faction_id and clearing in self.game_state.board.corner_clearings else 0 for clearing in self.game_state.board.clearings)
                else:
                    current_clearings = sum(1 if clearing.get_owner() == faction.faction_id and clearing.get_suit(
                    ) == faction.dominance else 0 for clearing in self.game_state.board.clearings)

                self.logger.info(
                    f"{faction} is working towards {faction.dominance} dominance ({current_clearings}/{needed_clearings})")
            elif faction.dominance and faction.faction_id == Factions.VAGABOND.value:
                self.logger.info(
                    f"{faction} is in a coalition with {faction.dominance}")
            else:
                self.logger.info(f"{faction} VP: {faction.victory_points}")

        for faction in self.settings.faction_list:
            if faction.dominance and faction.has_won:
                winners.append(faction)
            elif faction.victory_points >= 30:
                winners.append(faction)

        # If multiple players win simultaneously, the player taking the current turn wins (3.1)
        current = self.game_state.current_player
        if len(winners) > 1 and current in winners:
            winners = [current]

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
            return self._step_observation(), self._calculate_reward(), True, {}

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
                            return self._step_observation(), self._calculate_reward(), False, {}
                    except StopIteration:
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
                    return self._step_observation(), self._calculate_reward(), False, {}
                else:
                    continue
            except StopIteration:
                self._advance_setup_index()
                if self.setup_complete:
                    return self._run_game_step(None)
                continue
        return self._step_observation(), self._calculate_reward(), False, {}

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
            current_time = _CALLBACK_TIMES[self.current_time_index]
            self.game_state.current_phase = _CALLBACK_PHASES[current_time]
            current_group_set = current_faction.actions[current_time]
            current_group = current_group_set[self.current_group_index]
            # The group being played is part of the observation
            self.current_group = current_group

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
                            return self._step_observation(), self._calculate_reward(), False, {}
                        else:
                            continue
                    except StopIteration:
                        self._check_win_conditions()
                        reward = self._calculate_reward()
                        self._advance_step_indexes()
                        # if self.current_faction_index != starting_faction_index:
                        #     return obs, reward, False, {}
                        continue
                else:
                    # There were no yields
                    self._check_win_conditions()
                    obs = self._step_observation()
                    reward = self._calculate_reward()
                    self._advance_step_indexes()
                    if self.current_faction_index != starting_faction_index:
                        return obs, reward, False, {}
                    continue

            # Iterate through turn order
            try:
                self.current_message = self.action_group_iter.send(action)
                if self.current_message is not None:
                    return self._step_observation(), self._calculate_reward(), False, {}
                else:
                    continue
            except StopIteration:
                self._check_win_conditions()
                obs = self._step_observation()
                reward = self._calculate_reward()
                self._advance_step_indexes()
                if self.current_faction_index != starting_faction_index:
                    return obs, reward, False, {}
                continue
        return self._step_observation(), self._calculate_reward(), True, {}

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
                current_faction.reset_turn_state()
                self.current_faction_index += 1
                if self.current_faction_index >= len(self.turn_order):
                    self.current_faction_index = 0
                    self.turn_count += 1
                    self.game_state.turn_count = self.turn_count
                    self.logger.info(f"Turn: {self.turn_count}")

    def _get_faction_by_id(self, faction_id: int) -> Faction:
        for faction in self.settings.faction_list:
            if faction.faction_id == faction_id:
                return faction
        return None

    def reset_ids(self):
        PieceWithID.reset_ids()
        # ActionGroupRegistry is not reset here: action group ids are assigned when the factions
        # are constructed (before the GameManager), so resetting it afterwards left the registry
        # empty and the observation's action group id feature always 0. It is reset before the
        # factions are built by src.utils.global_state.reset_global_state

    def get_current_faction(self):
        if self.setup_complete and self.current_faction_setup_index < len(self.setup_order):
            return self.setup_order[self.current_faction_setup_index]
        else:
            return self.turn_order[self.current_faction_index]
