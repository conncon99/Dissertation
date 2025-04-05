from __future__ import annotations
from actions.action_handler import Action
from typing import TYPE_CHECKING
from actions.factionless.move_action import MoveAction
from controllers.messages.controller_messages import March1Response, March2Response
from controllers.messages.game_messages import March1Message, March2Message
from actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from factions.marquise_de_cat import Marquise
    from utils.game_state import GameState


class MarchAction(MoveAction):

    def __init__(self):
        super().__init__("March", None)
        self.id = ActionIDs.MARCH

    def perform(self, game_state: GameState, executor: Marquise):
        valid_moves = self.get_all_possible_moves(game_state, executor)
        march_response_1: March1Response = yield March1Message(game_state, self.action_group, valid_moves)
        from_clearing, to_clearing, units = march_response_1.move
        unit_count = len(units)
        self.move(from_clearing, to_clearing, units, executor, game_state)
        print(
            f" - Marching from clearing {from_clearing.index} to clearing {to_clearing.index} with {unit_count} units")
        valid_moves = self.get_all_possible_moves(game_state, executor)
        if valid_moves:
            march_response_2: March2Response = yield March2Message(game_state, self.action_group, valid_moves)
            from_clearing, to_clearing, units = march_response_2.move
            if from_clearing is not None:
                unit_count = len(units)
                self.move(from_clearing, to_clearing,
                          units, executor, game_state)
                print(
                    f" - Marching from clearing {from_clearing.index} to clearing {to_clearing.index} with {unit_count} units")
        print(f" - {self.name} action completed\n")
        self.times_used += 1
