from __future__ import annotations
from pieces.building import Building
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from utils.root_types import Items
    from board.clearing import Clearing


class Ruin(Building):
    def __init__(self, clearing: Clearing, item: Items, slot_idx: int) -> None:
        super().__init__(clearing, None, slot_idx, "Ruin")
        self.item = item

    def destroy(self, attacker):
        self.space.slots[self.slot_idx] = None
        print(" - Ruin is empty, destroying")
