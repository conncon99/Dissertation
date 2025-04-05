from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from utils.game_settings import GameSettings
    from factions.faction import Faction
from board.classic_map import ClassicMap
from utils.root_types import Items, GamePhase, Suits, Factions
from utils.callback_handler import CallbackTimes
from cards.deck import Deck
from utils.game_state import GameState
from utils.colour_utils import set_print_colour, RESET, original_print
from actions.cards.claim_dominance_action import ClaimDominanceAction
from controllers.nn_controllers.marquise_nn_controller import MarquiseNNController
from controllers.nn_controllers.observation_space_encoder import ObservationSpace
from actions.action_group_registry import ActionGroupRegistry
from pieces.piece_with_id import PieceWithID
import itertools

from utils.root_types import GamePhase


class GameManager:

    def __init__(self, settings: GameSettings, turn_limit: int, training_mode=False) -> None:
        self._initialized = True
        self.settings = settings
        self.winner = None
        self.done = False
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
        self.last_faction = None
        self.time_iterator = None
        self.action_group_iterator = None
        self.current_faction = None
        self.current_time = None
        self.current_group = None
        self.group_generator = None
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

        self.faction_setup_iter = iter([
            (faction, faction.setup_faction(
                self.game_state.board, self.game_state.deck, self.game_state))
            for faction in self.settings.faction_list
        ])
        # print("[DEBUG] Factions being set up:", [
        #       type(f).__name__ for f, _ in self.faction_setup_iter])

        self.pending_setup_faction = None
        self.pending_setup_gen = None

        for faction in self.game_state.faction_list:
            for action_group in faction.actions[CallbackTimes.IN_DAYLIGHT]:
                action_group.actions.append(ClaimDominanceAction())

    def setup_game(self):
        self.deck.shuffle()
        for faction in self.settings.faction_list:
            faction.hand.extend(self.deck.draw(3))

    def reset(self):
        self.turn_count = 0
        self.done = False
        self.winner = None
        self.setup_complete = False
        self._initialize_game_state()
        self.create_map()
        self.setup_game()
        self._initialize_faction_setup()
        self.group_generator = None
        self.faction_iterator = None
        self.last_faction = None
        return self._run_setup_step()


### * Iterators ###

# Iterate through factions ->
# For each faction, iterate through each Callback Time
# For each Callback Time, iterate through each action group
# For each action group, iterate through each action (where an ActionChoiceMessage counts as a distinct step)
# For each action, iterate through each step of it (whenever send_game_message() is called)

    def _run_setup_step(self, action=None):
        if not hasattr(self, 'faction_setup_iter'):
            self._initialize_faction_setup()
        if self.pending_setup_gen:
            if action is not None:
                self.current_faction.controller.inject_action(action)
                response = self.current_faction.controller.send_game_message(
                    self.current_message)
                try:
                    self.current_message = self.pending_setup_gen.send(
                        response)
                    return self._get_observation(), 0.0, False, {}
                except StopIteration:
                    self.pending_setup_gen = None

        while not self.setup_complete:
            try:
                faction, gen = next(self.faction_setup_iter)
                self.current_faction = faction
                self.game_state.current_player = self.current_faction
                set_print_colour(self.current_faction.print_colour)
                self.pending_setup_gen = gen
                self.current_message = next(gen, None)
                if self.current_message is not None:
                    return self._get_observation(), 0.0, False, {}
                else:
                    self.pending_setup_gen = None  # Setup was silent, skip to next
            except StopIteration:
                self.setup_complete = True
                self.faction_iterator = itertools.cycle(self.turn_order)
                self._advance_to_next_step()
                return self._get_observation(), 0.0, False, {}

    def _advance_to_next_step(self):
        if self.current_faction == self.turn_order[-1]:
            self.turn_count += 1
            if self.turn_count >= self.turn_limit:
                self.done = True
                return

        self.current_faction = next(self.faction_iterator)
        set_print_colour(self.current_faction.print_colour)
        self.phase_iterator = iter(CallbackTimes)
        self._advance_to_next_phase()

    def _advance_to_next_phase(self):
        try:
            self.current_phase = next(self.phase_iterator)
            self.group_iterator = iter(
                self.current_faction.actions[self.current_phase])
            self._advance_to_next_group()
        except StopIteration:
            self._advance_to_next_step()

    def _advance_to_next_group(self):
        try:
            self.current_group = next(self.group_iterator)
            self.group_generator = self.current_group.step_action_group(
                self.current_faction, self.game_state)
            self._advance_group_step()
        except StopIteration:
            print("Advancing to Next Phase")
            self._advance_to_next_phase()

    def _advance_group_step(self, action=None):
        if self.group_generator is None:
            self._advance_to_next_group()
            return

        try:
            if action is not None:
                self.current_faction.controller.inject_action(action)
                response = self.current_faction.controller.send_game_message(
                    self.current_message)
                self.current_message = self.group_generator.send(response)
            else:
                self.current_message = next(self.group_generator)
        except StopIteration:
            self._advance_to_next_group()

    def _get_observation(self):
        if self.current_message is None:
            return ObservationSpace.encode_game_state(self.game_state, None, self.current_group)
        return ObservationSpace.encode_game_state(
            self.game_state, self.current_message.type, self.current_group
        )

    def _calculate_reward(self):
        vp = self.current_faction.victory_points
        reward = vp - getattr(self.current_faction, '_last_vp', 0)
        self.current_faction._last_vp = vp
        return reward

    def _check_win_conditions(self):
        winners = []

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
        from controllers.messages.game_messages import GameMessages

        if self.done:
            return self._get_observation(), 0.0, True, {}

        if not self.setup_complete:
            return self._run_setup_step(action)

        if self.current_message is not None:
            assert action is not None, "Action must be provided when a decision is pending."
            self._advance_group_step(action)
        else:
            self._advance_group_step()

        self._check_win_conditions()

        done = self.done or (self.turn_count >= self.turn_limit)
        return self._get_observation(), self._calculate_reward(), done, {}

    def _handle_wins(self, current_faction: Faction):
        """Determines if anyone has won the game by reaching 30 VP. 
        If multiple people win at the same turn, the person whose turn it is wins"""
        potential_winners = []
        for faction in self.settings.faction_list:

            if faction.dominance:
                if faction.faction_id == Factions.VAGABOND.value:
                    print(f"{faction} is in a coalition with {faction.dominance}")
                else:
                    print(
                        f"{faction} is working towards {faction.dominance.name.capitalize()} Dominance")
            else:
                print(f"{faction} VP: {faction.victory_points}")

            if faction.dominance and faction.has_won:
                self.winner = faction
            elif faction.victory_points >= 30:
                self.winner = faction

    def _get_faction_by_id(self, faction_id: int) -> Faction:
        for faction in self.settings.faction_list:
            if faction.faction_id == faction_id:
                return faction
        return None

    def reset_ids(self):
        PieceWithID.reset_ids()
        ActionGroupRegistry.reset()
