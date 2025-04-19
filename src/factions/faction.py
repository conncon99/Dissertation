from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, TYPE_CHECKING, Optional, Callable, Generator, Any
import logging

from src.utils.root_types import Suits, Items
from src.utils.callback_handler import CallbackTimes, BattleCallbackTimes
from src.actions.action_handler import ActionGroup

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

    @abstractmethod
    def get_crafting_resources(self) -> Dict[Suits, int]: ...

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
