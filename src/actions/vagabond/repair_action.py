from __future__ import annotations
from actions.action_handler import Action
from typing import TYPE_CHECKING
from utils.root_types import Items

from controllers.messages.game_messages import RepairItemMessage
from controllers.messages.controller_messages import RepairItemResponse
from actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from factions.vagabond.vagabond import Vagabond


class RepairAction(Action):
    def __init__(self, name='Repair', max_uses=None, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.id = ActionIDs.REPAIR

    def can_perform(self, executor: Vagabond, game_state=None):
        return executor.satchel.has_damaged_items() and executor.satchel.available_items[Items.HAMMER] > 0

    def perform(self, game_state, executor: Vagabond):
        available_damaged_items = [
            item for item, amount in executor.satchel.available_damaged_items.items() for _ in range(amount)]
        exhausted_damaged_items = [
            item for item, amount in executor.satchel.exhausted_damaged_items.items() for _ in range(amount)]

        repair_response: RepairItemResponse = executor.controller.send_game_message(
            RepairItemMessage(game_state, self.action_group, available_damaged_items, exhausted_damaged_items))
        executor.satchel.repair_item(
            repair_response.chosen_item, repair_response.is_exhausted)
        executor.satchel.exhaust_item(Items.HAMMER)
        return super().perform(game_state, executor)
