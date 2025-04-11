from __future__ import annotations
from actions.action_handler import Action
from typing import List, Tuple, TYPE_CHECKING
from controllers.messages.game_messages import MoveMessage
from utils.root_types import Factions, Items
from pieces.woodland_alliance.alliance_tokens import Sympathy
from actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from board.clearing import Clearing
    from pieces.pawn import Pawn
    from factions.faction import Faction
    from utils.game_state import GameState


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
        if any(faction.faction_id == Factions.WOODLAND_ALLIANCE for faction in game_state.faction_list) and executor.faction_id != Factions.WOODLAND_ALLIANCE.value and any(isinstance(item, Sympathy) for item in to_clearing.tokens[Factions.WOODLAND_ALLIANCE.value]):
            print(" - Moved into clearing with a sympathy token: Outrage Triggered")
            # Trigger outrage
            woodland_alliance = next(
                (faction for faction in game_state.faction_list if faction.faction_id == Factions.WOODLAND_ALLIANCE.value))
            yield from woodland_alliance.trigger_outrage(
                executor, to_clearing, self.action_group, game_state)

    def perform(self, game_state, executor):
        # 1. Get all possible moves
        valid_moves = self.get_all_possible_moves(game_state, executor)
        # 2. Make a choice of which move to make and who to move
        response = yield MoveMessage(game_state, self.action_group, valid_moves)
        from_clearing, to_clearing, units = response.move
        # 3. Execute move
        print(
            f" - Moving from clearing {from_clearing.index} to clearing {to_clearing.index} with {len(units)} units")
        yield from self.move(from_clearing, to_clearing, units, executor, game_state)
        return super().perform(game_state, executor)
