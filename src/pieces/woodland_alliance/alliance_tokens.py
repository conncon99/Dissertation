from __future__ import annotations
from pieces.token import Token
from board.clearing import Clearing
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from factions.woodland_alliance import WoodlandAlliance


class Sympathy(Token):
    def __init__(self, clearing: Clearing, faction: WoodlandAlliance):
        super().__init__(clearing, faction, "Sympathy Token")
        faction.sympathy.append(self)

    def destroy(self, attacker):
        # Attacker must add matching card to hand
        self.faction.sympathy.remove(self)
        super().destroy(attacker)
        self.faction.trigger_outrage(attacker, self.space)

    def get_suit(self):
        return self.space.get_suit()
