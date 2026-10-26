from __future__ import annotations
from src.actions.action_handler import Action
from typing import TYPE_CHECKING, List
from src.pieces.woodland_alliance.alliance_tokens import Sympathy
from src.controllers.messages.game_messages import SpreadSympathyClearingMessage, SpreadSympathyDiscardMessage
from src.utils.root_types import Suits
from src.actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from src.factions.woodland_alliance import WoodlandAlliance
    from src.utils.game_state import GameState
    from src.board.clearing import Clearing


class SpreadSympathyAction(Action):
    def __init__(self, name="Spread Sympathy", max_uses=None, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.id = ActionIDs.SPREAD_SYMPATHY

    def can_perform(self, executor: WoodlandAlliance, game_state=None):
        return len(executor.sympathy) < executor.max_sympathy and self.get_valid_clearings(executor, game_state) and super().can_perform(executor, game_state)

    def get_valid_clearings(self, executor: WoodlandAlliance, game_state: GameState) -> List[Clearing]:
        valid_clearings = []
        # 1. If no sympathy are on the board, all clearings are available (provided they can be paid for)
        if len(executor.sympathy) == 0:
            return [clearing for clearing in game_state.board.clearings if not clearing.has_keep() and self.can_afford_sympathy(executor, clearing, game_state)]
        else:
            # 2. Otherwise, the clearing must be adjacent to a sympathetic clearing - sympathy cannot be placed on a clearing that already has sympathy
            sympathetic_clearings: List[Clearing] = [
                sympathy.space for sympathy in executor.sympathy]
            for sympathetic_clearing in sympathetic_clearings:
                for adj_clearing in sympathetic_clearing.adjacent_clearings:
                    if adj_clearing in sympathetic_clearings or adj_clearing in valid_clearings or adj_clearing.has_keep():
                        continue
                    if self.can_afford_sympathy(executor, adj_clearing, game_state):
                        valid_clearings.append(adj_clearing)
            return valid_clearings

    def can_afford_sympathy(self, executor: WoodlandAlliance, clearing: Clearing, game_state: GameState) -> bool:
        cost = executor.sympathy_track[len(executor.sympathy)][0]

        # If there are 3 or more enemy warriors on a clearing, the cost increases by 1
        for faction in game_state.faction_list:
            if faction.faction_id != executor.faction_id:
                if clearing.get_faction_warrior_count(faction.faction_id) >= 3:
                    cost += 1
                    break

        total = 0
        for supporter in executor.supporters:
            if supporter.suit == Suits.BIRD or supporter.suit == clearing.get_suit():
                total += 1
            if total >= cost:
                return True
        return False

    def get_available_supporters(self, executor: WoodlandAlliance, clearing: Clearing):
        return [supporter for supporter in executor.supporters if supporter.suit == clearing.get_suit() or supporter.suit == Suits.BIRD]

    def perform(self, game_state: GameState, executor: WoodlandAlliance):
        # 1. Choose clearing to place sympathy on

        available_clearings = self.get_valid_clearings(executor, game_state)

        response = yield SpreadSympathyClearingMessage(game_state, self.action_group, available_clearings)
        chosen_clearing = response.chosen_clearing
        game_state.selected_clearing = chosen_clearing

        self.logger.info(
            f" - Spread sympathy to clearing {chosen_clearing.index}")

        # 2. Choose supporters to discard

        num_to_discard = executor.sympathy_track[len(executor.sympathy)][0]

        for i in range(num_to_discard):
            valid_supporters = self.get_available_supporters(
                executor, chosen_clearing)
            response = yield SpreadSympathyDiscardMessage(game_state, self.action_group, valid_supporters)
            discard_choice = response.chosen_discard
            executor.discard_card(discard_choice)
            executor.supporters.remove(discard_choice)

        # 3. Place sympathy on chosen clearing

        executor.place_sympathy(chosen_clearing)
        game_state.selected_clearing = None
        return super().perform(game_state, executor)
