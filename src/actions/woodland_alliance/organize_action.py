from __future__ import annotations
from actions.action_handler import Action
from typing import TYPE_CHECKING
from controllers.messages.game_messages import OrganizeMessage
from pieces.woodland_alliance.alliance_tokens import Sympathy
if TYPE_CHECKING:
    from factions.woodland_alliance import WoodlandAlliance
    from pieces.pawn import Pawn


class OrganizeAction(Action):
    def __init__(self, name="Organize", max_uses=None, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)

    def can_perform(self, executor: WoodlandAlliance, game_state=None):
        return self.get_replaceable_units(executor) and super().can_perform(executor, game_state) and len(executor.sympathy) < executor.max_sympathy and len(executor.units) > 0

    def get_replaceable_units(self, executor: WoodlandAlliance):
        sympathetic_clearings = [
            sympathy.space for sympathy in executor.sympathy]
        return [unit for unit in executor.units if unit not in sympathetic_clearings]

    def perform(self, game_state, executor: WoodlandAlliance):
        chosen_unit: Pawn = executor.controller.send_game_message(
            OrganizeMessage(self.get_replaceable_units(executor))).chosen_unit

        Sympathy(chosen_unit.space, executor)
        print(
            f" - Replaced warrior on clearing {chosen_unit.space.index} with a Sympathy token")
        print(len(executor.units))
        chosen_unit.destroy(None)
        print(len(executor.units))

        return super().perform(game_state, executor)
