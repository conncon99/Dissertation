from __future__ import annotations
from src.actions.action_handler import Action
from typing import TYPE_CHECKING
from src.actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from src.factions.eyrie_dynasties import EyrieDynasties


class ReplenishHandAction(Action):

    def __init__(self, name="Replenish Hand", max_uses=1, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.id = ActionIDs.REPLENISH_HAND

    def can_perform(self, executor, game_state=None):
        return len(executor.hand) == 0 and super().can_perform(executor, game_state)

    def perform(self, game_state, executor: EyrieDynasties):
        executor.hand.extend(executor.deck.draw(1))
        return super().perform(game_state, executor)
        yield
