from __future__ import annotations
from actions.action_handler import Action
from typing import TYPE_CHECKING
from utils.root_types import Items
from actions.factionless.craft_action import CraftAction
from actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from factions.vagabond.vagabond import Vagabond
    from cards.card import Card


class VagabondCraft(CraftAction):
    def __init__(self, max_uses=None):
        super().__init__(max_uses)
        self.id = ActionIDs.VAGABOND_CRAFT

    def can_perform(self, executor: Vagabond, game_state=None):
        return executor.satchel.available_items[Items.HAMMER] > 0 and super().can_perform(executor, game_state)

    def perform(self, game_state, executor: Vagabond):
        super().perform(game_state, executor)

    def post_craft_callback(self, executor: Vagabond, card: Card):
        card_cost = sum(card.crafting_recipe.values())
        for _ in range(card_cost):
            executor.satchel.exhaust_item(Items.HAMMER)
        for item in executor.items:
            print(f" - Moving crafted {item.name.capitalize()} into satchel")
            executor.satchel.add_item(item)
        executor.items.clear()
