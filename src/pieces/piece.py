from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from src.factions.faction import Faction
    from src.board.space import Space


class PieceMeta(type):
    def __repr__(cls):
        return f"{cls.__name__}"


class Piece(metaclass=PieceMeta):

    def __init__(self, space: 'Space', faction: 'Faction', name: str) -> None:
        self.space = space
        self.faction = faction
        self.name = name
        self.logger = logging.getLogger()

    def __repr__(self):
        return self.name

    @abstractmethod
    def damage(self, amount: int, attacker: 'Faction', action_group=None):
        self.destroy(attacker, action_group)

    @abstractmethod
    def destroy(self, attacker: 'Faction', action_group=None): ...
