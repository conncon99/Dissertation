from __future__ import annotations
from factions.faction import Faction
from pieces.marquise_de_cat.marquise_tokens import Keep
from controllers.messages.game_messages import MarquiseBuildingSetupMessage
from controllers.messages.controller_messages import MarquiseBuildingSetupResponse
from controllers.messages.game_messages import FieldHospitalMessage
from actions.action_handler import ActionGroup
from actions.marquise_de_cat.place_wood import PlaceWood
from actions.marquise_de_cat.recruit_action import RecruitAction
from actions.factionless.craft_action import CraftAction
from actions.factionless.draw_and_discard_action import DrawAndDiscardAction
from actions.marquise_de_cat.overwork_action import OverworkAction
from actions.marquise_de_cat.marquise_build import MarquiseBuild
from actions.marquise_de_cat.march_action import MarchAction
from actions.marquise_de_cat.spend_bird_card_action import SpendBirdCardAction
from actions.factionless.battle_action import BattleAction
from actions.factionless.play_dominance_action import PlayDominanceAction
from utils.root_types import Suits
from board.map import Map
from utils.callback_handler import CallbackTimes
from typing import List, TYPE_CHECKING, Dict
from controllers.messages.game_messages import KeepClearingMessage
from pieces.pawn import Pawn
from pieces.marquise_de_cat.marquise_buildings import Sawmill, Workshop, Recruiter
if TYPE_CHECKING:
    from board.clearing import Clearing
    from pieces.marquise_de_cat.marquise_tokens import Wood
    from cards.deck import Deck
    from utils.game_state import GameState


class Marquise(Faction):

    def __init__(self, controller) -> None:
        super().__init__(faction_id=1,
                         reach_value=10, max_warriors=25, controller=controller, print_colour="\033[38;5;208m")
        self.max_sawmills = 6
        self.max_workshops = 6
        self.max_recruiters = 6
        self.max_wood = 8
        self.wood: List[Wood] = []
        self.sawmills: List[Sawmill] = []
        self.workshops: List[Workshop] = []
        self.recruiters: List[Recruiter] = []
        self.keep: Keep = None
        # Tracks are Dict[index, [Cost, VP reward]] - card draw bonuses are calculated separately
        self.sawmill_track: Dict[int, List[int]] = {
            0: [0, 0], 1: [1, 1], 2: [2, 2], 3: [3, 3], 4: [3, 4], 5: [4, 5]}
        self.workshop_track: Dict[int, List[int]] = {
            0: [0, 0], 1: [1, 2], 2: [2, 2], 3: [3, 3], 4: [3, 4], 5: [4, 5]}
        self.recruiter_track: Dict[int, List[int]] = {
            0: [0, 0], 1: [1, 1], 2: [2, 2], 3: [3, 3], 4: [3, 3], 5: [4, 4]}
        self.actions[CallbackTimes.IN_BIRDSONG] = [
            ActionGroup("Birdsong", False, [PlaceWood()], 1)]
        self.actions[CallbackTimes.IN_DAYLIGHT] = [
            ActionGroup("Daylight-1", False,
                        [CraftAction(), PlayDominanceAction()], None, can_abort=True),
            ActionGroup("Daylight-2", False,
                        [MarquiseBuild(), BattleAction(), RecruitAction(), OverworkAction(), MarchAction(), SpendBirdCardAction()], 3, can_abort=True),
            ActionGroup("Daylight-3", False,
                        [PlayDominanceAction()], 1, can_abort=True)
        ]
        self.actions[CallbackTimes.IN_EVENING] = [ActionGroup(
            "Evening", False, [DrawAndDiscardAction()], 1)]

    def __repr__(self) -> str:
        return "Marquise de Cat"

    def get_crafting_resources(self):
        """Crafting for the Marquise is based on the number and clearings of workstations"""
        crafting_resources = {suit: 0 for suit in Suits}
        for workshop in self.workshops:
            crafting_resources[workshop.get_suit()] += 1
        return crafting_resources

    def setup_faction(self, map: Map, deck: Deck, game_state: GameState):
        print(f"Setting Up {self}")

        self.deck = deck
        self.game_state = game_state

        # Place Keep in corner clearing
        free_corner_clearings = [
            clearing for clearing in map.corner_clearings if all(slot is None or slot.faction.faction_id == self.faction_id for slot in clearing.slots) and all(token_list == [] for token_list in clearing.tokens.values())]

        response = yield KeepClearingMessage(game_state, None, free_corner_clearings)
        keep_clearing: Clearing = response.keep_clearing
        self.keep = Keep(keep_clearing, self)
        print(f"- Placed Keep in clearing {keep_clearing.index}")

        # Place warrior in each clearing except the diagonally opposite corner from the keep
        for clearing in map.clearings:
            if ((keep_clearing.index == 0 and clearing.index == 11) or
                (keep_clearing.index == 2 and clearing.index == 8) or
                (keep_clearing.index == 11 and clearing.index == 0) or
                    (keep_clearing.index == 8 and clearing.index == 2)):
                continue
            Pawn(clearing, self)

        # Place 1 sawmill, 1 workshop and 1 recruiter either in the keep clearing or in an adjacent clearing

        available_clearings = [
            clearing for clearing in keep_clearing.adjacent_clearings if clearing.has_free_slots()]
        if keep_clearing.has_free_slots():
            available_clearings.append(keep_clearing)

        setup_response: MarquiseBuildingSetupResponse = yield MarquiseBuildingSetupMessage(
            game_state, None, available_clearings)

        sawmill = Sawmill(setup_response.sawmill_clearing, self,
                          setup_response.sawmill_clearing.get_first_free_slot())
        recruiter = Recruiter(setup_response.recruiter_clearing, self,
                              setup_response.recruiter_clearing.get_first_free_slot())
        workshop = Workshop(setup_response.workshop_clearing, self,
                            setup_response.workshop_clearing.get_first_free_slot())

        print(
            f"- Placed Sawmill in clearing {sawmill.space.index} at slot {sawmill.slot_idx}")
        print(
            f"- Placed Recruiter in clearing {recruiter.space.index} at slot {recruiter.slot_idx}")
        print(
            f"- Placed Workshop in clearing {workshop.space.index} at slot {workshop.slot_idx}")

        print(f"- Finished {self} Set Up\n")
        return
        yield

    def get_bonus_card_draws(self):
        if len(self.recruiters) >= 5:
            return 2
        elif len(self.recruiters) >= 3:
            return 1
        return 0

    def use_field_hospital(self, clearing: Clearing, units_destroyed: int, action_group):
        field_hospital_cards = [
            card for card in self.hand if card.suit == Suits.BIRD or card.suit == clearing.get_suit()]
        if field_hospital_cards != []:
            # send game message to allow marquise to use field hospital
            field_hospital_cards.append(None)

            message = FieldHospitalMessage(
                self.game_state, action_group, field_hospital_cards)

            chosen_card = yield message.chosen_card

            if chosen_card is not None:
                print(
                    f" - Using Field Hospital to save {units_destroyed} units on clearing {clearing.index}")
                self.discard_card(chosen_card)
                for _ in range(units_destroyed):
                    Pawn(self.keep.space, self)
            else:
                print(" - Field Hospital not used")
        else:
            print(" - No valid cards for Field Hospital")
