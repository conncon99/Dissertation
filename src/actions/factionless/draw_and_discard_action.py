from src.actions.action_handler import Action
from src.controllers.messages.game_messages import DiscardChoiceMessage
from src.controllers.messages.controller_messages import DiscardChoiceResponse
from src.actions.action_group_registry import ActionIDs


class DrawAndDiscardAction(Action):
    def __init__(self, max_uses=1):
        super().__init__("Draw and Discard", max_uses)
        self.id = ActionIDs.DRAW_AND_DISCARD

    def can_perform(self, executor, game_state=None):
        return super().can_perform(executor, game_state)

    def perform(self, game_state, executor):
        draw_count = 1 + executor.get_bonus_card_draws()
        self.logger.info(f" - Drawing {draw_count} cards")
        # Take draw_count cards from the deck
        executor.hand.extend(game_state.deck.draw(draw_count))
        # Choose which cards to discard down to the hand limit
        if len(executor.hand) > executor.hand_limit:
            discard_num = len(executor.hand) - executor.hand_limit
            for _ in range(discard_num):
                response = yield DiscardChoiceMessage(game_state, self.action_group, executor.hand)
                discard_choice = response.selected_card
                executor.discard_card(discard_choice)
        self.logger.info(f" - Hand: {executor.hand}")
        return super().perform(game_state, executor)
