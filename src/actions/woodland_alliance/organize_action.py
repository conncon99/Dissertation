from __future__ import annotations
from actions.action_handler import Action
from typing import TYPE_CHECKING
from controllers.messages.game_messages import OrganizeMessage
from pieces.woodland_alliance.alliance_tokens import Sympathy
from actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from factions.woodland_alliance import WoodlandAlliance
    from pieces.pawn import Pawn


class OrganizeAction(Action):
    def __init__(self, name="Organize", max_uses=None, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.id = ActionIDs.ORGANIZE

    def can_perform(self, executor: WoodlandAlliance, game_state=None):
        return self.get_replaceable_units(executor) and super().can_perform(executor, game_state) and len(executor.sympathy) < executor.max_sympathy and len(executor.units) > 0

    def get_replaceable_units(self, executor: WoodlandAlliance):
        sympathetic_clearings = [
            sympathy.space for sympathy in executor.sympathy]
        return [unit for unit in executor.units if unit not in sympathetic_clearings]

    def perform(self, game_state, executor: WoodlandAlliance):
        chosen_unit: Pawn = executor.controller.send_game_message(
            OrganizeMessage(game_state, self.action_group, self.get_replaceable_units(executor))).chosen_unit

        Sympathy(chosen_unit.space, executor)
        print(
            f" - Replaced warrior on clearing {chosen_unit.space.index} with a Sympathy token")
        chosen_unit.destroy(None, self.action_group)

        return super().perform(game_state, executor)
