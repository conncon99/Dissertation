from __future__ import annotations
from pieces.token import Token
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from factions.marquise_de_cat import Marquise


class Keep(Token):
    def __init__(self, clearing, faction: Marquise):
        super().__init__(clearing, faction, "Keep Token")

    def destroy(self, attacker, action_group=None):
        self.faction.keep = None
        return super().destroy(attacker)


class Wood(Token):
    def __init__(self, clearing, faction: Marquise):
        super().__init__(clearing, faction, "Wood Token")
        faction.wood.append(self)

    def destroy(self, attacker, action_group=None):
        self.faction.wood.remove(self)
        return super().destroy(attacker)
