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
        id_dict = {Suits.FOX: ActionIDs.DECREE_RECRUIT_FOX, Suits.MOUSE: ActionIDs.DECREE_RECRUIT_MOUSE,
                   Suits.RABBIT: ActionIDs.DECREE_RECRUIT_RABBIT, Suits.BIRD: ActionIDs.DECREE_RECRUIT_BIRD}
        self.id = id_dict[self.suit]
        self.turmoil_action = True

    def can_perform(self, executor: EyrieDynasties, game_state=None):
        # Charismatic must place two warriors, so both need to be in the supply (7.8.2)
        warriors_needed = 2 if executor.eyrie_leader == EyrieLeaders.Charismatic else 1
        return len(self._get_available_clearings(executor)) > 0 and executor.max_warriors - len(executor.units) >= warriors_needed

    def _get_available_clearings(self, executor: EyrieDynasties):
        # Bird cards match every clearing (2.1.1)
        return [roost.space for roost in executor.roosts if (self.suit == Suits.BIRD or roost.get_suit() == self.suit) and not any(isinstance(token, Keep) for token in roost.space.tokens[Factions.MARQUISE_DE_CAT.value])]

    def perform(self, game_state, executor: EyrieDynasties):
        available_clearings = list(
            dict.fromkeys(self._get_available_clearings(executor)))

        response = yield DecreeRecruitClearingMessage(game_state, self.action_group, available_clearings)
        roost_clearing: Clearing = response.chosen_clearing
        Pawn(roost_clearing, executor)

        if executor.eyrie_leader == EyrieLeaders.Charismatic:
            Pawn(roost_clearing, executor)

        return super().perform(game_state, executor)
