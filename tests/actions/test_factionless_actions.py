from src.actions.factionless.craft_action import CraftAction
from src.actions.factionless.move_action import MoveAction
from src.factions.faction import Faction
from unittest.mock import MagicMock
from src.controllers.random_controller import RandomController
from src.cards.deck import Deck
from src.pieces.pawn import Pawn
from src.utils.root_types import Suits
from src.board.map import Map
from src.board.classic_map import ClassicMap
from src.utils.game_settings import GameSettings
from src.utils.game_state import GameState
from src.factions.marquise_de_cat import Marquise

# TODO: Make these actual unit tests with decidable outcomes


# def test_crafting_action():
#     faction = MagicMock(spec=Faction)
#     faction.controller = RandomController()
#     deck = Deck()
#     faction.hand = []
#     faction.active_cards = []
#     faction.hand.extend(deck.draw(5))

#     faction.get_crafting_resources.return_value = {suit: 3 for suit in Suits}
#     craft_action = CraftAction("craft")
#     craft_action.perform(None, faction)


def test_move_action():
    faction = MagicMock(spec=Faction)
    marquise = Marquise(RandomController())
    game_settings = GameSettings(1, [marquise])
    map = ClassicMap(game_settings)
    game_state = GameState()
    game_state.faction_list = game_settings.faction_list
    game_state.board = map
    map.clearings[0].units = [Pawn(map.clearings[0], marquise), Pawn(map.clearings[0], marquise), Pawn(
        map.clearings[0], marquise), Pawn(map.clearings[0], marquise), Pawn(map.clearings[0], marquise)]
    move_action = MoveAction("move")
    assert move_action.can_perform(marquise, game_state)
    move_action.perform(game_state, marquise)
