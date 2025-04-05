from __future__ import annotations
from actions.action_handler import Action
from typing import TYPE_CHECKING
from utils.callback_handler import CallbackTimes
from actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from factions.woodland_alliance import WoodlandAlliance


class ModifyEveningActionCount(Action):
    def __init__(self, name="Modify Evening Action", max_uses=1, is_action_group_modifier=True):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.id = ActionIDs.MODIFY_EVENING_ACTION

    def can_perform(self, executor, game_state=None):
        return super().can_perform(executor, game_state)

    def perform(self, game_state, executor: WoodlandAlliance):
        executor.actions[CallbackTimes.IN_EVENING][1].max_total_uses = executor.officers
        return super().perform(game_state, executor)
        yield
