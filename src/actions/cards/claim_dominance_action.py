from src.actions.action_handler import Action
from src.utils.root_types import Suits
from src.controllers.messages.game_messages import ClaimDominanceCardMessage, ClaimDominanceSuitMessage
from src.actions.action_group_registry import ActionIDs


class ClaimDominanceAction(Action):
    def __init__(self, name="Claim Dominance", max_uses=None, is_action_group_modifier=True, group_spanning=True):
        super().__init__(name, max_uses, is_action_group_modifier, group_spanning)
        self.id = ActionIDs.CLAIM_DOMINANCE

    def can_perform(self, executor, game_state=None):
        return super().can_perform(executor, game_state) and any(self._get_payment_cards(executor, dominance_card) for dominance_card in game_state.board.available_dominance_cards)

    @staticmethod
    def _get_payment_cards(executor, dominance_card):
        """Cards that can be spent to take a dominance card: matching suit, or any bird card (unless the dominance card is a bird)"""
        return [card for card in executor.hand if card.suit == dominance_card.suit or (card.suit == Suits.BIRD and dominance_card.suit != Suits.BIRD)]

    def perform(self, game_state, executor):

        # 1. Choose which dominance card to take
        available_dominances = [d_card for d_card in game_state.board.available_dominance_cards if self._get_payment_cards(
            executor, d_card)]

        response = yield ClaimDominanceSuitMessage(game_state, self.action_group, available_dominances)
        chosen_dominance = response.chosen_dominance
        game_state.selected_suit = chosen_dominance.suit

        # 2. Expend card matching it

        available_cards = self._get_payment_cards(executor, chosen_dominance)
        response = yield ClaimDominanceCardMessage(game_state, self.action_group, available_cards)
        chosen_discard = response.chosen_discard
        game_state.selected_suit = None
        executor.discard_card(chosen_discard)
        executor.hand.append(chosen_dominance)
        game_state.board.available_dominance_cards.remove(chosen_dominance)
        self.logger.info(
            f" - {executor} expended '{chosen_discard}' to take '{chosen_dominance}'")

        return super().perform(game_state, executor)
