from __future__ import annotations
from actions.action_handler import Action
from typing import TYPE_CHECKING
from board.clearing import Clearing
from board.forest import Forest
from controllers.messages.game_messages import SlipMessage
from actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from factions.vagabond.vagabond import Vagabond


class SlipAction(Action):
    def __init__(self, name='Slip', max_uses=1, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.id = ActionIDs.SLIP

    def can_perform(self, executor: Vagabond, game_state=None):
        return super().can_perform(executor, game_state)

    def perform(self, game_state, executor: Vagabond):
        available_moves = []
        available_moves.extend(executor.vagabond_pawn.space.adjacent_clearings)
        available_moves.extend(executor.vagabond_pawn.space.adjacent_forests)
        from_space = executor.vagabond_pawn.space
        to_space = executor.controller.send_game_message(
            SlipMessage(game_state, self.action_group, available_moves)).chosen_space
        from_space.units[executor.faction_id].remove(executor.vagabond_pawn)
        to_space.units[executor.faction_id].append(executor.vagabond_pawn)
        executor.vagabond_pawn.space = to_space

        print(
            f" - Vagabond has slipped from {self._space_type(from_space)} {from_space.index} to {self._space_type(to_space)} {to_space.index}")

        return super().perform(game_state, executor)

    def _space_type(self, space) -> str:
        if isinstance(space, Clearing):
            return "Clearing"
        elif isinstance(space, Forest):
            return "Forest"
        else:
            return "Error"
