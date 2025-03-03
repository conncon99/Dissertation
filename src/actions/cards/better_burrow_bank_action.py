from actions.action_handler import Action
from controllers.messages.game_messages import BetterBurrowBankMessage


class BetterBurrowBankAction(Action):
    def __init__(self):
        super().__init__("Better Burrow Bank", 1, False)

    def can_perform(self, executor, game_state=None):
        return super().can_perform(executor, game_state)

    def perform(self, game_state, executor):
        # 1. Choose other player
        print(f" - {executor} Played Better Burrow Bank")
        player_list = [
            faction for faction in game_state.faction_list if faction.faction_id != executor.faction_id]
        other_player = executor.controller.send_game_message(
            BetterBurrowBankMessage(player_list)).chosen_player
        print(f" - Selected {other_player} to draw card")
        # 2. Both of you draw a card
        card = executor.deck.draw(1)
        if card != []:
            print(f" - {executor} drew '{card[0].name}'")
            executor.hand.append(card[0])
        card2 = other_player.deck.draw(1)
        if card2 != []:
            print(f" - {other_player} drew '{card2[0].name}'")
            other_player.hand.append(card2[0])

        return super().perform(game_state, executor)
