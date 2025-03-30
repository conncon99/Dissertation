from __future__ import annotations
from pieces.piece import Piece
from typing import TYPE_CHECKING
from utils.root_types import Factions
from factions.vagabond.relationship_track import HOSTILE
from pieces.piece_with_id import PieceWithID

if TYPE_CHECKING:
    from factions.faction import Faction
    from board.space import Space


class Pawn(Piece, PieceWithID):
    def __init__(self, space: Space, faction: Faction) -> None:
        super().__init__(space, faction, f"{faction} Pawn")
        PieceWithID.__init__(self, self.name)
        self.space.units[faction.faction_id].append(self)
        self.faction.units.append(self)

    def __repr__(self):
        return f"{self.faction} Pawn {self.id}"

    def damage(self, amount: int, attacker: Faction, action_group=None):
        return super().damage(amount, attacker, action_group)

    def destroy(self, attacker: Faction, action_group=None):
        PieceWithID.destroy(self)
        if attacker and attacker.faction_id == Factions.VAGABOND.value:
            if attacker.relationship_track.relationship_level[self.faction.faction_id] != HOSTILE:
                attacker.relationship_track.relationship_level[self.faction.faction_id] = HOSTILE
                print(f" - {attacker} became hostile with {self.faction}")
            elif not attacker.dominance:
                attacker.add_vp(1)
                print(f" - {attacker} gained 1 VP due to Infamy")

        if self in self.space.units[self.faction.faction_id]:
            self.space.units[self.faction.faction_id].remove(self)
        if self in self.faction.units:
            self.faction.units.remove(self)
