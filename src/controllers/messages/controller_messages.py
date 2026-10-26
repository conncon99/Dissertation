from __future__ import annotations
from enum import Enum, auto
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.pieces.piece import Piece


class UnexpectedControllerMessage(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ControllerMessages(Enum):
    AMBUSH_RESPONSE = auto()
    PIECE_TARGETING_RESPONSE = auto()
    MOVE_FROM_RESPONSE = auto()
    MOVE_TO_RESPONSE = auto()
    MOVE_UNITS_RESPONSE = auto()
    CRAFT_RESPONSE = auto()
    BATTLE_USE_CARD_RESPONSE = auto()
    CHOOSE_DOMINANCE_RESPONSE = auto()
    ACTION_CHOICE_RESPONSE = auto()
    BATTLE_CLEARING_RESPONSE = auto()
    BATTLE_TARGET_RESPONSE = auto()
    DISCARD_CHOICE_RESPONSE = auto()
    BETTER_BURROW_BANK_RESPONSE = auto()
    STAND_AND_DELIVER_RESPONSE = auto()
    TAX_COLLECTOR_RESPONSE = auto()
    CODEBREAKERS_RESPONSE = auto()
    CLAIM_DOMINANCE_SUIT_RESPONSE = auto()
    CLAIM_DOMINANCE_CARD_RESPONSE = auto()

    # Marquise messages
    KEEP_CLEARING_RESPONSE = auto()
    MARCH_AGAIN_RESPONSE = auto()
    OVERWORK_CLEARING_RESPONSE = auto()
    OVERWORK_DISCARD_RESPONSE = auto()
    MARQUISE_BUILDING_CLEARING_RESPONSE = auto()
    MARQUISE_BUILDING_TYPE_RESPONSE = auto()
    WOOD_REMOVAL_RESPONSE = auto()
    MARQUISE_WORKSHOP_SETUP_RESPONSE = auto()
    MARQUISE_RECRUITER_SETUP_RESPONSE = auto()
    MARQUISE_SAWMILL_SETUP_RESPONSE = auto()
    MARQUISE_SPEND_BIRD_CARD_RESPONSE = auto()
    FIELD_HOSPITAL_RESPONSE = auto()

    # Eyrie Dynasties Messages
    ROOSTLESS_RESPONSE = auto()
    ROOST_SETUP_RESPONSE = auto()
    LEADER_SETUP_RESPONSE = auto()
    DECREE_RECRUIT_CLEARING_RESPONSE = auto()
    EXTEND_DECREE_CARD_RESPONSE_1 = auto()
    EXTEND_DECREE_ACTION_RESPONSE_1 = auto()
    EXTEND_DECREE_CARD_RESPONSE_2 = auto()
    EXTEND_DECREE_ACTION_RESPONSE_2 = auto()
    DECREE_BUILD_RESPONSE = auto()
    TURMOIL_LEADER_RESPONSE = auto()

    # Woodland Alliance Messages
    ALLIANCE_NO_BASE_RESPONSE = auto()
    MOBILIZE_RESPONSE = auto()
    TRAIN_RESPONSE = auto()
    REVOLT_CLEARING_RESPONSE = auto()
    REVOLT_DISCARD_RESPONSE = auto()
    SPREAD_SYMPATHY_CLEARING_RESPONSE = auto()
    SPREAD_SYMPATHY_DISCARD_RESPONSE = auto()
    ALLIANCE_RECRUIT_RESPONSE = auto()
    ORGANIZE_RESPONSE = auto()
    TRIGGERER_OUTRAGE_RESPONSE = auto()
    ALLIANCE_OUTRAGE_RESPONSE = auto()

    # Vagabond Messages
    CHOOSE_CHARACTER_RESPONSE = auto()
    VAGABOND_PLACEMENT_RESPONSE = auto()
    RANGER_REPAIR_RESPONSE = auto()
    TINKER_CARD_RESPONSE = auto()
    THIEF_STEAL_RESPONSE = auto()
    SLIP_RESPONSE = auto()
    REFRESH_ITEM_RESPONSE = auto()
    VAGABOND_MOVE_RESPONSE = auto()
    CHOOSE_QUEST_RESPONSE = auto()
    QUEST_USE_ITEM_TRACK_RESPONSE = auto()
    CHOOSE_QUEST_REWARD_RESPONSE = auto()
    REPAIR_ITEM_RESPONSE = auto()
    EMPTY_SATCHEL_RESPONSE = auto()
    STRIKE_FACTION_CHOICE_RESPONSE = auto()
    STRIKE_PIECE_TARGETING_RESPONSE = auto()
    AID_FACTION_CHOICE_RESPONSE = auto()
    AID_CARD_CHOICE_RESPONSE = auto()
    AID_EXHAUST_ITEM_CHOICE_RESPONSE = auto()
    AID_TAKE_ITEM_CHOICE_RESPONSE = auto()
    BATTLE_DAMAGE_ITEM_RESPONSE = auto()
    COALITION_CHOICE_RESPONSE = auto()
    ALLY_MOVEMENT_FACTION_RESPONSE = auto()
    ALLY_MOVEMENT_UNIT_RESPONSE = auto()
    CHOOSE_ALLY_RESPONSE = auto()
    ALLY_DAMAGE_SPLIT_RESPONSE = auto()


class ControllerMessage:
    def __init__(self, type) -> None:
        self.type = type

# region Factionless Messages


class AmbushResponse(ControllerMessage):
    def __init__(self, ambush_card) -> None:
        super().__init__(ControllerMessages.AMBUSH_RESPONSE)
        self.ambush_card = ambush_card


class BattleUseCardResponse(ControllerMessage):
    def __init__(self, use_card):
        super().__init__(ControllerMessages.BATTLE_USE_CARD_RESPONSE)
        self.use_card = use_card


class BetterBurrowBankResponse(ControllerMessage):
    def __init__(self, chosen_player):
        super().__init__(ControllerMessages.BETTER_BURROW_BANK_RESPONSE)
        self.chosen_player = chosen_player


class ClaimDominanceSuitResponse(ControllerMessage):
    def __init__(self, chosen_dominance):
        super().__init__(ControllerMessages.CLAIM_DOMINANCE_SUIT_RESPONSE)
        self.chosen_dominance = chosen_dominance


class ClaimDominanceCardResponse(ControllerMessage):
    def __init__(self, chosen_discard):
        super().__init__(ControllerMessages.CLAIM_DOMINANCE_CARD_RESPONSE)
        self.chosen_discard = chosen_discard


class TaxCollectorResponse(ControllerMessage):
    def __init__(self, chosen_unit):
        super().__init__(ControllerMessages.TAX_COLLECTOR_RESPONSE)
        self.chosen_unit = chosen_unit


class CodebreakersResponse(ControllerMessage):
    def __init__(self, chosen_player):
        super().__init__(ControllerMessages.CODEBREAKERS_RESPONSE)
        self.chosen_player = chosen_player


class PieceTargetingResponse(ControllerMessage):
    def __init__(self, target: Piece) -> None:
        super().__init__(ControllerMessages.PIECE_TARGETING_RESPONSE)
        self.target = target


class MoveFromResponse(ControllerMessage):
    def __init__(self, from_clearing) -> None:
        super().__init__(ControllerMessages.MOVE_FROM_RESPONSE)
        self.from_clearing = from_clearing


class MoveToResponse(ControllerMessage):
    def __init__(self, to_clearing) -> None:
        super().__init__(ControllerMessages.MOVE_TO_RESPONSE)
        self.to_clearing = to_clearing


class MoveUnitsResponse(ControllerMessage):
    def __init__(self, num_units) -> None:
        super().__init__(ControllerMessages.MOVE_UNITS_RESPONSE)
        self.num_units = num_units


class CraftResponse(ControllerMessage):
    def __init__(self, chosen_card) -> None:
        super().__init__(ControllerMessages.CRAFT_RESPONSE)
        self.chosen_card = chosen_card


class ChooseDominanceResponse(ControllerMessage):
    def __init__(self, chosen_card):
        super().__init__(ControllerMessages.CHOOSE_DOMINANCE_RESPONSE)
        self.chosen_card = chosen_card


class StandAndDeliverResponse(ControllerMessage):
    def __init__(self, chosen_player):
        super().__init__(ControllerMessages.STAND_AND_DELIVER_RESPONSE)
        self.chosen_player = chosen_player


class DiscardChoiceResponse(ControllerMessage):
    def __init__(self, selected_card):
        super().__init__(ControllerMessages.DISCARD_CHOICE_RESPONSE)
        self.selected_card = selected_card


class ActionChoiceResponse(ControllerMessage):
    def __init__(self, chosen_action) -> None:
        super().__init__(ControllerMessages.ACTION_CHOICE_RESPONSE)
        self.chosen_action = chosen_action


class BattleClearingChoiceResponse(ControllerMessage):
    def __init__(self, chosen_clearing):
        super().__init__(ControllerMessages.BATTLE_CLEARING_RESPONSE)
        self.chosen_clearing = chosen_clearing


class BattleTargetResponse(ControllerMessage):
    def __init__(self, chosen_target):
        super().__init__(ControllerMessages.BATTLE_TARGET_RESPONSE)
        self.chosen_target = chosen_target

# endregion

# region Marquise Messages


class KeepClearingResponse(ControllerMessage):
    def __init__(self, keep_clearing):
        super().__init__(ControllerMessages.KEEP_CLEARING_RESPONSE)
        self.keep_clearing = keep_clearing


class MarchAgainResponse(ControllerMessage):
    def __init__(self, march_again):
        super().__init__(ControllerMessages.MARCH_AGAIN_RESPONSE)
        self.march_again = march_again


class OverworkClearingResponse(ControllerMessage):
    def __init__(self, chosen_clearing):
        super().__init__(ControllerMessages.OVERWORK_CLEARING_RESPONSE)
        self.chosen_clearing = chosen_clearing


class OverworkDiscardResponse(ControllerMessage):
    def __init__(self, discard_choice):
        super().__init__(ControllerMessages.OVERWORK_DISCARD_RESPONSE)
        self.discard_choice = discard_choice


class MarquiseBuildingClearingResponse(ControllerMessage):
    def __init__(self, clearing):
        super().__init__(ControllerMessages.MARQUISE_BUILDING_CLEARING_RESPONSE)
        self.chosen_clearing = clearing


class MarquiseBuildingTypeResponse(ControllerMessage):
    def __init__(self, building_type):
        super().__init__(ControllerMessages.MARQUISE_BUILDING_TYPE_RESPONSE)
        self.chosen_building_type = building_type


class WoodRemovalResponse(ControllerMessage):
    def __init__(self, chosen_wood_token):
        super().__init__(ControllerMessages.WOOD_REMOVAL_RESPONSE)
        self.chosen_wood_token = chosen_wood_token


class MarquiseRecruiterSetupResponse(ControllerMessage):
    def __init__(self, recruiter_clearing):
        super().__init__(ControllerMessages.MARQUISE_RECRUITER_SETUP_RESPONSE)
        self.recruiter_clearing = recruiter_clearing


class MarquiseSawmillSetupResponse(ControllerMessage):
    def __init__(self, sawmill_clearing):
        super().__init__(ControllerMessages.MARQUISE_SAWMILL_SETUP_RESPONSE)
        self.sawmill_clearing = sawmill_clearing


class MarquiseWorkshopSetupResponse(ControllerMessage):
    def __init__(self, workshop_clearing):
        super().__init__(ControllerMessages.MARQUISE_WORKSHOP_SETUP_RESPONSE)
        self.workshop_clearing = workshop_clearing


class MarquiseSpendBirdCardResponse(ControllerMessage):
    def __init__(self, chosen_card):
        super().__init__(ControllerMessages.MARQUISE_SPEND_BIRD_CARD_RESPONSE)
        self.chosen_card = chosen_card


class FieldHospitalResponse(ControllerMessage):
    def __init__(self, chosen_card):
        super().__init__(ControllerMessages.FIELD_HOSPITAL_RESPONSE)
        self.chosen_card = chosen_card

# endregion

# region Eyrie Dynasties Messages


class RoostlessResponse(ControllerMessage):
    def __init__(self, chosen_clearing):
        super().__init__(ControllerMessages.ROOSTLESS_RESPONSE)
        self.chosen_clearing = chosen_clearing


class RoostSetupResponse(ControllerMessage):
    def __init__(self, chosen_clearing):
        super().__init__(ControllerMessages.ROOST_SETUP_RESPONSE)
        self.chosen_clearing = chosen_clearing


class LeaderSetupResponse(ControllerMessage):
    def __init__(self, chosen_leader):
        super().__init__(ControllerMessages.LEADER_SETUP_RESPONSE)
        self.chosen_leader = chosen_leader


class DecreeRecruitClearingResponse(ControllerMessage):
    def __init__(self, chosen_clearing):
        super().__init__(ControllerMessages.DECREE_RECRUIT_CLEARING_RESPONSE)
        self.chosen_clearing = chosen_clearing


class ExtendDecreeActionResponse1(ControllerMessage):
    def __init__(self, chosen_action):
        super().__init__(ControllerMessages.EXTEND_DECREE_ACTION_RESPONSE_1)
        self.chosen_action = chosen_action


class ExtendDecreeCardResponse1(ControllerMessage):
    def __init__(self, chosen_card):
        super().__init__(ControllerMessages.EXTEND_DECREE_CARD_RESPONSE_1)
        self.chosen_card = chosen_card


class ExtendDecreeActionResponse2(ControllerMessage):
    def __init__(self, chosen_action):
        super().__init__(ControllerMessages.EXTEND_DECREE_ACTION_RESPONSE_2)
        self.chosen_action = chosen_action


class ExtendDecreeCardResponse2(ControllerMessage):
    def __init__(self, chosen_card):
        super().__init__(ControllerMessages.EXTEND_DECREE_CARD_RESPONSE_2)
        self.chosen_card = chosen_card


class DecreeBuildResponse(ControllerMessage):
    def __init__(self, chosen_clearing):
        super().__init__(ControllerMessages.DECREE_BUILD_RESPONSE)
        self.chosen_clearing = chosen_clearing


class TurmoilLeaderResponse(ControllerMessage):
    def __init__(self, chosen_leader):
        super().__init__(ControllerMessages.TURMOIL_LEADER_RESPONSE)
        self.chosen_leader = chosen_leader

# endregion

# region Woodland Alliance Messages


class AllianceNoBaseResponse(ControllerMessage):
    def __init__(self, chosen_card):
        super().__init__(ControllerMessages.ALLIANCE_NO_BASE_RESPONSE)
        self.chosen_card = chosen_card


class MobilizeResponse(ControllerMessage):
    def __init__(self, chosen_card):
        super().__init__(ControllerMessages.MOBILIZE_RESPONSE)
        self.chosen_card = chosen_card


class TrainResponse(ControllerMessage):
    def __init__(self, chosen_card):
        super().__init__(ControllerMessages.TRAIN_RESPONSE)
        self.chosen_card = chosen_card


class RevoltClearingResponse(ControllerMessage):
    def __init__(self, chosen_clearing):
        super().__init__(ControllerMessages.REVOLT_CLEARING_RESPONSE)
        self.chosen_clearing = chosen_clearing


class RevoltDiscardResponse(ControllerMessage):
    def __init__(self, chosen_discard):
        super().__init__(ControllerMessages.REVOLT_DISCARD_RESPONSE)
        self.chosen_discard = chosen_discard


class SpreadSympathyClearingResponse(ControllerMessage):
    def __init__(self, chosen_clearing):
        super().__init__(ControllerMessages.SPREAD_SYMPATHY_CLEARING_RESPONSE)
        self.chosen_clearing = chosen_clearing


class SpreadSympathyDiscardResponse(ControllerMessage):
    def __init__(self, chosen_discard):
        super().__init__(ControllerMessages.SPREAD_SYMPATHY_DISCARD_RESPONSE)
        self.chosen_discard = chosen_discard


class AllianceRecruitResponse(ControllerMessage):
    def __init__(self, chosen_clearing):
        super().__init__(ControllerMessages.ALLIANCE_RECRUIT_RESPONSE)
        self.chosen_clearing = chosen_clearing


class OrganizeResponse(ControllerMessage):
    def __init__(self, chosen_unit):
        super().__init__(ControllerMessages.ORGANIZE_RESPONSE)
        self.chosen_unit = chosen_unit


class TriggererOutrageResponse(ControllerMessage):
    def __init__(self, chosen_card):
        super().__init__(ControllerMessages.TRIGGERER_OUTRAGE_RESPONSE)
        self.chosen_card = chosen_card


class AllianceOutrageResponse(ControllerMessage):
    def __init__(self, chosen_card):
        super().__init__(ControllerMessages.ALLIANCE_OUTRAGE_RESPONSE)
        self.chosen_card = chosen_card


# endregion

# region Vagabond Messages

class ChooseCharacterResponse(ControllerMessage):
    def __init__(self, chosen_character):
        super().__init__(ControllerMessages.CHOOSE_CHARACTER_RESPONSE)
        self.chosen_character = chosen_character


class VagabondPlacementResponse(ControllerMessage):
    def __init__(self, chosen_forest):
        super().__init__(ControllerMessages.VAGABOND_PLACEMENT_RESPONSE)
        self.chosen_forest = chosen_forest


class RangerRepairResponse(ControllerMessage):
    def __init__(self, item_details):
        super().__init__(ControllerMessages.RANGER_REPAIR_RESPONSE)
        self.chosen_item, self.is_exhausted, _ = item_details


class TinkerCardResponse(ControllerMessage):
    def __init__(self, chosen_card):
        super().__init__(ControllerMessages.TINKER_CARD_RESPONSE)
        self.chosen_card = chosen_card


class ThiefStealResponse(ControllerMessage):
    def __init__(self, chosen_player):
        super().__init__(ControllerMessages.THIEF_STEAL_RESPONSE)
        self.chosen_player = chosen_player


class SlipResponse(ControllerMessage):
    def __init__(self, chosen_space):
        super().__init__(ControllerMessages.SLIP_RESPONSE)
        self.chosen_space = chosen_space


class RefreshItemResponse(ControllerMessage):
    def __init__(self, item_details):
        super().__init__(ControllerMessages.REFRESH_ITEM_RESPONSE)
        self.chosen_item, _, self.is_damaged = item_details


class VagabondMoveResponse(ControllerMessage):
    def __init__(self, chosen_clearing):
        super().__init__(ControllerMessages.VAGABOND_MOVE_RESPONSE)
        self.chosen_clearing = chosen_clearing


class ChooseQuestResponse(ControllerMessage):
    def __init__(self, chosen_quest):
        super().__init__(ControllerMessages.CHOOSE_QUEST_RESPONSE)
        self.chosen_quest = chosen_quest


class ChooseQuestRewardResponse(ControllerMessage):
    def __init__(self, take_vp_reward):
        super().__init__(ControllerMessages.CHOOSE_QUEST_REWARD_RESPONSE)
        self.take_vp_reward = take_vp_reward


class RepairItemResponse(ControllerMessage):
    def __init__(self, item_details):
        super().__init__(ControllerMessages.REPAIR_ITEM_RESPONSE)
        self.chosen_item, self.is_exhausted, _ = item_details


class EmptySatchelResponse(ControllerMessage):
    def __init__(self, item_details):
        super().__init__(ControllerMessages.EMPTY_SATCHEL_RESPONSE)
        self.chosen_item, self.is_exhausted, self.is_damaged = item_details


class StrikeFactionChoiceResponse(ControllerMessage):
    def __init__(self, chosen_faction):
        super().__init__(ControllerMessages.STRIKE_FACTION_CHOICE_RESPONSE)
        self.chosen_faction = chosen_faction


class StrikePieceTargetingResponse(ControllerMessage):
    def __init__(self, chosen_piece):
        super().__init__(ControllerMessages.STRIKE_PIECE_TARGETING_RESPONSE)
        self.chosen_piece = chosen_piece


class AidFactionChoiceResponse(ControllerMessage):
    def __init__(self, chosen_faction):
        super().__init__(ControllerMessages.AID_FACTION_CHOICE_RESPONSE)
        self.chosen_faction = chosen_faction


class AidCardChoiceResponse(ControllerMessage):
    def __init__(self, chosen_card):
        super().__init__(ControllerMessages.AID_CARD_CHOICE_RESPONSE)
        self.chosen_card = chosen_card


class AidExhaustItemChoiceResponse(ControllerMessage):
    def __init__(self, item_details):
        super().__init__(ControllerMessages.AID_EXHAUST_ITEM_CHOICE_RESPONSE)
        self.chosen_item, self.use_item_track = item_details


class AidTakeItemChoiceResponse(ControllerMessage):
    def __init__(self, chosen_item):
        super().__init__(ControllerMessages.AID_TAKE_ITEM_CHOICE_RESPONSE)
        self.chosen_item = chosen_item


class BattleDamageItemResponse(ControllerMessage):
    def __init__(self, item_details):
        super().__init__(ControllerMessages.BATTLE_DAMAGE_ITEM_RESPONSE)
        self.chosen_item, self.is_exhausted, self.use_item_track = item_details


class CoalitionChoiceResponse(ControllerMessage):
    def __init__(self, chosen_faction):
        super().__init__(ControllerMessages.COALITION_CHOICE_RESPONSE)
        self.chosen_faction = chosen_faction


class AllyMovementFactionResponse(ControllerMessage):
    def __init__(self, chosen_ally):
        super().__init__(ControllerMessages.ALLY_MOVEMENT_FACTION_RESPONSE)
        self.chosen_ally = chosen_ally


class AllyMovementUnitResponse(ControllerMessage):
    def __init__(self, chosen_unit_count):
        super().__init__(ControllerMessages.ALLY_MOVEMENT_UNIT_RESPONSE)
        self.chosen_unit_count = chosen_unit_count


class ChooseAllyResponse(ControllerMessage):
    def __init__(self, chosen_ally):
        super().__init__(ControllerMessages.CHOOSE_ALLY_RESPONSE)
        self.chosen_ally = chosen_ally


class AllyDamageSplitResponse(ControllerMessage):
    def __init__(self, chosen_damage_split):
        super().__init__(ControllerMessages.ALLY_DAMAGE_SPLIT_RESPONSE)
        self.chosen_damage_split = chosen_damage_split


class QuestUseItemTrackResponse(ControllerMessage):
    def __init__(self, use_item_track):
        super().__init__(ControllerMessages.QUEST_USE_ITEM_TRACK_RESPONSE)
        self.use_item_track = use_item_track

# endregion
