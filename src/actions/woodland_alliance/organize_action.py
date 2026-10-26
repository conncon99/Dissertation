from __future__ import annotations
from src.actions.action_handler import Action
from typing import TYPE_CHECKING
from src.controllers.messages.game_messages import OrganizeMessage
from src.pieces.woodland_alliance.alliance_tokens import Sympathy
from src.actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from src.factions.woodland_alliance import WoodlandAlliance
    from src.pieces.pawn import Pawn


class OrganizeAction(Action):
    def __init__(self, name="Organize", max_uses=None, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.id = ActionIDs.ORGANIZE

    def can_perform(self, executor: WoodlandAlliance, game_state=None):
        return self.get_replaceable_units(executor) and super().can_perform(executor, game_state) and len(executor.sympathy) < executor.max_sympathy and len(executor.units) > 0

    def get_replaceable_units(self, executor: WoodlandAlliance):
        sympathetic_clearings = [
            sympathy.space for sympathy in executor.sympathy]
        return [unit for unit in executor.units if unit.space not in sympathetic_clearings and not unit.space.has_keep()]

    def perform(self, game_state, executor: WoodlandAlliance):
        response = yield OrganizeMessage(game_state, self.action_group, self.get_replaceable_units(executor))
        chosen_unit: Pawn = response.chosen_unit

        clearing = chosen_unit.space
        chosen_unit.destroy(None, self.action_group)
        executor.place_sympathy(clearing)
        self.logger.info(
            f" - Replaced warrior on clearing {clearing.index} with a Sympathy token")

        return super().perform(game_state, executor)
