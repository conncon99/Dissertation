from __future__ import annotations
from typing import TYPE_CHECKING
from src.utils.root_types import Factions, Suits
from src.cards.card import ItemCard, RoyalClaimCard

import math

if TYPE_CHECKING:
    from src.utils.game_state import GameState
    from src.factions.faction import Faction


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


class RewardHelper:

    @classmethod
    def get_crafting_reward(cls, executor: Faction, game_state: GameState):
        # This is a heuristic, not the knapsack problem so just take the best vp value that they can craft instead of totaling
        potential_vp = 0
        for card in executor.hand:
            if isinstance(card, ItemCard):
                if cls._can_craft(card, executor, game_state):
                    if card.vp_bonus > potential_vp:
                        potential_vp = card.vp_bonus
            elif isinstance(card, RoyalClaimCard):
                if cls._can_craft(card, executor, game_state):
                    bonus = 0
                    for clearing in game_state.board.clearings:
                        if clearing.get_owner() == executor.faction_id:
                            bonus += 1
                    if bonus > potential_vp:
                        potential_vp = bonus
        return potential_vp

    @classmethod
    def _can_craft(cls, card, executor: Faction, game_state: GameState) -> bool:
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

    @classmethod
    def get_battle_rewards(cls, executor: Faction, game_state: GameState):
        potential_vp = 0

        for clearing in game_state.board.clearings:
            cardboard_available = 0
            if clearing.get_faction_warrior_count(executor.faction_id) == 0:
                continue
            for faction in game_state.faction_list:
                if faction.faction_id == executor.faction_id:
                    continue
                cardboard_available += sum(
                    1 for building in clearing.slots if building is not None and building.faction and building.faction.faction_id == faction.faction_id)
                cardboard_available += sum(
                    1 for token in clearing.tokens[faction.faction_id])
                true_availability = max(
                    (cardboard_available - clearing.get_faction_warrior_count(faction.faction_id)) + 1, 0)  # + 1 just to reward a little bit, even if it is innaccessible
                potential_vp += min(true_availability,
                                    clearing.get_faction_warrior_count(executor.faction_id))

        return potential_vp
