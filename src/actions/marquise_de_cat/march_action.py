from __future__ import annotations
from actions.action_handler import Action
from typing import TYPE_CHECKING
from actions.factionless.move_action import MoveAction
from controllers.messages.controller_messages import March1Response, March2Response
from controllers.messages.game_messages import March1Message, March2Message

if TYPE_CHECKING:
    from factions.marquise_de_cat import Marquise


class MarchAction(MoveAction):

    def __init__(self):
        super().__init__("March", None)

    def perform(self, game_state, executor: Marquise):
        valid_moves = self.get_all_possible_moves(game_state, executor)
        march_response_1: March1Response = executor.controller.send_game_message(
            March1Message(valid_moves))
        from_clearing, to_clearing, units = march_response_1.move
        unit_count = len(units)
        self.move(from_clearing, to_clearing, units, executor, game_state)
        print(
            f" - Marching from clearing {from_clearing.index} to clearing {to_clearing.index} with {unit_count} units")
        valid_moves = self.get_all_possible_moves(game_state, executor)
        march_response_2: March2Response = executor.controller.send_game_message(
            March2Message(valid_moves))
        from_clearing, to_clearing, units = march_response_2.move
        if from_clearing is not None:
            unit_count = len(units)
            self.move(from_clearing, to_clearing, units, executor, game_state)
            print(
                f" - Marching from clearing {from_clearing.index} to clearing {to_clearing.index} with {unit_count} units")
        print(f" - {self.name} action completed\n")
        self.times_used += 1
