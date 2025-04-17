from __future__ import annotations
from src.pieces.building import Building
from src.board.clearing import Clearing
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.factions.eyrie_dynasties import EyrieDynasties


class Roost(Building):
    def __init__(self, clearing: Clearing, faction: EyrieDynasties, slot_idx: int):
        super().__init__(clearing, faction, slot_idx, "Roost")
        faction.roosts.append(self)

    def destroy(self, attacker, action_group=None):
        self.faction.roosts.remove(self)
        return super().destroy(attacker)

    def get_suit(self):
        assert isinstance(self.space, Clearing)
        return self.space.get_suit()
