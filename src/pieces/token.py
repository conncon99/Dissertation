from __future__ import annotations
from src.pieces.piece import Piece
from typing import TYPE_CHECKING
from src.utils.root_types import EyrieLeaders, Factions
from src.pieces.piece_with_id import PieceWithID

if TYPE_CHECKING:
    from src.factions.faction import Faction
    from src.board.clearing import Clearing


class Token(Piece, PieceWithID):

    def __init__(self, clearing: Clearing, faction: Faction, name: str) -> None:
        super().__init__(clearing, faction, name)
        PieceWithID.__init__(self, name)
        clearing.tokens[faction.faction_id].append(self)

    def __repr__(self):
        return f"{self.name} {self.id}"

    def damage(self, amount: int, attacker: Faction, action_group=None):
        return super().damage(amount, attacker, action_group)

    def destroy(self, attacker: Faction, action_group=None):
        if attacker and not attacker.dominance:
            from src.factions.vagabond.relationship_track import HOSTILE
            if attacker.faction_id == Factions.VAGABOND.value and attacker.relationship_track.relationship_level[self.faction.faction_id] == HOSTILE:
                self.logger.info(f" - {attacker} gained 1 VP due to Infamy")
                attacker.add_vp(1)

            attacker.add_vp(1)
            if attacker.faction_id == Factions.EYRIE_DYNASTY.value and attacker.eyrie_leader == EyrieLeaders.Despot:
                attacker.gained_despot_bonus = True
        self.space.tokens[self.faction.faction_id].remove(self)
        if attacker:
            self.logger.info(f" - {attacker} destroyed {self}")
        PieceWithID.destroy(self)
