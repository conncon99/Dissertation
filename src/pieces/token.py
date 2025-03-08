from __future__ import annotations
from pieces.piece import Piece
from board.clearing import Clearing
from typing import TYPE_CHECKING
from utils.root_types import EyrieLeaders, Factions
from factions.vagabond.relationship_track import HOSTILE

if TYPE_CHECKING:
    from factions.faction import Faction


class Token(Piece):

    def __init__(self, clearing: Clearing, faction: Faction, name: str) -> None:
        super().__init__(clearing, faction, name)
        clearing.tokens[faction.faction_id].append(self)

    def damage(self, amount: int, attacker: Faction):
        return super().damage(amount, attacker)

    def destroy(self, attacker: Faction):
        if attacker and not attacker.dominance:

            if attacker.faction_id == Factions.VAGABOND.value and attacker.relationship_track.relationship_level[self.faction.faction_id] == HOSTILE:
                print(f" - {attacker} gained 1 VP due to Infamy")
                attacker.add_vp(1)

            attacker.add_vp(1)
            if attacker.faction_id == Factions.EYRIE_DYNASTY.value and attacker.eyrie_leader == EyrieLeaders.Despot:
                attacker.gained_despot_bonus = True
        assert isinstance(self.space, Clearing)
        self.space.tokens[self.faction.faction_id].remove(self)
        if attacker:
            print(f" - {attacker} destroyed {self}")
