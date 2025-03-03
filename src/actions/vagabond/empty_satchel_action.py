from __future__ import annotations
from actions.action_handler import Action
from typing import TYPE_CHECKING

from controllers.messages.game_messages import EmptySatchelMessage
from controllers.messages.controller_messages import EmptySatchelResponse

if TYPE_CHECKING:
    from factions.vagabond.vagabond import Vagabond


class EmptySatchelAction(Action):
    def __init__(self, name="Check Satchel Capacity", max_uses=1, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)

    def can_perform(self, executor: Vagabond, game_state=None):
        return executor.satchel.get_total_items() > 6 + (2 * executor.active_bag_count) and super().can_perform(executor, game_state)

    def perform(self, game_state, executor: Vagabond):
        max_satchel_limit = 6 + (2 * executor.active_bag_count)
        items_to_remove = executor.satchel.get_total_items() - max_satchel_limit
        print(f" - Needing to remove {items_to_remove} items from the satchel")

        for _ in range(items_to_remove):
            available_items = [
                item for item, amount in executor.satchel.available_items.items() for _ in range(amount)]
            exhausted_items = [
                item for item, amount in executor.satchel.exhausted_items.items() for _ in range(amount)]
            available_damaged_items = [
                item for item, amount in executor.satchel.available_damaged_items.items() for _ in range(amount)]
            exhausted_damaged_items = [
                item for item, amount in executor.satchel.exhausted_damaged_items.items() for _ in range(amount)]

            satchel_response: EmptySatchelResponse = executor.controller.send_game_message(EmptySatchelMessage(
                available_items, exhausted_items, available_damaged_items, exhausted_damaged_items))

            if satchel_response.is_damaged and satchel_response.is_exhausted:
                executor.satchel.exhausted_damaged_items[satchel_response.chosen_item] -= 1
            elif satchel_response.is_damaged:
                executor.satchel.available_damaged_items[satchel_response.chosen_item] -= 1
            elif satchel_response.is_exhausted:
                executor.satchel.exhausted_items[satchel_response.chosen_item] -= 1
            else:
                executor.satchel.available_items[satchel_response.chosen_item] -= 1
            print(
                f" - Removing {satchel_response.chosen_item.name.capitalize()} from the satchel")
            if satchel_response.is_damaged:
                print(f" - Removed Item was damaged")
            if satchel_response.is_exhausted:
                print(f" - Removed Item was exhausted")

        return super().perform(game_state, executor)
