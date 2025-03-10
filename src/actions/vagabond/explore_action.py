from __future__ import annotations
from actions.action_handler import Action
from typing import TYPE_CHECKING
from utils.root_types import Items
from board.clearing import Clearing
from pieces.factionless.buildings.ruin import Ruin
from actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from factions.vagabond.vagabond import Vagabond


class ExploreAction(Action):
    def __init__(self, name="Explore", max_uses=None, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.id = ActionIDs.EXPLORE

    def can_perform(self, executor: Vagabond, game_state=None):
        return executor.satchel.available_items[Items.TORCH] > 0 and isinstance(executor.vagabond_pawn.space, Clearing) and any(isinstance(slot, Ruin) for slot in executor.vagabond_pawn.space.slots)

    def perform(self, game_state, executor: Vagabond):
        executor.satchel.exhaust_item(Items.TORCH)
        ruin = None
        for slot in executor.vagabond_pawn.space.slots:
            if isinstance(slot, Ruin):
                ruin = slot
                break

        assert ruin is not None
        print(
            f" - Searching Ruin of Clearing {executor.vagabond_pawn.space.index}")
        executor.satchel.add_item(ruin.item)
        executor.add_vp(1)
        print(
            f" - Added {ruin.item.name.capitalize()} to satchel and gained 1 Victory Point")
        ruin.destroy(None)
        return super().perform(game_state, executor)
