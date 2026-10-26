from __future__ import annotations
from src.actions.action_handler import Action
from typing import List, Tuple, TYPE_CHECKING
from src.controllers.messages.game_messages import MoveFromMessage, MoveToMessage, MoveUnitsMessage
from src.controllers.messages.controller_messages import MoveFromResponse, MoveToResponse, MoveUnitsResponse
from src.utils.root_types import Factions
from src.pieces.woodland_alliance.alliance_tokens import Sympathy
from src.actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from src.board.clearing import Clearing
    from src.pieces.pawn import Pawn
    from src.factions.faction import Faction
    from src.utils.game_state import GameState


class MoveAction(Action):

    def __init__(self, name="Move", max_uses=None, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.id = ActionIDs.MOVE

    def can_perform(self, executor, game_state):
        return super().can_perform(executor, game_state) and self.get_all_possible_moves(game_state, executor) != []

    def get_all_possible_moves(self, game_state: GameState, executor: Faction) -> List[Tuple[Clearing, Clearing, List[Pawn]]]:
        valid_moves = []
        for from_clearing in self._valid_from_clearings(game_state, executor):
            # If we own the clearing we are moving from, we can move to any adjacent clearing
            if from_clearing.get_owner() == executor.faction_id:
                valid_moves.extend([(from_clearing, to_clearing, from_clearing.units[executor.faction_id])
                                   for to_clearing in from_clearing.adjacent_clearings])
            else:
                # Otherwise we must own the clearing we are moving to
                for to_clearing in from_clearing.adjacent_clearings:
                    if to_clearing.get_owner() == executor.faction_id:
                        valid_moves.append(
                            (from_clearing, to_clearing, from_clearing.units[executor.faction_id]))
        return valid_moves

    def _valid_from_clearings(self, game_state: GameState, executor: Faction) -> List[Clearing]:
        return [clearing for clearing in game_state.board.clearings if len(clearing.units[executor.faction_id]) != 0]

    def move(self, from_clearing: Clearing, to_clearing: Clearing, units: List[Pawn], executor: Faction, game_state: GameState):
        for unit in units:
            from_clearing.units[executor.faction_id].remove(unit)
            to_clearing.units[executor.faction_id].append(unit)
            unit.space = to_clearing
        if any(faction.faction_id == Factions.WOODLAND_ALLIANCE.value for faction in game_state.faction_list) and executor.faction_id != Factions.WOODLAND_ALLIANCE.value and any(isinstance(item, Sympathy) for item in to_clearing.tokens[Factions.WOODLAND_ALLIANCE.value]):
            self.logger.info(
                " - Moved into clearing with a sympathy token: Outrage Triggered")
            # Trigger outrage
            woodland_alliance = next(
                (faction for faction in game_state.faction_list if faction.faction_id == Factions.WOODLAND_ALLIANCE.value))
            yield from woodland_alliance.trigger_outrage(
                executor, to_clearing, self.action_group, game_state)

    def perform(self, game_state, executor):
        # 1. Get all possible moves
        valid_moves = self.get_all_possible_moves(game_state, executor)
        # 2. Make a choice of which move to make and who to move

        move_from_response: MoveFromResponse = yield MoveFromMessage(game_state, self.action_group, list(set([move[0] for move in valid_moves])))

        from_clearing: Clearing = move_from_response.from_clearing

        game_state.selected_clearing = from_clearing

        move_to_response: MoveToResponse = yield MoveToMessage(game_state, self.action_group, list(set([move[1]
                                                                                                   for move in valid_moves if move[0] == from_clearing])))
        to_clearing: Clearing = move_to_response.to_clearing

        game_state.selected_to_clearing = to_clearing

        move_units_response: MoveUnitsResponse = yield MoveUnitsMessage(game_state, self.action_group, from_clearing.units[executor.faction_id])

        num_units = move_units_response.num_units

        units = from_clearing.units[executor.faction_id][:num_units]
        self.logger.debug(
            f"Max available Units: {from_clearing.units[executor.faction_id]}")
        # 3. Execute move
        self.logger.info(
            f" - Moving from clearing {from_clearing.index} to clearing {to_clearing.index} with {num_units} units")
        yield from self.move(from_clearing, to_clearing, units, executor, game_state)
        game_state.selected_clearing = None
        game_state.selected_to_clearing = None
        return super().perform(game_state, executor)
