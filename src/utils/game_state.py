from __future__ import annotations
from typing import List, TYPE_CHECKING
from src.utils.root_types import GamePhase

if TYPE_CHECKING:
    from src.factions.faction import Faction
    from src.board.map import Map
    from src.factions.marquise_de_cat import Marquise
    from src.factions.eyrie_dynasties import EyrieDynasties
    from src.factions.woodland_alliance import WoodlandAlliance
    from src.factions.vagabond.vagabond import Vagabond
    from src.cards.deck import Deck
    from src.utils.root_types import Items, Suits
    from src.controllers.nn_controllers.battle_data import BattleData
    from src.board.clearing import Clearing
    from src.cards.card import Card


class GameState:
    # List of factions
    # Board state - where pieces are
    # Cards in discard
    # Cards in all hands
    # Cards still in deck?
    # Current Phase - Birdsong, Daylight, Evening
    # Current Turn - number and which faction's turn it is
    # Victory points
    # Dominance/other victory conditions
    def __init__(self):
        self.turn_count: int = 0
        self.turn_limit: int = 300
        self.current_player: Faction = None
        self.craftable_items: List[Items] = []
        self.current_phase: GamePhase = GamePhase.BIRDSONG
        self.faction_list: List[Faction] = []
        self.board: Map = None
        self.deck: Deck = None
        self.marquise: Marquise = None
        self.eyrie_dynasties: EyrieDynasties = None
        self.woodland_alliance: WoodlandAlliance = None
        self.vagabond: Vagabond = None
        self.battle_data: BattleData = None
        self.use_manual_rolling = False
        self.use_manual_card_draw = False
        self.active_player: Faction = None
        self.selected_clearing: Clearing = None
        self.selected_to_clearing: Clearing = None
        self.selected_faction: Faction = None
        self.selected_card: Card = None
        self.selected_suit: Suits = None
