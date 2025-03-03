from __future__ import annotations
from actions.action_handler import Action
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from factions.marquise_de_cat import Marquise


class RecruitAction(Action):
    def __init__(self):
        super().__init__("Recruit", 1)

    def can_perform(self, executor: Marquise, game_state=None):
        return len(executor.recruiters) > 0 and super().can_perform(executor, game_state)

    def perform(self, game_state, executor: Marquise):
        for recruiter in executor.recruiters:
            recruiter.recruit()
        return super().perform(game_state, executor)
