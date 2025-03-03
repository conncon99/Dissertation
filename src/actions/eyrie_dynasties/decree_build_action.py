from __future__ import annotations
from actions.action_handler import Action
from typing import TYPE_CHECKING
from utils.root_types import Suits
from pieces.eyrie_dynasties.eyrie_buildings import Roost
from controllers.messages.game_messages import DecreeBuildMessage

if TYPE_CHECKING:
    from factions.eyrie_dynasties import EyrieDynasties
    from utils.game_state import GameState


class DecreeBuildAction(Action):
    def __init__(self, suit: Suits, name="Decree Build", max_uses=1, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.suit = suit

    def can_perform(self, executor, game_state=None):
        return True

    def perform(self, game_state: GameState, executor: EyrieDynasties):
        if len(executor.roosts) >= executor.max_roosts:
            print(" - Cannot place any more roosts: TURMOIL TRIGGERED")
            executor.trigger_turmoil()
            return

        # Make a list of clearings that the eyrie owns that matches the suit of this card
        available_clearings = [clearing for clearing in game_state.board.clearings if clearing.get_suit(
        ) == self.suit and clearing.get_owner() == executor.faction_id and clearing.has_free_slots() and all(not isinstance(slot, Roost) for slot in clearing.slots)]

        if not available_clearings:
            print(
                f" - no available {self.suit.name.capitalize()} clearings for roosts: TURMOIL TRIGGERED")
            executor.trigger_turmoil()
            return

        # Choose clearing
        chosen_clearing = executor.controller.send_game_message(
            DecreeBuildMessage(available_clearings)).chosen_clearing
        Roost(chosen_clearing, executor, chosen_clearing.get_first_free_slot())

        return super().perform(game_state, executor)
