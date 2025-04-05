from __future__ import annotations
from actions.action_handler import Action
from typing import TYPE_CHECKING
from actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from factions.marquise_de_cat import Marquise


class PlaceWood(Action):
    def __init__(self):
        super().__init__("Place Wood", 1)
        self.id = ActionIDs.PLACE_WOOD

    def can_perform(self, executor: Marquise, game_state=None):
        return len(executor.sawmills) > 0 and super().can_perform(executor, game_state)

    def perform(self, game_state, executor: Marquise):
        for sawmill in executor.sawmills:
            if len(executor.wood) < executor.max_wood:
                sawmill.add_wood()
        return super().perform(game_state, executor)
        yield
