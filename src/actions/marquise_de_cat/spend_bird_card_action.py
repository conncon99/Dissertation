from __future__ import annotations
from actions.action_handler import Action
from typing import TYPE_CHECKING
from utils.root_types import Suits
from utils.callback_handler import CallbackTimes
from controllers.messages.game_messages import MarquiseSpendBirdCardMessage
from actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from factions.marquise_de_cat import Marquise


class SpendBirdCardAction(Action):
    def __init__(self, name="Spend Bird Card", max_uses=None):
        super().__init__(name, None, is_action_group_modifier=True)
        self.id = ActionIDs.SPEND_BIRD_CARD

    def can_perform(self, executor, game_state=None):
        return any(card.suit == Suits.BIRD for card in executor.hand)

    def perform(self, game_state, executor):
        bird_card_options = [
            card for card in executor.hand if card.suit == Suits.BIRD]
        response = yield MarquiseSpendBirdCardMessage(game_state, self.action_group, bird_card_options)
        chosen_card = response.chosen_card
        executor.discard_card(chosen_card)
        executor.actions[CallbackTimes.IN_DAYLIGHT][1].modify_max_uses(1)
        return super().perform(game_state, executor)
