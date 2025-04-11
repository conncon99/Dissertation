from __future__ import annotations
from actions.action_handler import Action
from typing import TYPE_CHECKING
from utils.root_types import Suits
from pieces.eyrie_dynasties.eyrie_buildings import Roost
from controllers.messages.game_messages import DecreeBuildMessage
from actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from factions.eyrie_dynasties import EyrieDynasties
    from utils.game_state import GameState


class DecreeBuildAction(Action):
    def __init__(self, suit: Suits, name="Decree Build", max_uses=1, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.suit = suit
        self.id = ActionIDs.DECREE_BUILD

    def can_perform(self, executor, game_state=None):
        return True

    def perform(self, game_state: GameState, executor: EyrieDynasties):
        if len(executor.roosts) >= executor.max_roosts:
            print(" - Cannot place any more roosts: TURMOIL TRIGGERED")
            yield from executor.trigger_turmoil(self.action_group)
            return

        # Make a list of clearings that the eyrie owns that matches the suit of this card
        available_clearings = [clearing for clearing in game_state.board.clearings if clearing.get_suit(
        ) == self.suit and clearing.get_owner() == executor.faction_id and clearing.has_free_slots() and all(not isinstance(slot, Roost) for slot in clearing.slots)]

        if not available_clearings:
            print(
                f" - no available {self.suit.name.capitalize()} clearings for roosts: TURMOIL TRIGGERED")
            yield from executor.trigger_turmoil(self.action_group)
            return

        # Choose clearing
        response = yield DecreeBuildMessage(game_state, self.action_group, available_clearings)
        chosen_clearing = response.chosen_clearing
        Roost(chosen_clearing, executor, chosen_clearing.get_first_free_slot())

        return super().perform(game_state, executor)
