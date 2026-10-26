from __future__ import annotations
from src.actions.factionless.battle_action import BattleAction
from typing import TYPE_CHECKING
from src.utils.root_types import Items
from src.actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from src.factions.vagabond.vagabond import Vagabond


class VagabondBattleAction(BattleAction):

    def __init__(self, name="Battle", max_uses=None, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.id = ActionIDs.VAGABOND_BATTLE

    def can_perform(self, executor: Vagabond, game_state):
        return executor.satchel.available_items[Items.SWORD] > 0 and super().can_perform(executor, game_state)

    def perform(self, game_state, executor: Vagabond):
        # Exhaust one S to initiate a battle (9.5.2)
        executor.satchel.exhaust_item(Items.SWORD)
        yield from super().perform(game_state, executor)
