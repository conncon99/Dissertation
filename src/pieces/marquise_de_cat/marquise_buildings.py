from __future__ import annotations
from src.pieces.building import Building
from typing import TYPE_CHECKING
from src.pieces.marquise_de_cat.marquise_tokens import Wood
from src.pieces.pawn import Pawn

if TYPE_CHECKING:
    from src.factions.marquise_de_cat import Marquise
    from src.board.clearing import Clearing


class Sawmill(Building):
    def __init__(self, clearing: Clearing, faction: Marquise, slot_idx: int):
        super().__init__(clearing, faction, slot_idx, "Sawmill")
        faction.sawmills.append(self)

    def add_wood(self) -> None:
        Wood(self.space, self.faction)


class Workshop(Building):

    def __init__(self, clearing: Clearing, faction: Marquise, slot_idx: int) -> None:
        super().__init__(clearing, faction, slot_idx, "Workshop")
        faction.workshops.append(self)

    def get_suit(self):
        return self.space.get_suit()


class Recruiter(Building):
    def __init__(self, clearing: Clearing, faction: Marquise, slot_idx: int) -> None:
        super().__init__(clearing, faction, slot_idx, "Recruiter")
        faction.recruiters.append(self)

    def recruit(self):
        if len(self.faction.units) < self.faction.max_warriors:
            Pawn(self.space, self.faction)
