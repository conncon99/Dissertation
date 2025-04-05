from __future__ import annotations
from actions.action_handler import Action
from typing import TYPE_CHECKING
from pieces.pawn import Pawn
from controllers.messages.game_messages import AllianceRecruitMessage
from utils.root_types import Factions
from pieces.marquise_de_cat.marquise_tokens import Keep
from actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from factions.woodland_alliance import WoodlandAlliance
    from board.clearing import Clearing


class AllianceRecruitAction(Action):
    def __init__(self, name="Alliance Recruit", max_uses=None, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.id = ActionIDs.ALLIANCE_RECRUIT

    def can_perform(self, executor: WoodlandAlliance, game_state=None):
        return len(executor.units) + executor.officers < executor.max_warriors and super().can_perform(executor, game_state) and any(base is not None for base in executor.bases.values())

    def perform(self, game_state, executor: WoodlandAlliance):
        available_clearings = [
            base.space for base in executor.bases.values() if base is not None and not any(isinstance(token, Keep) for token in base.space.tokens[Factions.MARQUISE_DE_CAT.value])]
        response = yield AllianceRecruitMessage(game_state, self.action_group, available_clearings)
        clearing: Clearing = response.chosen_clearing
        Pawn(clearing, executor)
        return super().perform(game_state, executor)
