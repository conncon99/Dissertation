from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import numpy as np
if TYPE_CHECKING:
    from utils.game_settings import GameSettings
    from factions.faction import Faction
from board.classic_map import ClassicMap
from utils.root_types import Items, GamePhase, Factions
from utils.callback_handler import CallbackTimes
from cards.deck import Deck
from utils.game_state import GameState
from utils.colour_utils import set_print_colour, RESET, original_print
from actions.cards.claim_dominance_action import ClaimDominanceAction
from controllers.nn_controllers.marquise_nn_controller import MarquiseNNController
from controllers.nn_controllers.observation_space_encoder import ObservationSpace
from actions.action_group_registry import ActionGroupRegistry
from pieces.piece_with_id import PieceWithID
import types
import itertools

from utils.root_types import GamePhase


class GameManager:

    def __init__(self, settings: GameSettings, turn_limit: int, training_faction: Optional[Faction] = None) -> None:
        self._initialized = True
        self.settings = settings
        self.winner = None
        self.done = False
        self.training_faction = training_faction
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

    def get_observation(self):  # TODO: Make get_observation also return an action mask
        # print("Storing obs")
        if self.current_message is None:
            return ObservationSpace.encode_game_state(self.game_state, None, self.current_group).astype(np.float32)
        return ObservationSpace.encode_game_state(
            self.game_state, self.current_message.type, self.current_group
        ).astype(np.float32)

    def _calculate_reward(self):
        # vp = self.game_state.current_faction.victory_points
        # reward = vp - getattr(self.game_state.current_faction, '_last_vp', 0)
        # self.game_state.current_faction._last_vp = vp
        # return reward
        return 0.0

    def _check_win_conditions(self):
        winners = []

        for faction in self.settings.faction_list:
            if faction.dominance:
                if faction.faction_id == Factions.VAGABOND.value:
                    print(f"{faction} is in a coalition with {faction.dominance}")
                else:
                    print(
                        f"{faction} is working towards {faction.dominance.name.capitalize()} Dominance")
            else:
                print(f"{faction} VP: {faction.victory_points}")

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

        if self.done:  # If the game is already done, just return
            self.done = True
            return self.get_observation(), 0.0, True, {}

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
                            return self.get_observation(), 0.0, False, {}
                    except:
                        # Faction setup completed immediately
                        self._advance_setup_index()
                        continue
                else:
                    # There were no yields
                    self._advance_setup_index()
                    continue

            # Iterate through setup order
            try:
                self.current_message = self.faction_setup_iter.send(action)
                if self.current_message is not None:
                    return self.get_observation(), 0.0, False, {}
            except StopIteration:
                self._advance_setup_index()
                continue
        return self.get_observation(), 0.0, False, {}

    def _advance_setup_index(self):
        self.current_faction_setup_index += 1
        self.current_message = None
        self.faction_setup_iter = None
        if self.current_faction_setup_index >= len(self.setup_order):
            self.setup_complete = True

    def _is_training_faction(self, current_faction: Faction):
        return self.training_faction and self.training_faction.faction_id == current_faction.faction_id

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
                            return self.get_observation(), 0.0, False, {}
                    except:
                        self._check_win_conditions()
                        obs = self.get_observation()
                        reward = self._calculate_reward()
                        self._advance_step_indexes()
                        if self.current_faction_index != starting_faction_index:
                            return obs, reward, False, {}
                        continue
                else:
                    # There were no yields
                    self._check_win_conditions()
                    obs = self.get_observation()
                    reward = self._calculate_reward()
                    # TODO: Bug appearing where only first action group at a given time appears
                    self._advance_step_indexes()
                    if self.current_faction_index != starting_faction_index:
                        return obs, reward, False, {}
                    continue

            # Iterate through setup order
            try:
                self.current_message = self.action_group_iter.send(action)
                if self.current_message is not None:
                    return self.get_observation(), 0.0, False, {}
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
                    print(f"Turn: {self.turn_count}")

    def _get_faction_by_id(self, faction_id: int) -> Faction:
        for faction in self.settings.faction_list:
            if faction.faction_id == faction_id:
                return faction
        return None

    def reset_ids(self):
        PieceWithID.reset_ids()
        ActionGroupRegistry.reset()

    def get_current_faction(self):
        if self.setup_complete:
            return self.setup_order[self.current_faction_setup_index]
        else:
            return self.turn_order[self.current_faction_index]
