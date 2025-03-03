from __future__ import annotations
from pieces.piece import Piece
from board.clearing import Clearing
from typing import TYPE_CHECKING
from utils.root_types import Factions, EyrieLeaders
from factions.vagabond.relationship_track import HOSTILE

if TYPE_CHECKING:
    from factions.faction import Faction


class Building(Piece):
    def __init__(self, clearing: Clearing, faction: Faction, slot_idx: int) -> None:
        self.slot_idx = slot_idx
        super().__init__(clearing, faction)
        assert isinstance(self.space, Clearing)
        self.space.slots[slot_idx] = self

    def damage(self, amount: int, attacker: Faction):
        return super().damage(amount, attacker)

    def destroy(self, attacker: Faction):
        if not attacker.dominance:
            if attacker.faction_id == Factions.VAGABOND.value and attacker.relationship_track.relationship_level[self.faction.faction_id] == HOSTILE:
                print(f" - {attacker} gained 1 VP due to Infamy")
                attacker.add_vp(1)

            attacker.add_vp(1)
            if attacker.faction_id == Factions.EYRIE_DYNASTY.value and attacker.eyrie_leader == EyrieLeaders.Despot:
                attacker.gained_despot_bonus = True
        assert isinstance(self.space, Clearing)
        self.space.slots[self.slot_idx] = None
        print("destroyed building")
        print(f"attacker dominance: {attacker.dominance}")
