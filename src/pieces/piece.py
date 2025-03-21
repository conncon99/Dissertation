from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from factions.faction import Faction
    from board.space import Space


class Piece(ABC):

    def __init__(self, space: 'Space', faction: 'Faction', name: str) -> None:
        self.space = space
        self.faction = faction
        self.name = name

    def __repr__(self):
        return self.name

    @abstractmethod
    def damage(self, amount: int, attacker: 'Faction', action_group=None):
        self.destroy(attacker, action_group)

    @abstractmethod
    def destroy(self, attacker: 'Faction', action_group=None): ...
