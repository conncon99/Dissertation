from src.controllers.messages.controller_messages import *
from src.controllers.messages.game_messages import *
from src.controllers.nn_controllers.action_space_decoder import *


class Decoder:

    @classmethod
    def decode(cls, action, msg: GameMessage):
        logger.debug(f"Decoding {msg.type}")
        match msg.type:
            case GameMessages.ACTION_CHOICE_MESSAGE:
                return ActionChoiceResponse(decode_action_output(action, 60, msg.action_group))
            case GameMessages.AMBUSH_MESSAGE:
                return AmbushResponse(decode_card_output(action))
            case GameMessages.BATTLE_USE_CARD_MESSAGE:
                return BattleUseCardResponse(decode_binary_choice(action))
            case GameMessages.PIECE_TARGETING_MESSAGE:
                return PieceTargetingResponse(decode_piece_output(action, msg.game_state))
            case GameMessages.MOVE_FROM_MESSAGE:
                return MoveFromResponse(decode_clearing_output(action, msg.game_state))
            case GameMessages.MOVE_TO_MESSAGE:
                return MoveToResponse(decode_clearing_output(action, msg.game_state))
            case GameMessages.MOVE_UNITS_MESSAGE:
                return MoveUnitsResponse(decode_numerical_selection(action))
            case GameMessages.CRAFT_MESSAGE:
                return CraftResponse(decode_card_output(action))
            case GameMessages.DISCARD_CHOICE_MESSAGE:
                return DiscardChoiceResponse(decode_card_output(action))
            case GameMessages.CHOOSE_DOMINANCE_MESSAGE:
                return ChooseDominanceResponse(decode_card_output(action))
            case GameMessages.BETTER_BURROW_BANK_MESSAGE:
                return BetterBurrowBankResponse(decode_faction_output(action, msg.game_state))
            case GameMessages.STAND_AND_DELIVER_MESSAGE:
                return StandAndDeliverResponse(decode_faction_output(action, msg.game_state))
            case GameMessages.TAX_COLLECTOR_MESSAGE:
                return TaxCollectorResponse(decode_warrior_output(action))
            case GameMessages.CODEBREAKERS_MESSAGE:
                return CodebreakersResponse(decode_faction_output(action, msg.game_state))
            case GameMessages.CLAIM_DOMINANCE_SUIT_MESSAGE:
                return ClaimDominanceSuitResponse(decode_card_output(action))
            case GameMessages.CLAIM_DOMINANCE_CARD_MESSAGE:
                return ClaimDominanceCardResponse(decode_card_output(action))
            case GameMessages.BATTLE_CLEARING_CHOICE_MESSAGE:
                return BattleClearingChoiceResponse(decode_clearing_output(action, msg.game_state))
            case GameMessages.BATTLE_TARGET_CHOICE_MESSAGE:
                return BattleTargetResponse(decode_faction_output(action, msg.game_state))

            # Marquise Messages

            case GameMessages.KEEP_CLEARING_MESSAGE:
                return KeepClearingResponse(decode_clearing_output(action, msg.game_state))
            case GameMessages.MARCH_AGAIN_MESSAGE:
                return MarchAgainResponse(decode_binary_choice(action))
            case GameMessages.OVERWORK_CLEARING_MESSAGE:
                return OverworkClearingResponse(decode_clearing_output(action, msg.game_state))
            case GameMessages.OVERWORK_DISCARD_MESSAGE:
                return OverworkDiscardResponse(decode_card_output(action))
            case GameMessages.WOOD_REMOVAL_MESSAGE:
                return WoodRemovalResponse(decode_wood_output(action, msg.game_state))
            case GameMessages.MARQUISE_SETUP_SAWMILL_MESSAGE:
                return MarquiseSawmillSetupResponse(decode_clearing_output(action, msg.game_state))
            case GameMessages.MARQUISE_SETUP_WORKSHOP_MESSAGE:
                return MarquiseWorkshopSetupResponse(decode_clearing_output(action, msg.game_state))
            case GameMessages.MARQUISE_SETUP_RECRUITER_MESSAGE:
                return MarquiseRecruiterSetupResponse(decode_clearing_output(action, msg.game_state))
            case GameMessages.MARQUISE_BUILDING_CLEARING_MESSAGE:
                return MarquiseBuildingClearingResponse(decode_clearing_output(action, msg.game_state))
            case GameMessages.MARQUISE_BUILDING_TYPE_MESSAGE:
                return MarquiseBuildingTypeResponse(decode_marquise_building_types(action))
            case GameMessages.MARQUISE_SPEND_BIRD_CARD_MESSAGE:
                return MarquiseSpendBirdCardResponse(decode_card_output(action))
            case GameMessages.FIELD_HOSPITAL_MESSAGE:
                return FieldHospitalResponse(decode_card_output(action))

            # Eyrie Dynasty Messages

            case GameMessages.ROOSTLESS_MESSAGE:
                return RoostlessResponse(decode_clearing_output(action, msg.game_state))
            case GameMessages.ROOST_SETUP_MESSAGE:
                return RoostSetupResponse(decode_clearing_output(action, msg.game_state))
            case GameMessages.LEADER_SETUP_MESSAGE:
                return LeaderSetupResponse(decode_leader_output(action))
            case GameMessages.DECREE_RECRUIT_CLEARING_MESSAGE:
                return DecreeRecruitClearingResponse(decode_clearing_output(action, msg.game_state))
            case GameMessages.EXTEND_DECREE_ACTION_MESSAGE_1:
                return ExtendDecreeActionResponse1(decode_decree_type_output(action))
            case GameMessages.EXTEND_DECREE_CARD_MESSAGE_1:
                return ExtendDecreeCardResponse1(decode_card_output(action))
            case GameMessages.EXTEND_DECREE_ACTION_MESSAGE_2:
                return ExtendDecreeActionResponse2(decode_decree_type_output(action))
            case GameMessages.EXTEND_DECREE_CARD_MESSAGE_2:
                return ExtendDecreeCardResponse2(decode_card_output(action))
            case GameMessages.DECREE_BUILD_MESSAGE:
                return DecreeBuildResponse(decode_clearing_output(action, msg.game_state))
            case GameMessages.TURMOIL_LEADER_MESSAGE:
                return TurmoilLeaderResponse(decode_leader_output(action))

            # Woodland Alliance Messages

            case GameMessages.ALLIANCE_NO_BASE_MESSAGE:
                return AllianceNoBaseResponse(decode_card_output(action))
            case GameMessages.MOBILIZE_MESSAGE:
                return MobilizeResponse(decode_card_output(action))
            case GameMessages.TRAIN_MESSAGE:
                return TrainResponse(decode_card_output(action))
            case GameMessages.REVOLT_CLEARING_MESSAGE:
                return RevoltClearingResponse(decode_clearing_output(action, msg.game_state))
            case GameMessages.REVOLT_DISCARD_MESSAGE:
                return RevoltDiscardResponse(decode_card_output(action))
            case GameMessages.SPREAD_SYMPATHY_CLEARING_MESSAGE:
                return SpreadSympathyClearingResponse(decode_clearing_output(action, msg.game_state))
            case GameMessages.SPREAD_SYMPATHY_DISCARD_MESSAGE:
                return SpreadSympathyDiscardResponse(decode_card_output(action))
            case GameMessages.ALLIANCE_RECRUIT_MESSAGE:
                return AllianceRecruitResponse(decode_clearing_output(action, msg.game_state))
            case GameMessages.ORGANIZE_MESSAGE:
                return OrganizeResponse(decode_warrior_output(action))
            case GameMessages.TRIGGERER_OUTRAGE_MESSAGE:
                return TriggererOutrageResponse(decode_card_output(action))
            case GameMessages.ALLIANCE_OUTRAGE_MESSAGE:
                return AllianceOutrageResponse(decode_card_output(action))

            # Vagabond Messages

            case GameMessages.CHOOSE_CHARACTER_MESSAGE:
                return ChooseCharacterResponse(decode_character_output(action))
            case GameMessages.VAGABOND_PLACEMENT_MESSAGE:
                return VagabondPlacementResponse(decode_forest_output(action, msg.game_state))
            case GameMessages.RANGER_REPAIR_MESSAGE:
                return RangerRepairResponse(decode_item_output(action))
            case GameMessages.TINKER_CARD_MESSAGE:
                return TinkerCardResponse(decode_card_output(action))
            case GameMessages.THIEF_STEAL_MESSAGE:
                return ThiefStealResponse(decode_faction_output(action, msg.game_state))
            case GameMessages.SLIP_MESSAGE:
                return SlipResponse(decode_space_output(action, msg.game_state))
            case GameMessages.REFRESH_ITEM_MESSAGE:
                return RefreshItemResponse(decode_item_output(action))
            case GameMessages.VAGABOND_MOVE_MESSAGE:
                return VagabondMoveResponse(decode_clearing_output(action, msg.game_state))
            case GameMessages.CHOOSE_QUEST_MESSAGE:
                return ChooseQuestResponse(decode_quest_output(action))
            case GameMessages.QUEST_USE_ITEM_TRACK_MESSAGE:
                return QuestUseItemTrackResponse(decode_binary_choice(action))
            case GameMessages.CHOOSE_QUEST_REWARD_MESSAGE:
                return ChooseQuestRewardResponse(decode_binary_choice(action))
            case GameMessages.REPAIR_ITEM_MESSAGE:
                return RepairItemResponse(decode_item_output(action))
            case GameMessages.EMPTY_SATCHEL_MESSAGE:
                return EmptySatchelResponse(decode_item_output(action))
            case GameMessages.STRIKE_FACTION_CHOICE_MESSAGE:
                return StrikeFactionChoiceResponse(decode_faction_output(action, msg.game_state))
            case GameMessages.STRIKE_PIECE_TARGETING_MESSAGE:
                assert isinstance(msg, StrikePieceTargetingMessage)
                return StrikePieceTargetingResponse(decode_strike_output(action, msg.chosen_faction, msg.game_state))
            case GameMessages.AID_FACTION_CHOICE_MESSAGE:
                return AidFactionChoiceResponse(decode_faction_output(action, msg.game_state))
            case GameMessages.AID_CARD_CHOICE_MESSAGE:
                return AidCardChoiceResponse(decode_card_output(action))
            case GameMessages.AID_EXHAUST_ITEM_CHOICE_MESSAGE:
                return AidExhaustItemChoiceResponse(decode_aid_exhaust_item(action))
            case GameMessages.AID_TAKE_ITEM_CHOICE_MESSAGE:
                return AidTakeItemChoiceResponse(decode_aid_take_item_output(action))
            case GameMessages.BATTLE_DAMAGE_ITEM_MESSAGE:
                return BattleDamageItemResponse(decode_battle_damage_item(action))
            case GameMessages.COALITION_CHOICE_MESSAGE:
                return CoalitionChoiceResponse(decode_faction_output(action, msg.game_state))
            case GameMessages.ALLY_MOVEMENT_FACTION_MESSAGE:
                return AllyMovementFactionResponse(decode_faction_output(action, msg.game_state))
            case GameMessages.ALLY_MOVEMENT_UNITS_MESSAGE:
                return AllyMovementUnitResponse(decode_numerical_selection(action))
            case GameMessages.CHOOSE_ALLY_MESSAGE:
                return ChooseAllyResponse(decode_faction_output(action, msg.game_state))
            case GameMessages.ALLY_DAMAGE_SPLIT_MESSAGE:
                return AllyDamageSplitResponse(decode_numerical_selection(action))


# action is supposedly a 56 long float vector - if this is the case, the decode messages will need to change to argmax the action
# Depending on the GameMessage, choose correct type of ControllerResponse
# Depending on ControllerResponse expected type, convert action to match that
