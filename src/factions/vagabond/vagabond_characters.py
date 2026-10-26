
from __future__ import annotations
import numpy as np
from typing import List, TYPE_CHECKING
from src.utils.root_types import Items, Suits
from enum import Enum
from abc import abstractmethod, ABC
from src.board.clearing import Clearing
from src.controllers.messages.controller_messages import RangerRepairResponse
from src.controllers.messages.game_messages import RangerRepairMessage, TinkerCardMessage, ThiefStealMessage
import logging

if TYPE_CHECKING:
    from src.utils.game_state import GameState
    from src.factions.vagabond.vagabond import Vagabond


class VagabondCharacter(ABC):
    def __init__(self, name: str, starting_items: List[Items]):
        self.name = name
        self.starting_items = starting_items

    def __repr__(self):
        return self.name

    @abstractmethod
    def can_perform_special_action(
            self, executor: Vagabond, game_state: GameState) -> bool:
        return executor.satchel.available_items[Items.TORCH] > 0

    @abstractmethod
    def perform_special_action(
        self, executor: Vagabond, game_state: GameState, action_group): ...


class ThiefCharacter(VagabondCharacter):
    def __init__(self):
        super().__init__("Thief", [Items.BOOTS,
                                   Items.TORCH, Items.TEA, Items.SWORD])

    def can_perform_special_action(self, executor, game_state):
        if not isinstance(executor.vagabond_pawn.space, Clearing):
            return False
        return any(faction.faction_id != executor.faction_id and len(faction.hand) > 0 and executor.vagabond_pawn.space.get_faction_piece_count(faction.faction_id) > 0 for faction in game_state.faction_list) and super().can_perform_special_action(executor, game_state)

    def perform_special_action(self, executor, game_state, action_group):
        executor.satchel.exhaust_item(Items.TORCH)
        available_players = [faction for faction in game_state.faction_list if executor.vagabond_pawn.space.get_faction_piece_count(
            faction.faction_id) and faction.faction_id != executor.faction_id and len(faction.hand) > 0]

        response = yield ThiefStealMessage(game_state, action_group, available_players)
        chosen_player = response.chosen_player
        selected_card = np.random.choice(chosen_player.hand)
        chosen_player.hand.remove(selected_card)
        executor.hand.append(selected_card)


class TinkerCharacter(VagabondCharacter):
    def __init__(self):
        super().__init__("Tinker", [Items.BOOTS,
                                    Items.TORCH, Items.BAG, Items.HAMMER])

    def can_perform_special_action(self, executor, game_state):
        if not isinstance(executor.vagabond_pawn.space, Clearing):
            return False
        return len([card.suit for card in game_state.deck.discard if card.suit == Suits.BIRD or card.suit == executor.vagabond_pawn.space.get_suit()]) > 0 and super().can_perform_special_action(executor, game_state)

    def perform_special_action(self, executor, game_state, action_group):
        executor.satchel.exhaust_item(Items.TORCH)
        available_cards = [card for card in game_state.deck.discard if card.suit ==
                           Suits.BIRD or card.suit == executor.vagabond_pawn.space.get_suit()]
        response = yield TinkerCardMessage(game_state, action_group, available_cards)
        chosen_card = response.chosen_card
        executor.hand.append(chosen_card)
        game_state.deck.discard.remove(chosen_card)
        logger = logging.getLogger()
        logger.info(f" - Taken '{chosen_card}' from the discard pile")


class RangerCharacter(VagabondCharacter):
    def __init__(self):
        super().__init__("Ranger", [Items.BOOTS,
                                    Items.TORCH, Items.CROSSBOW, Items.SWORD])

    def can_perform_special_action(self, executor, game_state):
        return executor.satchel.has_damaged_items() and super().can_perform_special_action(executor, game_state)

    def perform_special_action(self, executor, game_state, action_group):
        executor.satchel.exhaust_item(Items.TORCH)
        for _ in range(3):
            if not executor.satchel.has_damaged_items():
                break
            available_damaged_items = [
                item for item, amount in executor.satchel.available_damaged_items.items() for _ in range(amount)]
            exhausted_damaged_items = [
                item for item, amount in executor.satchel.exhausted_damaged_items.items() for _ in range(amount)]
            ranger_response: RangerRepairResponse = yield RangerRepairMessage(game_state, action_group, available_damaged_items, exhausted_damaged_items)
            executor.satchel.repair_item(
                ranger_response.chosen_item, ranger_response.is_exhausted)


class Characters(Enum):
    THIEF = ThiefCharacter()
    TINKER = TinkerCharacter()
    RANGER = RangerCharacter()
