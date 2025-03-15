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


class GameManager:

    def __init__(self, settings: GameSettings, turn_limit: int, training_mode=False) -> None:
        self._initialized = True
        self.settings = settings
        self.winner = None
        self.done = False
        self.game_phase = GamePhase.BIRDSONG
        self.game_state = GameState()
        self.game_state.turn_limit = turn_limit
        self.turn_count = -1
        self.turn_limit = turn_limit
        self.craftable_items = [Items.BAG, Items.BAG, Items.BOOTS, Items.BOOTS, Items.SWORD, Items.SWORD, Items.HAMMER,
                                Items.HAMMER, Items.TEA, Items.TEA, Items.COINS, Items.COINS, Items.CROSSBOW, Items.CROSSBOW]
        self._initialize_game_state()
        self.create_map()
        self.setup_game()
        # self.run_game()

    def _initialize_game_state(self):
        self.game_state.faction_list = self.settings.faction_list
        self.game_state.turn_limit = self.turn_limit
        self.game_state.craftable_items = self.craftable_items
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
        self.deck = Deck(self.map)
        self.game_state.deck = self.deck
        for faction in self.game_state.faction_list:
            self.game_state.current_player = faction
            faction.setup_faction(self.map, self.deck, self.game_state)
            for action_group in faction.actions[CallbackTimes.IN_DAYLIGHT]:
                action_group.actions.append(ClaimDominanceAction())

    def setup_game(self):
        self.deck.shuffle()
        for faction in self.settings.faction_list:
            faction.hand.extend(self.deck.draw(3))

    def run_game(self):
        """Runs the game until completion"""
        turn_order = self.settings.randomize_turn_order()
        while not self.winner:
            self.turn_count += 1
            self.game_state.turn_count = self.turn_count
            print(f"TURN {self.turn_count}")
            for faction in turn_order:
                set_print_colour(RESET)
                self.game_state.current_player = faction
                set_print_colour(faction.print_colour)
                for time in CallbackTimes:
                    self.game_phase = time.get_phase()
                    assert self.game_phase is not None
                    self.game_state.current_phase = self.game_phase
                    for action_group in faction.actions[time]:
                        if self.winner is not None:
                            self.done = True
                            break
                        action_group.run_group(faction, self.game_state)
                        self._handle_wins(faction)
                    faction.used_spanning_actions.clear()
            if self.turn_count >= self.turn_limit:
                self.done = True
                # original_print(
                #     f"Turn count has reached {self.turn_limit}, cancelling game...")
                return
        set_print_colour(self.winner.print_colour)
        print(f"{self.winner} has won")

        for faction in self.settings.faction_list:
            if faction.faction_id == Factions.VAGABOND.value:
                if faction.dominance and faction.dominance.faction_id == self.winner.faction_id:
                    print(
                        f"{faction} has won through a coalition with {self.winner}")
                    break

    def get_game_phase(self) -> GamePhase:
        """Gets the current game phase"""
        return self.game_phase

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
