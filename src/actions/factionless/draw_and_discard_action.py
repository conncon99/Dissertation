from actions.action_handler import Action
from controllers.messages.game_messages import DiscardChoiceMessage
from controllers.messages.controller_messages import DiscardChoiceResponse
from actions.action_group_registry import ActionIDs


class DrawAndDiscardAction(Action):
    def __init__(self, max_uses=1):
        super().__init__("Draw and Discard", max_uses)
        self.id = ActionIDs.DRAW_AND_DISCARD

    def can_perform(self, executor, game_state=None):
        return super().can_perform(executor, game_state)

    def perform(self, game_state, executor):
        draw_count = 1 + executor.get_bonus_card_draws()
        print(f" - Drawing {draw_count} cards")
        # Take draw_count cards from the deck
        executor.hand.extend(game_state.deck.draw(draw_count))
        # Choose which cards to discard down to the hand limit
        if len(executor.hand) > executor.hand_limit:
            discard_num = len(executor.hand) - executor.hand_limit
            discard_choices = executor.controller.send_game_message(
                DiscardChoiceMessage(executor.hand, discard_num)).selected_cards
            for card in discard_choices:
                executor.discard_card(card)
        print(f" - Hand: {executor.hand}")
        return super().perform(game_state, executor)
