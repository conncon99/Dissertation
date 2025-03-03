from __future__ import annotations
from pieces.building import Building
from board.clearing import Clearing
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from factions.eyrie_dynasties import EyrieDynasties


class Roost(Building):
    def __init__(self, clearing: Clearing, faction: EyrieDynasties, slot_idx: int):
        super().__init__(clearing, faction, slot_idx)
        faction.roosts.append(self)

    def __repr__(self):
        return "Roost"

    def destroy(self, attacker):
        self.faction.roosts.remove(self)
        return super().destroy(attacker)

    def get_suit(self):
        assert isinstance(self.space, Clearing)
        return self.space.get_suit()
