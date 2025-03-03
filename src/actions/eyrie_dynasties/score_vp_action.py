from __future__ import annotations
from actions.action_handler import Action
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from factions.eyrie_dynasties import EyrieDynasties


class ScoreVpAction(Action):

    def __init__(self, name="Score VP", max_uses=1, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)

    def can_perform(self, executor, game_state=None):
        return super().can_perform(executor, game_state)

    def perform(self, game_state, executor: EyrieDynasties):
        executor.add_vp(executor.roost_track[len(executor.roosts)])
        return super().perform(game_state, executor)
