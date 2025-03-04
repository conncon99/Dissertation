from actions.action_handler import Action
from controllers.messages.game_messages import ClaimDominanceCardMessage, ClaimDominanceSuitMessage


class ClaimDominanceAction(Action):
    def __init__(self, name="Claim Dominance", max_uses=None, is_action_group_modifier=True, group_spanning=True):
        super().__init__(name, max_uses, is_action_group_modifier, group_spanning)

    def can_perform(self, executor, game_state=None):
        return super().can_perform(executor, game_state) and game_state.board.available_dominance_cards != [] and any(card.suit in self.get_suit_list(game_state) for card in executor.hand)

    def get_suit_list(self, game_state):
        return [card.suit for card in game_state.board.available_dominance_cards]

    def perform(self, game_state, executor):

        # 1. Choose which dominance card to take
        available_dominances = [d_card for d_card in game_state.board.available_dominance_cards if any(
            d_card.suit == card.suit for card in executor.hand)]

        chosen_dominance = executor.controller.send_game_message(
            ClaimDominanceSuitMessage(available_dominances)).chosen_dominance

        # 2. Expend card matching it

        available_cards = [
            card for card in executor.hand if card.suit == chosen_dominance.suit]
        chosen_discard = executor.controller.send_game_message(
            ClaimDominanceCardMessage(available_cards)).chosen_discard

        executor.discard_card(chosen_discard)
        executor.hand.append(chosen_discard)
        game_state.board.available_dominance_cards.remove(chosen_dominance)
        print(
            f" - {executor} expended '{chosen_discard}' to take '{chosen_dominance}'")

        return super().perform(game_state, executor)
