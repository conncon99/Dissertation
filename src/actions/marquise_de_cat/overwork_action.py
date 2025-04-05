from __future__ import annotations
from actions.action_handler import Action
from typing import TYPE_CHECKING
from board.clearing import Clearing
from utils.root_types import Suits
from pieces.marquise_de_cat.marquise_tokens import Wood
from controllers.messages.game_messages import OverworkMessage
from controllers.messages.controller_messages import OverworkResponse
from actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from factions.marquise_de_cat import Marquise


class OverworkAction(Action):

    def __init__(self):
        super().__init__("Overwork", None)
        self.id = ActionIDs.OVERWORK

    def has_card_for_clearing(self, executor: Marquise):
        hand_suits = [card.suit for card in executor.hand]
        for sawmill in executor.sawmills:
            assert isinstance(sawmill.space, Clearing)
            if Suits.BIRD in hand_suits or sawmill.space.get_suit() in hand_suits:
                return True
        return False

    def can_perform(self, executor: Marquise, game_state=None):
        return len(executor.sawmills) > 0 and len(executor.wood) < executor.max_wood and self.has_card_for_clearing(executor) and super().can_perform(executor, game_state)

    def get_all_valid_clearings(self, executor: Marquise):
        valid_clearings = []
        hand_suits = [card.suit for card in executor.hand]
        for sawmill in executor.sawmills:
            assert isinstance(sawmill.space, Clearing)
            if Suits.BIRD in hand_suits or sawmill.space.get_suit() in hand_suits:
                valid_clearings.append(sawmill.space)
        return valid_clearings

    def perform(self, game_state, executor):
        # find the intersection of card suits in hand and the suits of clearings with sawmills
        valid_clearings = self.get_all_valid_clearings(executor)
        # Choose from that intersection
        overwork_response: OverworkResponse = yield OverworkMessage(game_state, self.action_group, valid_clearings, executor.hand)
        executor.discard_card(overwork_response.discard_choice)
        Wood(overwork_response.chosen_clearing, executor)
        return super().perform(game_state, executor)
