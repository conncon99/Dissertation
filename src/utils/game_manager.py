from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from utils.game_settings import GameSettings
    from factions.faction import Faction
from board.classic_map import ClassicMap
from utils.root_types import Items, GamePhase, Suits
from utils.callback_handler import CallbackTimes
from cards.deck import Deck
from utils.game_state import GameState
from utils.colour_utils import set_print_colour


class GameManager:

    def __init__(self, settings: 'GameSettings') -> None:
        self._initialized = True
        self.settings = settings
        self.winner = None
        self.game_phase = GamePhase.BIRDSONG
        self.deck = Deck()
        self.game_state = GameState()
        self.setup_game()
        self.create_map()
        self._initialize_game_state()
        self.run_game()

    def create_map(self):
        self.map = ClassicMap(self.settings)
        for factions in self.settings.faction_list:
            factions.setup_faction(self.map, self.deck)

    def setup_game(self):
        self.deck.shuffle()
        for factions in self.settings.faction_list:
            factions.hand.extend(self.deck.draw(3))

    def run_game(self):
        """Runs the game until completion"""
        while not self.winner:
            turn_order = self.settings.randomize_turn_order()
            for faction in turn_order:
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
                # faction.add_vp(1)
        if len([self.winner]) == 1:
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
                print(f"{faction} has dominance")
            else:
                print(f"{faction} VP: {faction.victory_points}")

            if faction.dominance and faction.has_won:
                potential_winners.append(faction)
            elif faction.victory_points >= 30:
                potential_winners.append(faction)

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
