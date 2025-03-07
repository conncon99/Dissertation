from __future__ import annotations
from actions.action_handler import Action
from utils.root_types import Items
from typing import TYPE_CHECKING
from board.clearing import Clearing
from board.forest import Forest
from controllers.messages.game_messages import VagabondMoveMessage, AllyMovementMessage
from controllers.messages.controller_messages import AllyMovementResponse
from factions.vagabond.relationship_track import HOSTILE, ALLIED

if TYPE_CHECKING:
    from factions.vagabond.vagabond import Vagabond
    from utils.game_state import GameState
    from board.space import Space
    from pieces.pawn import Pawn


class VagabondMoveAction(Action):
    def __init__(self, name='Move', max_uses=None, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)

    def can_perform(self, executor: Vagabond, game_state: GameState):
        if executor.satchel.available_items[Items.BOOTS] >= 2:
            return True
        elif executor.satchel.available_items[Items.BOOTS] == 1:
            for clearing in executor.vagabond_pawn.space.adjacent_clearings:
                for faction in game_state.faction_list:
                    if faction.faction_id == executor.faction_id:
                        continue
                    if clearing.get_faction_warrior_count(faction.faction_id) != 0:
                        return False
                return True
        return False

    def perform(self, game_state: GameState, executor: Vagabond):

        available_clearings = self._generate_clearing_costs(
            executor, game_state)

        chosen_clearing: Clearing = executor.controller.send_game_message(
            VagabondMoveMessage(available_clearings)).chosen_clearing
        clearing_cost = available_clearings[chosen_clearing]

        from_space = executor.vagabond_pawn.space
        to_clearing = chosen_clearing

        # Can bring one allied faction's warriors with you on a move
        available_allies = []
        for faction in game_state.faction_list:
            if faction.faction_id == executor.faction_id:
                continue
            if executor.relationship_track.relationship_level[faction.faction_id] == ALLIED and isinstance(executor.vagabond_pawn.space, Clearing) and executor.vagabond_pawn.space.get_faction_warrior_count(faction.faction_id) > 0:
                available_allies.append(faction)

        if available_allies != []:
            available_allies.append(None)

            ally_movement_response: AllyMovementResponse = executor.controller.send_game_message(
                AllyMovementMessage(available_allies, from_space))
            if ally_movement_response.chosen_ally is not None:
                print(
                    f" - {executor} is bringing along {len(ally_movement_response.chosen_units)} allied warriors from {ally_movement_response.chosen_ally}")
                for unit in ally_movement_response.chosen_units:
                    self.move(from_space, to_clearing,
                              ally_movement_response.chosen_ally.faction_id, unit)

        self.move(from_space, to_clearing,
                  executor.faction_id, executor.vagabond_pawn)

        for _ in range(clearing_cost):
            executor.satchel.exhaust_item(Items.BOOTS)

        print(
            f" - Vagabond has moved from {self._space_type(from_space)} {from_space.index} to Clearing {to_clearing.index} by exhausting {clearing_cost} Boots")

        return super().perform(game_state, executor)

    def _space_type(self, space) -> str:
        if isinstance(space, Clearing):
            return "Clearing"
        elif isinstance(space, Forest):
            return "Forest"
        else:
            return "Error"

    def _generate_clearing_costs(self, executor: Vagabond, game_state: GameState):
        clearing_costs = {
            clearing: 1 for clearing in executor.vagabond_pawn.space.adjacent_clearings}

        for clearing in executor.vagabond_pawn.space.adjacent_clearings:
            for faction in game_state.faction_list:
                if faction.faction_id == executor.faction_id:
                    continue
                if clearing.get_faction_warrior_count(faction.faction_id) != 0 and executor.relationship_track.relationship_level[faction.faction_id] == HOSTILE:
                    if executor.satchel.available_items[Items.BOOTS] < 2:
                        del clearing_costs[clearing]
                    else:
                        clearing_costs[clearing] = 2
                    break
        return clearing_costs

    def move(self, from_space: Space, to_clearing: Clearing, faction_id: int, unit: Pawn):
        from_space.units[faction_id].remove(unit)
        to_clearing.units[faction_id].append(unit)
        unit.space = to_clearing
