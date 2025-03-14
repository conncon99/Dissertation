from __future__ import annotations
from typing import List, TYPE_CHECKING
from utils.root_types import GamePhase

if TYPE_CHECKING:
    from factions.faction import Faction
    from board.map import Map
    from factions.marquise_de_cat import Marquise
    from factions.eyrie_dynasties import EyrieDynasties
    from factions.woodland_alliance import WoodlandAlliance
    from factions.vagabond.vagabond import Vagabond
    from cards.deck import Deck
    from utils.root_types import Items


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
