from controllers.messages.controller_messages import *
from controllers.messages.game_messages import *
from controllers.nn_controllers.action_space_decoder import *


# TODO: All Responses need to be changed to only produce one output


class Decoder:

    @classmethod
    def decode(cls, action, message_type, game_state, action_group):
        mapping = {
            # Factionless Messages
            GameMessages.ACTION_CHOICE_MESSAGE: ActionChoiceResponse(decode_action_output(action), 56, action_group),
            # GameMessages.BATTLE_START_MESSAGE: None,
            # GameMessages.BATTLE_END_MESSAGE: None,
            GameMessages.BATTLE_USE_CARD_MESSAGE: BattleUseCardResponse(decode_card_output(action)),
            GameMessages.PIECE_TARGETING_MESSAGE: PieceTargetingResponse(decode_piece_output(action, game_state)),
            # GameMessages.MOVE_MESSAGE: MoveResponse() # TODO
            # GameMessages.MOVE_UNITS_MESSAGE: # TODO
            GameMessages.CRAFT_MESSAGE: CraftResponse(decode_card_output(action)),
            GameMessages.DISCARD_CHOICE_MESSAGE: DiscardChoiceResponse(decode_card_output(action)),
            GameMessages.CHOOSE_DOMINANCE_MESSAGE: ChooseDominanceResponse(decode_card_output(action)),
            GameMessages.BETTER_BURROW_BANK_MESSAGE: BetterBurrowBankResponse(decode_faction_output(action, game_state)),
            GameMessages.STAND_AND_DELIVER_MESSAGE: StandAndDeliverResponse(decode_faction_output(action, game_state)),
            GameMessages.TAX_COLLECTOR_MESSAGE: TaxCollectorResponse(decode_warrior_output(action)),
            GameMessages.CODEBREAKERS_MESSAGE: CodebreakersResponse(decode_faction_output(action, game_state)),
            GameMessages.CLAIM_DOMINANCE_SUIT_MESSAGE: ClaimDominanceSuitResponse(decode_card_output(action)),
            GameMessages.CLAIM_DOMINANCE_CARD_MESSAGE: ClaimDominanceCardResponse(decode_card_output(action)),
            GameMessages.BATTLE_CLEARING_CHOICE_MESSAGE: BattleClearingChoiceResponse(decode_clearing_output(action, game_state)),
            GameMessages.BATTLE_TARGET_CHOICE_MESSAGE: BattleTargetResponse(decode_faction_output(action, game_state)),

            # Marquise Messages

            GameMessages.KEEP_CLEARING_MESSAGE: KeepClearingResponse(decode_clearing_output(action, game_state)),
            # GameMessages.MARCH_1_MESSAGE:,
            # GameMessages.MARCH_1_UNITS_MESSAGE:,
            # GameMessages.MARCH_2_MESSAGE:,
            # GameMessages.MARCH_2_CHOICE_MESSAGE:,
            # GameMessages.MARCH_2_UNITS_MESSAGE:,
            GameMessages.OVERWORK_CLEARING_MESSAGE: OverworkClearingResponse(decode_clearing_output(action, game_state)),
            GameMessages.OVERWORK_DISCARD_MESSAGE: OverworkDiscardResponse(decode_card_output(action)),
            # GameMessages.MARQUISE_BUILDING_MESSAGE: MarquiseBuildingResponse(),
            GameMessages.WOOD_REMOVAL_MESSAGE: WoodRemovalResponse(decode_wood_output(action, game_state)),
            # GameMessages.MARQUISE_SETUP_BUILDINGS_MESSAGE:
            # GameMessages.MARQUISE_SETUP_SAWMILL_MESSAGE:,
            # GameMessages.MARQUISE_SETUP_WORKSHOP_MESSAGE:,
            # GameMessages.MARQUISE_SETUP_RECRUITER_MESSAGE:,
            # GameMessages.MARQUISE_BUILDING_TYPE_MESSAGE:,
            GameMessages.MARQUISE_SPEND_BIRD_CARD_MESSAGE: MarquiseSpendBirdCardResponse(decode_card_output(action)),
            GameMessages.FIELD_HOSPITAL_MESSAGE: FieldHospitalResponse(decode_card_output(action)),

            # Eyrie Dynasty Messages

            GameMessages.ROOSTLESS_MESSAGE: RoostlessResponse(decode_clearing_output(action, game_state)),
            GameMessages.ROOST_SETUP_MESSAGE: RoostSetupResponse(decode_clearing_output(action, game_state)),
            GameMessages.LEADER_SETUP_MESSAGE: LeaderSetupResponse(decode_leader_output(action)),
            GameMessages.DECREE_RECRUIT_CLEARING_MESSAGE: DecreeRecruitClearingResponse(decode_clearing_output(action, game_state)),
            GameMessages.EXTEND_DECREE_ACTION_MESSAGE_1: ExtendDecreeActionResponse1(decode_decree_type_output(action)),
            GameMessages.EXTEND_DECREE_CARD_MESSAGE_1: ExtendDecreeCardResponse1(decode_card_output(action)),
            GameMessages.EXTEND_DECREE_ACTION_MESSAGE_2: ExtendDecreeActionResponse2(decode_decree_type_output(action)),
            GameMessages.EXTEND_DECREE_CARD_MESSAGE_2: ExtendDecreeCardResponse2(decode_card_output(action)),
            GameMessages.DECREE_BUILD_MESSAGE: DecreeBuildResponse(decode_clearing_output(action, game_state)),
            GameMessages.TURMOIL_LEADER_MESSAGE: TurmoilLeaderResponse(decode_leader_output(action)),

            # Woodland Alliance Messages

            GameMessages.ALLIANCE_NO_BASE_MESSAGE: AllianceNoBaseResponse(decode_card_output(action)),
            GameMessages.MOBILIZE_MESSAGE: MobilizeResponse(decode_card_output(action)),
            GameMessages.TRAIN_MESSAGE: TrainResponse(decode_card_output(action)),
            GameMessages.REVOLT_CLEARING_MESSAGE: RevoltClearingResponse(decode_clearing_output(action, game_state)),
            GameMessages.REVOLT_DISCARD_MESSAGE: RevoltDiscardResponse(decode_card_output(action)),
            GameMessages.SPREAD_SYMPATHY_CLEARING_MESSAGE: SpreadSympathyClearingResponse(decode_clearing_output(action, game_state)),
            GameMessages.SPREAD_SYMPATHY_DISCARD_MESSAGE: SpreadSympathyDiscardResponse(decode_card_output(action)),
            GameMessages.ALLIANCE_RECRUIT_MESSAGE: AllianceRecruitResponse(decode_clearing_output(action, game_state)),
            GameMessages.ORGANIZE_MESSAGE: OrganizeResponse(decode_warrior_output(action)),
            GameMessages.TRIGGERER_OUTRAGE_MESSAGE: TriggererOutrageResponse(decode_card_output(action)),
            GameMessages.ALLIANCE_OUTRAGE_MESSAGE: AllianceOutrageResponse(decode_card_output(action)),

            # Vagabond Messages

            # GameMessages.CHOOSE_CHARACTER_MESSAGE: ChooseCharacterResponse,
            # GameMessages.VAGABOND_PLACEMENT_MESSAGE: VagabondPlacementResponse(),
            # GameMessages.RANGER_REPAIR_MESSAGE:,
            GameMessages.TINKER_CARD_MESSAGE: TinkerCardResponse(decode_card_output(action)),
            GameMessages.THIEF_STEAL_MESSAGE: ThiefStealResponse(decode_faction_output(action, game_state)),
            # GameMessages.SLIP_MESSAGE:,
            # GameMessages.REFRESH_ITEM_MESSAGE:,
            # GameMessages.VAGABOND_MOVE_MESSAGE:,
            # GameMessages.CHOOSE_QUEST_MESSAGE:,
            # GameMessages.QUEST_USE_ITEM_TRACK_MESSAGE:,
            GameMessages.CHOOSE_QUEST_REWARD_MESSAGE: ChooseQuestRewardResponse(decode_binary_choice(action)),
            # GameMessages.REPAIR_ITEM_MESSAGE:,
            # GameMessages.EMPTY_SATCHEL_MESSAGE:,
            GameMessages.STRIKE_FACTION_CHOICE_MESSAGE: StrikeFactionChoiceResponse(decode_faction_output(action, game_state)),
            # GameMessages.STRIKE_PIECE_TARGETING_MESSAGE: StrikePieceTargetingResponse(decode_piece_output()),
            GameMessages.AID_FACTION_CHOICE_MESSAGE: AidFactionChoiceResponse(decode_faction_output(action, game_state)),
            GameMessages.AID_CARD_CHOICE_MESSAGE: AidCardChoiceResponse(decode_card_output(action)),
            # GameMessages.AID_EXHAUST_ITEM_CHOICE_MESSAGE:,
            # GameMessages.AID_TAKE_ITEM_CHOICE_MESSAGE:,
            # GameMessages.BATTLE_DAMAGE_ITEM_MESSAGE:,
            GameMessages.COALITION_CHOICE_MESSAGE: CoalitionChoiceResponse(decode_faction_output(action, game_state)),
            # GameMessages.ALLY_MOVEMENT_MESSAGE: AllyMovementResponse(),
            GameMessages.CHOOSE_ALLY_MESSAGE: ChooseAllyResponse(decode_faction_output(action, game_state)),
            GameMessages.ALLY_DAMAGE_SPLIT_MESSAGE: AllyDamageSplitResponse(decode_numerical_selection(action)),
        }
        return mapping[message_type]


# action is supposedly a 56 long float vector - if this is the case, the decode messages will need to change to argmax the action
# Depending on the GameMessage, choose correct type of ControllerResponse
# Depending on ControllerResponse expected type, convert action to match that
