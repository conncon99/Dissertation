from __future__ import annotations
from src.actions.action_handler import Action
from typing import TYPE_CHECKING
from src.actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from src.factions.marquise_de_cat import Marquise


class RecruitAction(Action):
    def __init__(self):
        super().__init__("Recruit", 1)
        self.id = ActionIDs.MARQUISE_RECRUIT

    def can_perform(self, executor: Marquise, game_state=None):
        return len(executor.recruiters) > 0 and super().can_perform(executor, game_state)

    def perform(self, game_state, executor: Marquise):
        for recruiter in executor.recruiters:
            recruiter.recruit()
        return super().perform(game_state, executor)
        yield
