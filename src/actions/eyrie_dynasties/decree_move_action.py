from __future__ import annotations
from actions.action_handler import Action
from actions.factionless.move_action import MoveAction
from typing import TYPE_CHECKING, List, Tuple
from utils.root_types import Suits
from controllers.messages.game_messages import MoveMessage
from actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from factions.eyrie_dynasties import EyrieDynasties
    from board.clearing import Clearing
    from pieces.pawn import Pawn
    from utils.game_state import GameState


class DecreeMoveAction(MoveAction):
    def __init__(self, suit: Suits, name="Decree Move", max_uses=1, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.suit = suit
        self.id = ActionIDs.DECREE_MOVE

    def can_perform(self, executor, game_state=None):
        return True

    def _valid_from_clearings(self, game_state, executor):
        return [
            clearing for clearing in game_state.board.clearings if clearing.get_suit() == self.suit and len(clearing.units[executor.faction_id]) != 0]

    def perform(self, game_state: GameState, executor: EyrieDynasties):
        # 1. Get all possible moves
        valid_moves = self.get_all_possible_moves(game_state, executor)

        if not valid_moves:
            print(f" - No valid moves: TURMOIL TRIGGERED")
            executor.trigger_turmoil()
            return

        # 2. Make a choice of which move to make and who to move
        from_clearing, to_clearing, units = executor.controller.send_game_message(
            MoveMessage(valid_moves)).move
        # 3. Execute move
        print(
            f" - Moving from clearing {from_clearing.index} to clearing {to_clearing.index} with {len(units)} units")
        self.move(from_clearing, to_clearing, units, executor, game_state)
        return super(MoveAction, self).perform(game_state, executor)
