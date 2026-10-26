from __future__ import annotations
import math
from src.actions.action_handler import Action
from typing import TYPE_CHECKING
from src.pieces.marquise_de_cat.marquise_buildings import Sawmill, Recruiter, Workshop
from src.controllers.messages.game_messages import WoodRemovalMessage, MarquiseBuildingClearingMessage, MarquiseBuildingTypeMessage
from src.controllers.messages.controller_messages import WoodRemovalResponse, MarquiseBuildingClearingResponse, MarquiseBuildingTypeResponse
from src.pieces.building import Building
from src.actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from src.factions.marquise_de_cat import Marquise
    from src.utils.game_state import GameState
    from src.board.clearing import Clearing


# 1. Choose the building type to build
#   - restricted by wood cost: For each clearing calculate the amount of wood available to that clearing
#   - restricted by maximum number of that building allowed
# 2. Choose the clearing to build in
# 3. Build the building and spend the wood - receive rewards from the building track

class MarquiseBuild(Action):
    def __init__(self):
        super().__init__("Marquise Build", None)
        self.id = ActionIDs.MARQUISE_BUILD

    def can_perform(self, executor: Marquise, game_state=None):
        # 1. Generate wood availability map
        wood_availability_map = self._generate_wood_availability_map(
            executor, game_state)
        # 2. See if we have exceeded maximum numbers of buildings
        available_building_types = self._get_available_building_types(executor)
        if available_building_types == []:
            return False
        # 3. Get the lowest wood cost according to the building tracks
        lowest_wood_cost = self._get_lowest_wood_cost(
            executor, available_building_types)
        # 4. Check if there is a clearing where we can meet the lowest wood cost
        for wood_cost in wood_availability_map.values():
            if wood_cost >= lowest_wood_cost:
                return True
        return False

    def perform(self, game_state, executor: Marquise):
        # 1. Generate wood availability map

        wood_availability_map = self._generate_wood_availability_map(
            executor, game_state)

        clearing_building_options = {clearing: []
                                     for clearing in wood_availability_map.keys()}
        # 2. Create a dictionary of clearing and building types that can be built in them
        for clearing, wood_supply in wood_availability_map.items():
            if len(executor.sawmills) < executor.max_sawmills and self._get_sawmill_cost(executor) <= wood_supply:
                clearing_building_options[clearing].append(Sawmill)

            if len(executor.recruiters) < executor.max_recruiters and self._get_recruiter_cost(executor) <= wood_supply:
                clearing_building_options[clearing].append(
                    Recruiter)

            if len(executor.workshops) < executor.max_workshops and self._get_workshop_cost(executor) <= wood_supply:
                clearing_building_options[clearing].append(Workshop)
        # 3. Choose the clearing and building type via the faction controller

        # Clean clearing_building_options
        clearing_building_options = {clearing: building_options for clearing,
                                     building_options in clearing_building_options.items() if building_options}

        building_clearing_response: MarquiseBuildingClearingResponse = yield MarquiseBuildingClearingMessage(game_state, self.action_group, clearing_building_options)
        clearing = building_clearing_response.chosen_clearing
        game_state.selected_clearing = clearing

        building_type_response: MarquiseBuildingTypeResponse = yield MarquiseBuildingTypeMessage(game_state, self.action_group, clearing_building_options[clearing])

        BuildingChoice = building_type_response.chosen_building_type

        # 4. Receive victory points from the building track and pay wood cost
        cost = -1
        if BuildingChoice is Sawmill:
            cost = self._get_sawmill_cost(executor)
            executor.add_vp(executor.sawmill_track[len(
                executor.sawmills)][1])
        elif BuildingChoice is Recruiter:
            cost = self._get_recruiter_cost(executor)
            executor.add_vp(executor.recruiter_track[len(
                executor.recruiters)][1])
        elif BuildingChoice is Workshop:
            cost = self._get_workshop_cost(executor)
            executor.add_vp(executor.workshop_track[len(
                executor.workshops)][1])

        for _ in range(cost):
            # Wood can only come from the chosen clearing, or clearings connected to it through clearings the Marquise rule (6.5.4.II)
            reachable_wood = self._get_reachable_wood(executor, clearing)
            response = yield WoodRemovalMessage(game_state, self.action_group, reachable_wood)
            wood = response.chosen_wood_token
            wood.destroy(None, self.action_group)

        # 5. Build the building
        building = BuildingChoice(
            clearing, executor, clearing.get_first_free_slot())
        self.logger.info(
            f" - Built {building} on clearing {clearing.index} for slot {building.slot_idx} for {cost} wood")
        game_state.selected_clearing = None
        return super().perform(game_state, executor)

    def _get_reachable_wood(self, executor: Marquise, clearing: Clearing):
        visited = [clearing]
        queue = [clearing]
        while queue:
            current = queue.pop(0)
            for adjacent in current.adjacent_clearings:
                if adjacent not in visited and adjacent.get_owner() == executor.faction_id:
                    visited.append(adjacent)
                    queue.append(adjacent)
        return [wood for wood in executor.wood if wood.space in visited]

    def _get_lowest_wood_cost(self, executor: Marquise, available_building_types):
        lowest_cost = math.inf
        if Sawmill in available_building_types:
            if self._get_sawmill_cost(executor) < lowest_cost:
                lowest_cost = self._get_sawmill_cost(executor)
        if Recruiter in available_building_types:
            if self._get_recruiter_cost(executor) < lowest_cost:
                lowest_cost = self._get_recruiter_cost(executor)
        if Workshop in available_building_types:
            if self._get_workshop_cost(executor) < lowest_cost:
                lowest_cost = self._get_workshop_cost(executor)
        return lowest_cost

    def _get_available_building_types(self, executor: Marquise):
        available_building_types = [Sawmill, Recruiter, Workshop]
        if len(executor.sawmills) >= executor.max_sawmills:
            available_building_types.remove(Sawmill)
        if len(executor.recruiters) >= executor.max_recruiters:
            available_building_types.remove(Recruiter)
        if len(executor.workshops) >= executor.max_workshops:
            available_building_types.remove(Workshop)
        return available_building_types

    def _generate_wood_availability_map(self, executor: Marquise, game_state: GameState):
        # Create a dict[Clearing: wood_count] - starting at 0
        # For each wood token, we go through every clearing that can be traveled to on a path still owned by us
        # We add one to that clearings wood count

        # The board does not change during this search, so each clearing's owner is computed once
        owned = {}

        def is_owned(clearing):
            if clearing not in owned:
                owned[clearing] = clearing.get_owner() == executor.faction_id
            return owned[clearing]

        clearing_wood_counts = {
            clearing: 0 for clearing in game_state.board.clearings if is_owned(clearing) and clearing.has_free_slots()}

        for wood in executor.wood:
            current_clearing: Clearing = wood.space
            visited = []
            queued = [current_clearing]
            while len(queued) > 0:
                queued.remove(current_clearing)
                visited.append(current_clearing)
                if is_owned(current_clearing):
                    if current_clearing.has_free_slots():
                        clearing_wood_counts[current_clearing] += 1
                    for adjacent_clearing in current_clearing.adjacent_clearings:
                        if adjacent_clearing not in visited and adjacent_clearing not in queued:
                            queued.append(adjacent_clearing)
                if len(queued) > 0:
                    current_clearing = queued[0]
        return clearing_wood_counts

    def _get_sawmill_cost(self, executor: Marquise):
        return executor.sawmill_track[len(executor.sawmills)][0]

    def _get_recruiter_cost(self, executor: Marquise):
        return executor.recruiter_track[len(executor.recruiters)][0]

    def _get_workshop_cost(self, executor: Marquise):
        return executor.workshop_track[len(executor.workshops)][0]
