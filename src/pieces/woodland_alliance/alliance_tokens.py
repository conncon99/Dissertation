from __future__ import annotations
from pieces.token import Token
from board.clearing import Clearing
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from factions.woodland_alliance import WoodlandAlliance


class Sympathy(Token):
    def __init__(self, clearing: Clearing, faction: WoodlandAlliance):
        super().__init__(clearing, faction)
        faction.sympathy.append(self)

    def destroy(self, attacker):
        # Attacker must add matching card to hand
        print(" - Destroyed Sympathy Token: Outrage Triggered")
        self.faction.trigger_outrage(attacker, self.space)
        self.faction.sympathy.remove(self)
        return super().destroy(attacker)

    def get_suit(self):
        return self.space.get_suit()
