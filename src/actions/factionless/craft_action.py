from actions.action_handler import Action
from typing import TYPE_CHECKING, List
from controllers.messages.game_messages import CraftMessage
from cards.card import ItemCard
from utils.root_types import Suits
from utils.game_settings import CRAFTABLE_ITEMS

if TYPE_CHECKING:
    from cards.card import Card
    from factions.faction import Faction


# How controller works:
# ActionChoiceMessage (containing list of available actions) -> action choice response (chosen action) -> execute action
# If we are unable to craft anything, the CraftAction should be unavailable in the action choice message
# We query the actual card we are crafting in the perform method

class CraftAction(Action):
    def __init__(self, max_uses=None) -> None:
        super().__init__("Craft", max_uses)

    def can_perform(self, executor, game_state=None) -> bool:
        """If we are free to craft this turn and we hold a craftable card in our hand, this function returns True"""
        if self.times_used >= self.max_uses or len(executor.hand) == 0:
            return False
        return any(self._can_craft(card, executor) for card in executor.hand)

    def _can_craft(self, card: 'Card', executor: 'Faction') -> bool:
        if not card.is_craftable:
            return False

        # Can't Craft Duplicate Persistent Cards
        if card.name in [card.name for card in executor.active_cards]:
            return False

        # # Can't craft if there is no item available
        if isinstance(card, ItemCard):
            if card.item_bonus not in CRAFTABLE_ITEMS:
                return False

        # Needs necessary resources
        crafting_resources = executor.get_crafting_resources()
        remaining_fox = crafting_resources[Suits.FOX] - \
            card.crafting_recipe[Suits.FOX]
        remaining_mouse = crafting_resources[Suits.MOUSE] - \
            card.crafting_recipe[Suits.MOUSE]
        remaining_rabbit = crafting_resources[Suits.RABBIT] - \
            card.crafting_recipe[Suits.RABBIT]

        if remaining_fox < 0 or remaining_mouse < 0 or remaining_rabbit < 0:
            return False

        # Finally Handle Wild Suits
        remaining_wild = remaining_rabbit + remaining_fox + remaining_mouse
        if remaining_wild < card.crafting_recipe[Suits.BIRD]:
            return False

        return True

    def perform(self, game_state, executor) -> None:
        # 1. Get list of craftable cards
        crafting_options = [
            card for card in executor.hand if self._can_craft(card, executor)]
        # 2. Send crafting message to choose card and get card response
        card: 'Card' = executor.controller.send_game_message(
            CraftMessage(crafting_options)).chosen_card
        # 3. Craft card
        print(f" - '{executor}' Crafted '{card}'")
        card.owner = executor

        if card.is_persistent:
            executor.hand.remove(card)
            executor.active_cards.append(card)
            print(f"- Active Cards: {executor.active_cards}")
            card.activate(game_state)
        else:
            card.activate(game_state)
            executor.discard_card(card)
        self.post_craft_callback(executor, card)
        super().perform(game_state, executor)

    def post_craft_callback(self, executor, card):
        pass
