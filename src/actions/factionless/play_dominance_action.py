from __future__ import annotations
from actions.action_handler import Action
from cards.cards import DOMINANCE_CARDS
from typing import TYPE_CHECKING
from controllers.messages.game_messages import ChooseDominanceMessage

if TYPE_CHECKING:
    from cards.card import DominanceCard


class PlayDominanceAction(Action):
    def __init__(self, name="Play Dominance", max_uses=1, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)

    def can_perform(self, executor, game_state=None):
        return any(card in executor.hand for card in DOMINANCE_CARDS) and not executor.dominance and executor.victory_points >= 10 and super().can_perform(executor, game_state)

    def perform(self, game_state, executor):
        # 1. Choose which dominance card to use if we have multiple
        available_dominance_cards = [
            card for card in executor.hand if card in DOMINANCE_CARDS]

        if len(available_dominance_cards) > 1:
            chosen_card: DominanceCard = executor.controller.send_game_message(
                ChooseDominanceMessage(available_dominance_cards)).chosen_card
        else:
            chosen_card: DominanceCard = available_dominance_cards[0]

        # 2. Activate the dominance card
        chosen_card.owner = executor
        chosen_card.activate(game_state.board)
        print(f" - {executor} has activated {chosen_card}")

        return super().perform(game_state, executor)
