from __future__ import annotations
from board.clearing import Clearing
from abc import ABC, abstractmethod
from utils.root_types import BASE_SUITS, Items
from pieces.factionless.buildings.ruin import Ruin
import random
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from cards.card import DominanceCard
    from board.forest import Forest


class Map(ABC):

    def __init__(self, settings) -> None:
        self.settings = settings
        self.clearings: List[Clearing] = []
        self.forests: List[Forest] = []
        self.corner_clearings: List[Clearing] = []
        self.available_dominance_cards: List[DominanceCard] = []
        self.available_ruin_items: List[Items] = [
            Items.BAG, Items.BOOTS, Items.HAMMER, Items.SWORD]
        self.create_map()

    def create_map(self) -> None:
        # Working left -> right, top -> bottom
        self.create_clearings()
        self.create_forests()
        self.set_up_clearings()
        self.set_up_forests()

    @abstractmethod
    def create_clearings(self) -> None: ...

    @abstractmethod
    def create_forests(self) -> None: ...

    @abstractmethod
    def set_up_clearings(self) -> None: ...

    @abstractmethod
    def set_up_forests(self) -> None: ...

    @abstractmethod
    def get_opposite_corner(self, clearing: Clearing) -> Clearing: ...

    def create_new_clearing(self, index, suit: BASE_SUITS, slot_count: int, has_ruin: bool) -> None:
        slots = [None] * slot_count
        clearing = Clearing(index, suit, slots, [], [], self.settings)
        if has_ruin:
            ruin_item_idx = random.randint(
                0, len(self.available_ruin_items) - 1)
            clearing.slots[0] = Ruin(
                clearing, self.available_ruin_items.pop(ruin_item_idx), 0)
        self.clearings.append(clearing)

    def add_clearing_connections(self, clearing: Clearing, clearing_indexes: list[int]) -> None:
        for idx in clearing_indexes:
            clearing.adjacent_clearings.append(self.clearings[idx])

    def add_forest_connections(self, forest: Forest, clearing_indexes: list[int], forest_indexes: list[int]) -> None:
        for idx in clearing_indexes:
            self.clearings[idx].adjacent_forests.append(forest)
        forest.adjacent_clearings = [self.clearings[i]
                                     for i in clearing_indexes]
        forest.adjacent_forests = [self.forests[i] for i in forest_indexes]
