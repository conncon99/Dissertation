from __future__ import annotations
from src.pieces.token import Token
from src.pieces.piece_with_id import PieceWithID
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.factions.woodland_alliance import WoodlandAlliance
    from src.board.clearing import Clearing


class Sympathy(Token, PieceWithID):
    def __init__(self, clearing: Clearing, faction: WoodlandAlliance):
        super().__init__(clearing, faction, "Sympathy Token")
        faction.sympathy.append(self)

    def destroy(self, attacker, action_group):
        # Attacker must add matching card to hand
        self.faction.sympathy.remove(self)
        super().destroy(attacker, action_group)
        yield from self.faction.trigger_outrage(attacker, self.space, action_group, self.faction.game_state)

    def get_suit(self):
        return self.space.get_suit()
