from __future__ import annotations
from utils.root_types import Items
from typing import List, TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from factions.vagabond.vagabond import Vagabond


class Satchel:
    def __init__(self, owner: Vagabond):
        self.item_limit = 6
        self.owner = owner
        self.available_items: Dict[Items, int] = {item: 0 for item in Items}
        self.exhausted_items: Dict[Items, int] = {item: 0 for item in Items}
        self.available_damaged_items: Dict[Items, int] = {
            item: 0 for item in Items}
        self.exhausted_damaged_items: Dict[Items, int] = {
            item: 0 for item in Items}

    def add_item(self, item: Items):
        self._add_to_item_tracks(item)

    def get_non_damaged_count(self, item: Items) -> int:
        return self.available_items[item] + self.exhausted_items[item]

    def has_available_item(self) -> bool:
        return any(amount > 0 for amount in self.available_items.values())

    def has_damaged_items(self) -> bool:
        return any(amount1 > 0 or amount2 > 0 for amount1, amount2 in zip(self.available_damaged_items.values(), self.exhausted_damaged_items.values()))

    def has_any_exhausted_items(self) -> bool:
        return any(amount > 0 for amount in self.exhausted_items.values()) or any(amount > 0 for amount in self.exhausted_damaged_items.values())

    def has_available_exhausted_items(self) -> bool:
        return any(amount > 0 for amount in self.exhausted_items.values())

    def get_total_items(self):
        total = 0
        for i1, i2, i3, i4 in zip(self.available_items.values(), self.exhausted_items.values(), self.available_damaged_items.values(), self.exhausted_damaged_items.values()):
            total += i1 + i2 + i3 + i4
        return total

    def get_all_of_item(self, item: Items):
        return self.available_items[item], self.exhausted_items[item], self.available_damaged_items[item], self.exhausted_damaged_items[item]

    def exhaust_item(self, item: Items):
        if item == Items.COINS and self.owner.active_coin_count > 0:
            self.owner.active_coin_count -= 1
        elif item == Items.BAG and self.owner.active_bag_count > 0:
            self.owner.active_bag_count -= 1
        elif item == Items.TEA and self.owner.active_tea_count > 0:
            self.owner.active_tea_count -= 1
        else:
            assert self.available_items[item] > 0
            self.available_items[item] -= 1
        self.exhausted_items[item] += 1
        print(f" - Exhausting {item.name.capitalize()}")

    def refresh_item(self, item: Items, is_damaged: bool):
        if is_damaged:
            assert self.exhausted_damaged_items[item] > 0
            self.exhausted_damaged_items[item] -= 1
            self.available_damaged_items[item] += 1
            print(f" - Refreshed a damaged {item.name.capitalize()}")
        else:
            assert self.exhausted_items[item] > 0
            self.exhausted_items[item] -= 1
            self._add_to_item_tracks(item)
            print(f" - Refreshed an undamaged {item.name.capitalize()}")

    def repair_item(self, item: Items, is_exhausted: bool):
        if is_exhausted:
            assert self.exhausted_damaged_items[item] > 0
            self.exhausted_damaged_items[item] -= 1
            self.exhausted_items[item] += 1
            print(f" - Repaired an exhausted {item.name.capitalize()}")
        else:
            assert self.available_damaged_items[item] > 0
            self.available_damaged_items[item] -= 1
            self._add_to_item_tracks(item)
            print(f" - Repaired an available {item.name.capitalize()}")

    def damage_item(self, item: Items, is_exhausted: bool, use_item_track: bool):
        if is_exhausted:
            assert self.exhausted_items[item] > 0
            self.exhausted_items[item] -= 1
            self.exhausted_damaged_items[item] += 1
            print(f" - Damaged exhausted {item.name.capitalize()}")
        elif use_item_track:
            if item == Items.COINS and self.owner.active_coin_count > 0:
                self.owner.active_coin_count -= 1
            elif item == Items.BAG and self.owner.active_bag_count > 0:
                self.owner.active_bag_count -= 1
            elif item == Items.TEA and self.owner.active_tea_count > 0:
                self.owner.active_tea_count -= 1
            else:
                assert self.available_items[item] > 0
                self.available_items[item] -= 1
            self.available_damaged_items[item] += 1
            print(f" - Damaged {item.name.capitalize()} from item track")
        else:
            assert self.available_items[item] > 0
            self.available_items[item] -= 1
            self.available_damaged_items[item] += 1
            print(f" - Damaged available {item.name.capitalize()}")

    def _add_to_item_tracks(self, item: Items):
        if item == Items.TEA and self.owner.active_tea_count < self.owner.max_track_count:
            self.owner.active_tea_count += 1
        elif item == Items.COINS and self.owner.active_coin_count < self.owner.max_track_count:
            self.owner.active_coin_count += 1
        elif item == Items.BAG and self.owner.active_bag_count < self.owner.max_track_count:
            self.owner.active_bag_count += 1
        else:
            self.available_items[item] += 1
