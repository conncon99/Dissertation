from __future__ import annotations
from actions.action_handler import Action
from typing import TYPE_CHECKING
from utils.root_types import Suits, RECRUIT, MOVE, BATTLE, BUILD
from controllers.messages.controller_messages import ExtendDecreeActionResponse1, ExtendDecreeActionResponse2, ExtendDecreeCardResponse1, ExtendDecreeCardResponse2
from controllers.messages.game_messages import ExtendDecreeActionMessage1, ExtendDecreeActionMessage2, ExtendDecreeCardMessage1, ExtendDecreeCardMessage2
from actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from factions.eyrie_dynasties import EyrieDynasties


class ExtendDecreeAction(Action):

    def __init__(self, name="Extend Decree", max_uses=1, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.id = ActionIDs.EXTEND_DECREE

    def perform(self, game_state, executor: EyrieDynasties):
        # 1. Choose card 1 and choose which part of the decree to add it to
        decree_types = [RECRUIT, MOVE, BATTLE, BUILD]

        extend_decree_action_response_1: ExtendDecreeActionResponse1 = yield ExtendDecreeActionMessage1(game_state, self.action_group, executor.hand, decree_types)
        decree_type = extend_decree_action_response_1.chosen_action

        extend_decree_card_response_1: ExtendDecreeCardResponse1 = yield ExtendDecreeCardMessage1(game_state, self.action_group, executor.hand, decree_types)
        card1 = extend_decree_card_response_1.chosen_card

        # 2. Add card 1 to the relevant part of the decree and remove it from the hand (do not discard)
        executor.add_card_to_decree(card1, decree_type)

        # 3. Choose whether to do a second card or not (restricted by previous bird card use) and where in the decree to add it
        valid_cards = executor.hand if card1.suit != Suits.BIRD else [
            card for card in executor.hand if card.suit != Suits.BIRD]

        if valid_cards:
            decree_types.append(None)

        extend_decree_action_response_2: ExtendDecreeActionResponse2 = yield ExtendDecreeActionMessage2(game_state, self.action_group, executor.hand, decree_types)
        decree_type = extend_decree_action_response_2.chosen_action

        extend_decree_card_response_2: ExtendDecreeCardResponse2 = yield ExtendDecreeCardMessage2(game_state, self.action_group, executor.hand, decree_types)
        card2 = extend_decree_card_response_2.chosen_card

        # 4. If it exists, add card 2 to the relevant part of the decree and remove it from the hand (do not discard)
        if decree_type:
            executor.add_card_to_decree(card2, decree_type)
        return super().perform(game_state, executor)

    def can_perform(self, executor, game_state=None):
        return len(executor.hand) > 0 and super().can_perform(executor, game_state)
