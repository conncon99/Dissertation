from __future__ import annotations
from src.actions.action_handler import Action
from typing import TYPE_CHECKING
from src.utils.root_types import Suits
from src.pieces.eyrie_dynasties.eyrie_buildings import Roost
from src.controllers.messages.game_messages import DecreeBuildMessage
from src.actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from src.factions.eyrie_dynasties import EyrieDynasties
    from src.utils.game_state import GameState


class DecreeBuildAction(Action):
    def __init__(self, suit: Suits, name="Decree Build", max_uses=1, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.suit = suit
        id_dict = {Suits.FOX: ActionIDs.DECREE_BUILD_FOX, Suits.MOUSE: ActionIDs.DECREE_BUILD_MOUSE,
                   Suits.RABBIT: ActionIDs.DECREE_BUILD_RABBIT, Suits.BIRD: ActionIDs.DECREE_BUILD_BIRD}
        self.id = id_dict[self.suit]
        self.turmoil_action = True

    def can_perform(self, executor: EyrieDynasties, game_state=None):
        return len(executor.roosts < executor.max_roosts) and any(clearing.get_suit() == self.suit and clearing.get_owner() == executor.faction_id and clearing.has_free_slots() and all(not isinstance(slot, Roost) for slot in clearing.slots) for clearing in game_state.board.clearings)

    def perform(self, game_state: GameState, executor: EyrieDynasties):

        # Make a list of clearings that the eyrie owns that matches the suit of this card
        available_clearings = [clearing for clearing in game_state.board.clearings if clearing.get_suit(
        ) == self.suit and clearing.get_owner() == executor.faction_id and clearing.has_free_slots() and all(not isinstance(slot, Roost) for slot in clearing.slots)]

        # Choose clearing
        response = yield DecreeBuildMessage(game_state, self.action_group, available_clearings)
        chosen_clearing = response.chosen_clearing
        Roost(chosen_clearing, executor, chosen_clearing.get_first_free_slot())

        return super().perform(game_state, executor)
