from __future__ import annotations
import math
from actions.action_handler import Action
from typing import TYPE_CHECKING
from pieces.pawn import Pawn
from pieces.eyrie_dynasties.eyrie_buildings import Roost
from pieces.marquise_de_cat.marquise_tokens import Keep
from controllers.messages.game_messages import RoostlessMessage
from utils.root_types import Factions

if TYPE_CHECKING:
    from factions.eyrie_dynasties import EyrieDynasties
    from utils.game_state import GameState
    from board.clearing import Clearing


class RoostlessAction(Action):
    def __init__(self, name="Roostless", max_uses=1, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)

    def can_perform(self, executor: EyrieDynasties, game_state=None):
        return executor.roosts == [] and super().can_perform(executor, game_state)

    def perform(self, game_state: GameState, executor: EyrieDynasties):
        # 1. Find clearings with lowest number of total warriors
        peaceful_clearings = []
        lowest_clearing_warriors = math.inf
        for clearing in game_state.board.clearings:
            if not clearing.has_free_slots():
                continue
            clearing_warrior_count = self._get_total_warriors(
                game_state, clearing)
            if clearing_warrior_count < lowest_clearing_warriors:
                peaceful_clearings = [clearing]
                lowest_clearing_warriors = clearing_warrior_count
            elif clearing_warrior_count == lowest_clearing_warriors:
                peaceful_clearings.append(clearing)

        # 2. Choose which peaceful clearing to use
        chosen_clearing: Clearing = executor.controller.send_game_message(
            RoostlessMessage(peaceful_clearings)).chosen_clearing

        # 3. Place a roost and 3 troops in that clearing
        Roost(chosen_clearing, executor, chosen_clearing.get_first_free_slot())
        if not any(isinstance(token, Keep) for token in chosen_clearing.tokens[Factions.MARQUISE_DE_CAT.value]):
            for i in range(3):
                Pawn(chosen_clearing, executor)
        return super().perform(game_state, executor)

    def _get_total_warriors(self, game_state: GameState, clearing: Clearing) -> int:
        total_warriors = 0
        for faction in game_state.faction_list:
            total_warriors += clearing.get_faction_warrior_count(
                faction.faction_id)
        return total_warriors
