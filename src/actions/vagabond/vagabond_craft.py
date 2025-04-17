from __future__ import annotations
from src.actions.action_handler import Action
from typing import TYPE_CHECKING
from src.utils.root_types import Items
from src.actions.factionless.craft_action import CraftAction
from src.actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from src.factions.vagabond.vagabond import Vagabond
    from src.cards.card import Card


class VagabondCraft(CraftAction):
    def __init__(self, max_uses=None):
        super().__init__(max_uses)
        self.id = ActionIDs.VAGABOND_CRAFT

    def can_perform(self, executor: Vagabond, game_state=None):
        return executor.satchel.available_items[Items.HAMMER] > 0 and super().can_perform(executor, game_state)

    def perform(self, game_state, executor: Vagabond):
        yield from super().perform(game_state, executor)
        yield

    def post_craft_callback(self, executor: Vagabond, card: Card):
        card_cost = sum(card.crafting_recipe.values())
        for _ in range(card_cost):
            executor.satchel.exhaust_item(Items.HAMMER)
        for item in executor.items:
            self.logger.info(
                f" - Moving crafted {item.name.capitalize()} into satchel")
            executor.satchel.add_item(item)
        executor.items.clear()
