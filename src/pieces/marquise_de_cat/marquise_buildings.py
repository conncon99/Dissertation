from __future__ import annotations
from pieces.building import Building
from typing import TYPE_CHECKING
from pieces.marquise_de_cat.marquise_tokens import Wood
from pieces.pawn import Pawn
from board.clearing import Clearing

if TYPE_CHECKING:
    from factions.marquise_de_cat import Marquise


class Sawmill(Building):
    def __init__(self, clearing: Clearing, faction: Marquise, slot_idx: int):
        super().__init__(clearing, faction, slot_idx)
        faction.sawmills.append(self)

    def __repr__(self):
        return "Sawmill"

    def add_wood(self) -> None:
        Wood(self.space, self.faction)


class Workshop(Building):

    def __init__(self, clearing: Clearing, faction: Marquise, slot_idx: int) -> None:
        super().__init__(clearing, faction, slot_idx)
        faction.workshops.append(self)

    def __repr__(self):
        return "Workshop"

    def get_suit(self):
        assert isinstance(self.space, Clearing)
        return self.space.get_suit()


class Recruiter(Building):
    def __init__(self, clearing: Clearing, faction: Marquise, slot_idx: int) -> None:
        super().__init__(clearing, faction, slot_idx)
        faction.recruiters.append(self)

    def __repr__(self):
        return "Recruiter"

    def recruit(self):
        if len(self.faction.units) < self.faction.max_warriors:
            Pawn(self.space, self.faction)
