from __future__ import annotations
from actions.action_handler import Action
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from factions.vagabond.vagabond import Vagabond


class SpecialAction(Action):
    def __init__(self, name="Special Action", max_uses=None, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)

    def can_perform(self, executor: Vagabond, game_state=None):
        return executor.character.can_perform_special_action(executor, game_state)

    def perform(self, game_state, executor: Vagabond):
        executor.character.perform_special_action(executor, game_state)
        return super().perform(game_state, executor)
