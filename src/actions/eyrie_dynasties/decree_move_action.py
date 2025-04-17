from __future__ import annotations
from src.actions.action_handler import Action
from src.actions.factionless.move_action import MoveAction
from typing import TYPE_CHECKING, List, Tuple
from src.utils.root_types import Suits
from src.controllers.messages.game_messages import MoveFromMessage, MoveToMessage, MoveUnitsMessage
from src.controllers.messages.controller_messages import MoveFromResponse, MoveToResponse, MoveUnitsResponse
from src.actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from src.factions.eyrie_dynasties import EyrieDynasties
    from src.board.clearing import Clearing
    from src.pieces.pawn import Pawn
    from src.utils.game_state import GameState


class DecreeMoveAction(MoveAction):
    def __init__(self, suit: Suits, name="Decree Move", max_uses=1, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.suit = suit
        id_dict = {Suits.FOX: ActionIDs.DECREE_MOVE_FOX, Suits.MOUSE: ActionIDs.DECREE_MOVE_MOUSE,
                   Suits.RABBIT: ActionIDs.DECREE_MOVE_RABBIT, Suits.BIRD: ActionIDs.DECREE_MOVE_BIRD}
        self.id = id_dict[self.suit]

    def can_perform(self, executor, game_state=None):
        return True

    def _valid_from_clearings(self, game_state, executor):
        return [
            clearing for clearing in game_state.board.clearings if clearing.get_suit() == self.suit and len(clearing.units[executor.faction_id]) != 0]

    def perform(self, game_state: GameState, executor: EyrieDynasties):
        # 1. Get all possible moves
        valid_moves = self.get_all_possible_moves(game_state, executor)

        if not valid_moves:
            self.logger.info(f" - No valid moves: TURMOIL TRIGGERED")
            yield from executor.trigger_turmoil(self.action_group)
            return

        # 2. Make a choice of which move to make and who to move
        move_from_response: MoveFromResponse = yield MoveFromMessage(game_state, self.action_group, list(set([move[0] for move in valid_moves])))

        from_clearing: Clearing = move_from_response.from_clearing

        move_to_response: MoveToResponse = yield MoveToMessage(game_state, self.action_group, list(set([move[1]
                                                                                                   for move in valid_moves if move[0] == from_clearing])))
        to_clearing: Clearing = move_to_response.to_clearing

        move_units_response: MoveUnitsResponse = yield MoveUnitsMessage(game_state, self.action_group, from_clearing.units[executor.faction_id])

        num_units = move_units_response.num_units

        units = from_clearing.units[executor.faction_id][:num_units]
        # 3. Execute move
        self.logger.info(
            f" - Moving from clearing {from_clearing.index} to clearing {to_clearing.index} with {len(units)} units")
        yield from self.move(from_clearing, to_clearing, units, executor, game_state)
        return super(MoveAction, self).perform(game_state, executor)
