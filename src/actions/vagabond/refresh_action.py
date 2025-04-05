from __future__ import annotations
from actions.action_handler import Action
from typing import TYPE_CHECKING
from controllers.messages.game_messages import RefreshItemMessage
from controllers.messages.controller_messages import RefreshItemResponse
from actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from factions.vagabond.vagabond import Vagabond


class RefreshAction(Action):
    def __init__(self, name='Refresh', max_uses=1, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.id = ActionIDs.REFRESH

    def can_perform(self, executor: Vagabond, game_state=None):
        return executor.satchel.has_any_exhausted_items() and super().can_perform(executor, game_state)

    def perform(self, game_state, executor: Vagabond):
        total_refreshes_available = 3 + (executor.active_tea_count * 2)
        for i in range(total_refreshes_available):
            if not executor.satchel.has_any_exhausted_items():
                break
            remaining_refreshes = total_refreshes_available - i
            exhausted_damaged_items = [
                item for item, amount in executor.satchel.exhausted_damaged_items.items() for _ in range(amount)]
            exhausted_available_items = [
                item for item, amount in executor.satchel.exhausted_items.items() for _ in range(amount)]
            refresh_response: RefreshItemResponse = yield RefreshItemMessage(game_state, self.action_group, exhausted_damaged_items, exhausted_available_items, remaining_refreshes)
            executor.satchel.refresh_item(
                refresh_response.chosen_item, refresh_response.is_damaged)

        return super().perform(game_state, executor)
