from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, TYPE_CHECKING, Optional, Callable, Generator, Any
import logging

from src.utils.root_types import Suits, Items, Factions
from src.utils.callback_handler import CallbackTimes, BattleCallbackTimes
from src.actions.action_handler import ActionGroup
from src.controllers.nn_controllers.reward_helper import RewardHelper

if TYPE_CHECKING:
    from src.actions.action_handler import Action
    from src.cards.card import Card
    from src.pieces.pawn import Pawn
    from src.controllers.base_controllers.controller import Controller
    from src.cards.deck import Deck
    from src.utils.game_state import GameState
    from src.controllers.messages.game_messages import GameMessage


@dataclass
class Faction(ABC):
    faction_id: int
    reach_value: int
    max_warriors: int
    controller: Controller

    victory_points: int = 0

    prev_vp: int = 0
    prev_unit_count: int = 0
    prev_clearings_controlled: int = 0
    prev_dominance_clearings_controlled: int = 0
    prev_active_cards_count: int = 0
    last_vp_change: int = 0
    last_dominance_change: int = 0

    hand: List[Card] = field(default_factory=list)
    items: List[Items] = field(default_factory=list)
    active_cards: List[Card] = field(default_factory=list)
    units: List[Pawn] = field(default_factory=list)
    hand_limit: int = 5
    setup_order: int = -1
    deck: Deck = None
    print_colour: str = ""
    game_state: GameState = None
    logger: logging.Logger = logging.getLogger()

    dominance: Optional[Suits] = None
    has_won: bool = False
    battle_callbacks: Dict[BattleCallbackTimes, List[Callable]] = field(
        default_factory=lambda: {time: [] for time in BattleCallbackTimes})
    actions: Dict[CallbackTimes, List[ActionGroup]] = field(
        default_factory=lambda: {
            CallbackTimes.DOMINANCE_TIME: [ActionGroup(
                'Dominance', False, [], max_total_uses=1)],
            CallbackTimes.BIRDSONG_START: [ActionGroup(
                'Birdsong-Start', False, [], can_abort=True)],
            CallbackTimes.DAYLIGHT_START: [ActionGroup(
                'Daylight-Start', False, [], can_abort=True)],
            CallbackTimes.EVENING_START: [ActionGroup(
                'Evening-Start', False, [], can_abort=True)],
            **{time: [] for time in CallbackTimes if time not in {CallbackTimes.DOMINANCE_TIME, CallbackTimes.BIRDSONG_START, CallbackTimes.DAYLIGHT_START, CallbackTimes.EVENING_START}}})

    used_spanning_actions: Dict[Action, int] = field(default_factory=dict)
    # Crafting pieces activated this turn, by suit - each may only be activated once per turn (4.1.1)
    crafting_used: Dict[Suits, int] = field(default_factory=dict)

    @abstractmethod
    def get_crafting_resources(self) -> Dict[Suits, int]: ...

    def get_available_crafting_resources(self) -> Dict[Suits, int]:
        """Crafting pieces that have not yet been activated this turn"""
        resources = self.get_crafting_resources()
        return {suit: resources[suit] - self.crafting_used.get(suit, 0) for suit in resources}

    def use_crafting_resources(self, recipe: Dict[Suits, int]) -> None:
        """Activates crafting pieces to pay for a recipe. Wild costs are paid from the suits with the most pieces left"""
        available = self.get_available_crafting_resources()
        for suit in (Suits.FOX, Suits.MOUSE, Suits.RABBIT):
            amount = recipe.get(suit, 0)
            available[suit] -= amount
            self.crafting_used[suit] = self.crafting_used.get(suit, 0) + amount
        for _ in range(recipe.get(Suits.BIRD, 0)):
            suit = max((Suits.FOX, Suits.MOUSE, Suits.RABBIT),
                       key=lambda s: available[s])
            available[suit] -= 1
            self.crafting_used[suit] = self.crafting_used.get(suit, 0) + 1

    def reset_turn_state(self) -> None:
        """Called at the end of this faction's turn"""
        self.crafting_used = {}
        self.used_spanning_actions.clear()

    @abstractmethod
    def setup_faction(
        self, map, deck, game_state) -> Generator[GameMessage, Any, None]: ...

    @abstractmethod
    def get_bonus_card_draws(self) -> int: ...

    def discard_card(self, card: Card) -> None:
        assert self.deck
        self.deck.discard_card(card, self)

    def add_vp(self, amount: int) -> None:
        if self.dominance is None:
            self.victory_points += amount

    def subtract_vp(self, amount: int) -> None:
        if self.dominance is None:
            self.victory_points -= amount

    def get_potential_vp(self, game_state: GameState) -> int:
        potential_vp = 0
        if self.dominance and self.faction_id != Factions.VAGABOND.value:
            pass
        elif not self.dominance:
            potential_vp += RewardHelper.get_battle_rewards(self, game_state)
            potential_vp += RewardHelper.get_crafting_reward(self, game_state)
        return potential_vp
