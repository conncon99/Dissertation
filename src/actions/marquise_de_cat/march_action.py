from __future__ import annotations
from typing import TYPE_CHECKING
from src.actions.factionless.move_action import MoveAction
from src.controllers.messages.controller_messages import MarchAgainResponse, MoveFromResponse, MoveToResponse, MoveUnitsResponse
from src.controllers.messages.game_messages import MarchAgainMessage, MoveFromMessage, MoveToMessage, MoveUnitsMessage
from src.actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from src.factions.marquise_de_cat import Marquise
    from src.utils.game_state import GameState
    from src.board.clearing import Clearing


class MarchAction(MoveAction):

    def __init__(self):
        super().__init__("March", None)
        self.id = ActionIDs.MARCH

    def perform(self, game_state: GameState, executor: Marquise):

        for i in range(2):
            # 1. Get all possible moves
            valid_moves = self.get_all_possible_moves(game_state, executor)

            if len(valid_moves) == 0:
                break

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
                f" - Marching from clearing {from_clearing.index} to clearing {to_clearing.index} with {num_units} units")
            yield from self.move(from_clearing, to_clearing, units, executor, game_state)

            if i == 0:
                march_again_response: MarchAgainResponse = yield MarchAgainMessage(game_state, self.action_group)
                if not march_again_response.march_again:
                    break

        self.logger.info(f" - {self.name} action completed\n")
        self.times_used += 1
