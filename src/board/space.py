from __future__ import annotations
from typing import Dict, TYPE_CHECKING, List
from utils.root_types import Factions
if TYPE_CHECKING:
    from utils.game_settings import GameSettings
    from pieces.pawn import Pawn
    from board.clearing import Clearing
    from board.forest import Forest


class Space:
    """"""

    # Change to make it a list of units
    def __init__(self, index: int, settings: GameSettings) -> None:
        self.settings = settings
        self.units: Dict[int, List[Pawn]] = {
            faction_id: [] for faction_id in self.settings.faction_ids}
        self.index = index
        self.adjacent_clearings: List[Clearing] = []
        self.adjacent_forests: List[Forest] = []
