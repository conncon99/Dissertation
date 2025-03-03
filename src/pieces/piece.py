from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from factions.faction import Faction
    from board.space import Space


class Piece(ABC):

    def __init__(self, space: 'Space', faction: 'Faction') -> None:
        self.space = space
        self.faction = faction

    @abstractmethod
    def damage(self, amount: int, attacker: 'Faction'):
        self.destroy(attacker)

    @abstractmethod
    def destroy(self, attacker: 'Faction'): ...
