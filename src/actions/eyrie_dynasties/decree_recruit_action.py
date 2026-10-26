from __future__ import annotations
from src.actions.action_handler import Action
from typing import TYPE_CHECKING
from src.utils.root_types import Suits, EyrieLeaders, Factions
from src.pieces.pawn import Pawn
from src.controllers.messages.game_messages import DecreeRecruitClearingMessage
from src.pieces.marquise_de_cat.marquise_tokens import Keep
from src.actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from src.factions.eyrie_dynasties import EyrieDynasties
    from src.board.clearing import Clearing


class DecreeRecruitAction(Action):
    def __init__(self, suit: Suits, name="Decree Recruit", max_uses=1, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.suit = suit
        id_dict = {Suits.FOX: ActionIDs.DECREE_MOVE_FOX, Suits.MOUSE: ActionIDs.DECREE_MOVE_MOUSE,
                   Suits.RABBIT: ActionIDs.DECREE_MOVE_RABBIT, Suits.BIRD: ActionIDs.DECREE_MOVE_BIRD}
        self.id = id_dict[self.suit]
        self.turmoil_action = True

    def can_perform(self, executor: EyrieDynasties, game_state=None):
        return any(roost for roost in executor.roosts if roost.get_suit() == self.suit and not any(isinstance(token, Keep) for token in roost.space.tokens[Factions.MARQUISE_DE_CAT.value])) and len(executor.units) < executor.max_warriors

    def perform(self, game_state, executor: EyrieDynasties):
        valid_roosts = [
            roost for roost in executor.roosts if roost.get_suit() == self.suit]

        available_clearings = [roost.space for roost in valid_roosts if not any(isinstance(
            token, Keep) for token in roost.space.tokens[Factions.MARQUISE_DE_CAT.value])]

        response = yield DecreeRecruitClearingMessage(game_state, self.action_group, available_clearings)
        roost_clearing: Clearing = response.chosen_clearing
        Pawn(roost_clearing, executor)

        if executor.eyrie_leader == EyrieLeaders.Charismatic:
            if len(executor.units) >= executor.max_warriors:
                self.logger.info(
                    f" - Cannot place any more warriors: TURMOIL TRIGGERED")
                yield from executor.trigger_turmoil(self.action_group)
                return
            Pawn(roost_clearing, executor)

        return super().perform(game_state, executor)
