from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from utils.game_settings import GameSettings
    from factions.faction import Faction
from board.classic_map import ClassicMap
from utils.root_types import Items, GamePhase, Suits, Factions
from utils.callback_handler import CallbackTimes
from cards.deck import Deck
from utils.game_state import GameState
from utils.colour_utils import set_print_colour, RESET
from actions.cards.claim_dominance_action import ClaimDominanceAction


class GameManager:

    def __init__(self, settings: 'GameSettings') -> None:
        self._initialized = True
        self.settings = settings
        self.winner = None
        self.game_phase = GamePhase.BIRDSONG
        self.game_state = GameState()
        self.turn_count = -1
        self.create_map()
        self.setup_game()
        self._initialize_game_state()
        self.run_game()

    def create_map(self):
        self.map = ClassicMap(self.settings)
        self.deck = Deck(self.map)
        for faction in self.settings.faction_list:
            faction.setup_faction(self.map, self.deck)
            for action_group in faction.actions[CallbackTimes.IN_DAYLIGHT]:
                action_group.actions.append(ClaimDominanceAction())

    def setup_game(self):
        self.deck.shuffle()
        for faction in self.settings.faction_list:
            faction.hand.extend(self.deck.draw(3))

    def run_game(self):
        """Runs the game until completion"""
        while not self.winner:
            turn_order = self.settings.randomize_turn_order()
            self.turn_count += 1
            for faction in turn_order:
                set_print_colour(RESET)
                print(f"TURN {self.turn_count}")
                self.game_state.current_player = faction
                set_print_colour(faction.print_colour)
                for time in CallbackTimes:
                    self.game_phase = time.get_phase()
                    assert self.game_phase is not None
                    self.game_state.current_phase = self.game_phase
                    for action_group in faction.actions[time]:
                        if self.winner is not None:
                            break
                        action_group.run_group(faction, self.game_state)
                        self._handle_wins(faction)
                    faction.used_spanning_actions.clear()
        if not isinstance(self.winner, list):
            set_print_colour(self.winner.print_colour)
            print(f"{self.winner} has won")
        else:
            print("TIE")

    def get_game_phase(self) -> GamePhase:
        """Gets the current game phase"""
        return self.game_phase

    def _handle_wins(self, current_faction):
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
                potential_winners.append(faction)
            elif faction.victory_points >= 30:
                potential_winners.append(faction)

        for faction in self.settings.faction_list:
            if faction.faction_id == Factions.VAGABOND.value:
                if faction.dominance and faction.dominance in potential_winners:
                    potential_winners.append(faction)
                break

        if len(potential_winners) == 1:
            self.winner = potential_winners[0]
        elif len(potential_winners) > 1:
            if current_faction in potential_winners:
                self.winner = current_faction
            else:
                self.winner = potential_winners

    def _initialize_game_state(self):
        assert self.map is not None
        self.game_state.board = self.map
        self.game_state.faction_list = self.settings.faction_list
        self.game_state.deck = self.deck
        # TODO: Maybe pass game state to factions here
