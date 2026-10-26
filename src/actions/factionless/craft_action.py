import types
from src.actions.action_handler import Action
from typing import TYPE_CHECKING
from src.controllers.messages.game_messages import CraftMessage
from src.cards.card import ItemCard
from src.utils.root_types import Suits
from src.actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from src.cards.card import Card
    from src.factions.faction import Faction


# How controller works:
# ActionChoiceMessage (containing list of available actions) -> action choice response (chosen action) -> execute action
# If we are unable to craft anything, the CraftAction should be unavailable in the action choice message
# We query the actual card we are crafting in the perform method

class CraftAction(Action):
    def __init__(self, max_uses=None) -> None:
        super().__init__("Craft", max_uses)
        self.id = ActionIDs.CRAFT

    def can_perform(self, executor, game_state=None) -> bool:
        """If we are free to craft this turn and we hold a craftable card in our hand, this function returns True"""
        if self.times_used >= self.max_uses or len(executor.hand) == 0:
            return False
        return any(self._can_craft(card, executor, game_state) for card in executor.hand)

    def _can_craft(self, card: 'Card', executor: 'Faction', game_state) -> bool:
        if not card.is_craftable:
            return False

        # Can't Craft Duplicate Persistent Cards
        if card.name in [card.name for card in executor.active_cards]:
            return False

        # # Can't craft if there is no item available
        if isinstance(card, ItemCard):
            if card.item_bonus not in game_state.craftable_items:
                return False

        # Needs necessary resources
        crafting_resources = executor.get_available_crafting_resources()
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

    def perform(self, game_state, executor):
        # 1. Get list of craftable cards
        crafting_options = [
            card for card in executor.hand if self._can_craft(card, executor, game_state)]
        # 2. Send crafting message to choose card and get card response
        response = yield CraftMessage(game_state, self.action_group, crafting_options)
        card: 'Card' = response.chosen_card
        # 3. Craft card
        self.logger.info(f" - '{executor}' Crafted '{card}'")
        card.owner = executor
        executor.use_crafting_resources(card.crafting_recipe)

        if card.is_persistent:
            executor.hand.remove(card)
            executor.active_cards.append(card)
            self.logger.info(f" - Active Cards: {executor.active_cards}")
            result = card.activate(game_state, self.action_group)
        else:
            result = card.activate(game_state, self.action_group)
        # Some effects (e.g. Favor cards) need to ask for decisions
        if isinstance(result, types.GeneratorType):
            yield from result
        if not card.is_persistent:
            executor.discard_card(card)
        self.post_craft_callback(executor, card)
        super().perform(game_state, executor)

    def post_craft_callback(self, executor, card):
        pass
