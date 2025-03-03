from __future__ import annotations
from pieces.token import Token
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from factions.marquise_de_cat import Marquise


class Keep(Token):
    def __init__(self, clearing, faction: Marquise):
        super().__init__(clearing, faction)

    def destroy(self, attacker):
        self.faction.keep = None
        return super().destroy(attacker)


class Wood(Token):
    def __init__(self, clearing, faction: Marquise):
        super().__init__(clearing, faction)
        faction.wood.append(self)

    def destroy(self, attacker):
        self.remove_wood()
        return super().destroy(attacker)

    def remove_wood(self):
        self.faction.wood.remove(self)
