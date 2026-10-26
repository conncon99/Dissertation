from __future__ import annotations
from src.actions.action_handler import Action
from typing import TYPE_CHECKING
from src.board.forest import Forest
from src.actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from src.factions.vagabond.vagabond import Vagabond


class EveningRestAction(Action):
    def __init__(self, name="Evening's Rest", max_uses=1, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.id = ActionIDs.EVENINGS_REST

    def can_perform(self, executor: Vagabond, game_state=None):
        return isinstance(executor.vagabond_pawn.space, Forest) and executor.satchel.has_damaged_items() and super().can_perform(executor, game_state)

    def perform(self, game_state, executor: Vagabond):
        # Move every damaged item back to the satchel (or its track) face up
        for item in executor.satchel.exhausted_damaged_items.keys():
            while executor.satchel.exhausted_damaged_items[item] > 0:
                executor.satchel.refresh_item(item, True)
        for item in executor.satchel.available_damaged_items.keys():
            while executor.satchel.available_damaged_items[item] > 0:
                executor.satchel.repair_item(item, False)
        return super().perform(game_state, executor)
        yield
