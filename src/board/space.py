from __future__ import annotations
from typing import Dict, TYPE_CHECKING, List
from src.utils.root_types import Factions
if TYPE_CHECKING:
    from src.utils.game_settings import GameSettings
    from src.pieces.pawn import Pawn
    from src.board.clearing import Clearing
    from src.board.forest import Forest
    from src.utils.game_state import GameState


class Space:
    """"""

    # Change to make it a list of units
    def __init__(self, index: int, game_state: GameState) -> None:
        self.game_state = game_state
        self.units: Dict[int, List[Pawn]] = {
            faction.faction_id: [] for faction in self.game_state.faction_list}
        self.index = index
        self.adjacent_clearings: List[Clearing] = []
        self.adjacent_forests: List[Forest] = []
