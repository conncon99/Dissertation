from src.board.space import Space
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.board.clearing import Clearing
    from src.utils.game_settings import GameSettings


class Forest(Space):
    def __init__(self, index, settings: 'GameSettings', adjacent_clearings: list['Clearing'] = [], adjacent_forests: list['Forest'] = []) -> None:
        super().__init__(index, settings)
        self.adjacent_clearings = adjacent_clearings
        self.adjacent_forests = adjacent_forests

    def __repr__(self):
        return f"Forest {self.index}"
