from __future__ import annotations
from src.factions.faction import Faction
from src.pieces.marquise_de_cat.marquise_tokens import Keep
from src.controllers.messages.game_messages import MarquiseWorkshopSetupMessage, MarquiseRecruiterSetupMessage, MarquiseSawmillSetupMessage
from src.controllers.messages.controller_messages import MarquiseWorkshopSetupResponse, MarquiseRecruiterSetupResponse, MarquiseSawmillSetupResponse
from src.controllers.messages.game_messages import FieldHospitalMessage
from src.actions.action_handler import ActionGroup
from src.actions.marquise_de_cat.place_wood import PlaceWood
from src.actions.marquise_de_cat.recruit_action import RecruitAction
from src.actions.factionless.craft_action import CraftAction
from src.actions.factionless.draw_and_discard_action import DrawAndDiscardAction
from src.actions.marquise_de_cat.overwork_action import OverworkAction
from src.actions.marquise_de_cat.marquise_build import MarquiseBuild
from src.actions.marquise_de_cat.march_action import MarchAction
from src.actions.marquise_de_cat.spend_bird_card_action import SpendBirdCardAction
from src.actions.factionless.battle_action import BattleAction
from src.actions.factionless.play_dominance_action import PlayDominanceAction
from src.utils.root_types import Suits
from src.board.map import Map
from src.utils.callback_handler import CallbackTimes
from typing import List, TYPE_CHECKING, Dict
from src.controllers.messages.game_messages import KeepClearingMessage
from src.pieces.pawn import Pawn
from src.pieces.marquise_de_cat.marquise_buildings import Sawmill, Workshop, Recruiter
if TYPE_CHECKING:
    from src.board.clearing import Clearing
    from src.pieces.marquise_de_cat.marquise_tokens import Wood
    from src.cards.deck import Deck
    from src.utils.game_state import GameState


class Marquise(Faction):

    def __init__(self, controller) -> None:
        super().__init__(faction_id=1, setup_order=0,
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
        self.logger.info(f"Setting Up {self}")

        self.deck = deck
        self.game_state = game_state

        # Place Keep in corner clearing
        free_corner_clearings = [
            clearing for clearing in map.corner_clearings if all(slot is None or slot.faction.faction_id == self.faction_id for slot in clearing.slots) and all(token_list == [] for token_list in clearing.tokens.values())]

        response = yield KeepClearingMessage(game_state, None, free_corner_clearings)
        keep_clearing: Clearing = response.keep_clearing
        self.keep = Keep(keep_clearing, self)
        self.logger.info(f"- Placed Keep in clearing {keep_clearing.index}")

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

        sawmill_response: MarquiseSawmillSetupResponse = yield MarquiseSawmillSetupMessage(game_state, None, available_clearings)

        sawmill = Sawmill(sawmill_response.sawmill_clearing, self,
                          sawmill_response.sawmill_clearing.get_first_free_slot())

        if not sawmill_response.sawmill_clearing.has_free_slots():
            available_clearings.remove(sawmill_response.sawmill_clearing)

        recruiter_response: MarquiseRecruiterSetupResponse = yield MarquiseRecruiterSetupMessage(game_state, None, available_clearings)

        recruiter = Recruiter(recruiter_response.recruiter_clearing, self,
                              recruiter_response.recruiter_clearing.get_first_free_slot())

        if not recruiter_response.recruiter_clearing.has_free_slots():
            available_clearings.remove(recruiter_response.recruiter_clearing)

        workshop_response: MarquiseWorkshopSetupResponse = yield MarquiseWorkshopSetupMessage(game_state, None, available_clearings)

        workshop = Workshop(workshop_response.workshop_clearing, self,
                            workshop_response.workshop_clearing.get_first_free_slot())

        self.logger.info(
            f"- Placed Sawmill in clearing {sawmill.space.index} at slot {sawmill.slot_idx}")
        self.logger.info(
            f"- Placed Recruiter in clearing {recruiter.space.index} at slot {recruiter.slot_idx}")
        self.logger.info(
            f"- Placed Workshop in clearing {workshop.space.index} at slot {workshop.slot_idx}")

        self.logger.info(f"- Finished {self} Set Up\n")
        return

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
            self.game_state.active_player = self
            response = yield FieldHospitalMessage(self.game_state, action_group, field_hospital_cards)
            self.game_state.active_player = self.game_state.current_player
            chosen_card = response.chosen_card

            if chosen_card is not None:
                self.logger.info(
                    f" - Using Field Hospital to save {units_destroyed} units on clearing {clearing.index}")
                self.discard_card(chosen_card)
                for _ in range(units_destroyed):
                    Pawn(self.keep.space, self)
            else:
                pass
                self.logger.info(" - Field Hospital not used")
        else:
            pass
            self.logger.info(" - No valid cards for Field Hospital")
        return
        yield
