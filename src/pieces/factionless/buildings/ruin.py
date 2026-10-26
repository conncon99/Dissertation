from __future__ import annotations
from src.pieces.building import Building
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.utils.root_types import Items
    from src.board.clearing import Clearing


class Ruin(Building):
    def __init__(self, clearing: Clearing, item: Items, slot_idx: int) -> None:
        super().__init__(clearing, None, slot_idx, "Ruin")
        self.item = item

    def destroy(self, attacker, action_group=None):
        self.space.slots[self.slot_idx] = None
        self.logger.info(" - Ruin is empty, destroying")
