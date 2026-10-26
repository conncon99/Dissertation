from __future__ import annotations
from src.utils.game_state import GameState
from typing import List, TYPE_CHECKING, Type, Union
from src.utils.root_types import Factions, EyrieLeaders
from src.cards.cards import *
from src.pieces.marquise_de_cat.marquise_buildings import Sawmill, Workshop, Recruiter
from src.board.forest import Forest
from src.factions.vagabond.quests import *
from src.actions.action_group_registry import ActionIDs
from src.controllers.messages.game_messages import *

if TYPE_CHECKING:
    from src.actions.action_handler import Action
    from src.board.clearing import Clearing
    from src.cards.card import Card
    from src.factions.faction import Faction
    from src.pieces.pawn import Pawn
    from src.pieces.piece import Piece
    from src.pieces.marquise_de_cat.marquise_tokens import Wood
    from src.board.space import Space
    import logging


class Mask:

    def __init__(self, action_size=340):
        self.action_size = action_size
        self.logger = logging.getLogger()

    def create_mask(self, msg: GameMessage) -> List[bool]:
        self.logger.debug(f"Masking {msg.type}")
        match msg.type:
            case GameMessages.ACTION_CHOICE_MESSAGE:
                assert isinstance(msg, ActionChoiceMessage)
                return self.action_mask(msg.available_actions, msg.action_group.can_abort)
            case GameMessages.AMBUSH_MESSAGE:
                assert isinstance(msg, AmbushMessage)
                return self.card_mask(msg.available_ambush_cards, allow_none=True)
            case GameMessages.BATTLE_USE_CARD_MESSAGE:
                assert isinstance(msg, BattleUseCardMessage)
                return self.binary_mask()
            case GameMessages.PIECE_TARGETING_MESSAGE:
                assert isinstance(msg, PieceTargetingMessage)
                return self.piece_mask(msg.targets)
            case GameMessages.MOVE_FROM_MESSAGE:
                assert isinstance(msg, MoveFromMessage)
                return self.clearing_mask(msg.available_from_clearings)
            case GameMessages.MOVE_TO_MESSAGE:
                assert isinstance(msg, MoveToMessage)
                return self.clearing_mask(msg.available_to_clearings)
            case GameMessages.MOVE_UNITS_MESSAGE:
                assert isinstance(msg, MoveUnitsMessage)
                return self.numerical_mask(1, len(msg.available_units))
            case GameMessages.CRAFT_MESSAGE:
                assert isinstance(msg, CraftMessage)
                return self.card_mask(msg.crafting_options)
            case GameMessages.DISCARD_CHOICE_MESSAGE:
                assert isinstance(msg, DiscardChoiceMessage)
                return self.card_mask(msg.discard_options)
            case GameMessages.CHOOSE_DOMINANCE_MESSAGE:
                assert isinstance(msg, ChooseDominanceMessage)
                return self.card_mask(msg.available_cards)
            case GameMessages.BETTER_BURROW_BANK_MESSAGE:
                assert isinstance(msg, BetterBurrowBankMessage)
                return self.faction_mask(msg.available_players, msg.game_state)
            case GameMessages.STAND_AND_DELIVER_MESSAGE:
                assert isinstance(msg, StandAndDeliverMessage)
                return self.faction_mask(msg.available_players, msg.game_state)
            case GameMessages.TAX_COLLECTOR_MESSAGE:
                assert isinstance(msg, TaxCollectorMessage)
                return self.warrior_mask(msg.available_units)
            case GameMessages.CODEBREAKERS_MESSAGE:
                assert isinstance(msg, CodebreakersMessage)
                return self.faction_mask(msg.available_players, msg.game_state)
            case GameMessages.CLAIM_DOMINANCE_SUIT_MESSAGE:
                assert isinstance(msg, ClaimDominanceSuitMessage)
                return self.card_mask(msg.available_dominance_cards)
            case GameMessages.CLAIM_DOMINANCE_CARD_MESSAGE:
                assert isinstance(msg, ClaimDominanceCardMessage)
                return self.card_mask(msg.available_discard_cards)
            case GameMessages.BATTLE_CLEARING_CHOICE_MESSAGE:
                assert isinstance(msg, BattleClearingChoiceMessage)
                return self.clearing_mask(msg.available_clearings)
            case GameMessages.BATTLE_TARGET_CHOICE_MESSAGE:
                assert isinstance(msg, BattleTargetChoiceMessage)
                return self.faction_mask(msg.battle_target_list, msg.game_state)

            # Marquise Messages

            case GameMessages.KEEP_CLEARING_MESSAGE:
                assert isinstance(msg, KeepClearingMessage)
                return self.clearing_mask(msg.available_clearings)
            case GameMessages.MARCH_AGAIN_MESSAGE:
                assert isinstance(msg, MarchAgainMessage)
                return self.binary_mask()
            case GameMessages.OVERWORK_CLEARING_MESSAGE:
                assert isinstance(msg, OverworkClearingMessage)
                return self.clearing_mask(msg.available_clearings)
            case GameMessages.OVERWORK_DISCARD_MESSAGE:
                assert isinstance(msg, OverworkDiscardMessage)
                return self.card_mask(msg.available_cards)
            case GameMessages.WOOD_REMOVAL_MESSAGE:
                assert isinstance(msg, WoodRemovalMessage)
                return self.wood_mask(msg.wood_list)
            case GameMessages.MARQUISE_SETUP_SAWMILL_MESSAGE:
                assert isinstance(msg, MarquiseSawmillSetupMessage)
                return self.clearing_mask(msg.available_clearings)
            case GameMessages.MARQUISE_SETUP_WORKSHOP_MESSAGE:
                assert isinstance(msg, MarquiseWorkshopSetupMessage)
                return self.clearing_mask(msg.available_clearings)
            case GameMessages.MARQUISE_SETUP_RECRUITER_MESSAGE:
                assert isinstance(msg, MarquiseRecruiterSetupMessage)
                return self.clearing_mask(msg.available_clearings)
            case GameMessages.MARQUISE_BUILDING_CLEARING_MESSAGE:
                assert isinstance(msg, MarquiseBuildingClearingMessage)
                return self.clearing_mask(msg.clearing_building_options)
            case GameMessages.MARQUISE_BUILDING_TYPE_MESSAGE:
                assert isinstance(msg, MarquiseBuildingTypeMessage)
                return self.marquise_building_type_mask(msg.clearing_building_options)
            case GameMessages.MARQUISE_SPEND_BIRD_CARD_MESSAGE:
                assert isinstance(msg, MarquiseSpendBirdCardMessage)
                return self.card_mask(msg.bird_cards)
            case GameMessages.FIELD_HOSPITAL_MESSAGE:
                assert isinstance(msg, FieldHospitalMessage)
                return self.card_mask(msg.available_cards, allow_none=True)

            # Eyrie Dynasty Messages

            case GameMessages.ROOSTLESS_MESSAGE:
                assert isinstance(msg, RoostlessMessage)
                return self.clearing_mask(msg.available_clearings)
            case GameMessages.ROOST_SETUP_MESSAGE:
                assert isinstance(msg, RoostSetupMessage)
                return self.clearing_mask(msg.available_clearings)
            case GameMessages.LEADER_SETUP_MESSAGE:
                assert isinstance(msg, LeaderSetupMessage)
                return self.eyrie_leader_mask(msg.leader_choices)
            case GameMessages.DECREE_RECRUIT_CLEARING_MESSAGE:
                assert isinstance(msg, DecreeRecruitClearingMessage)
                return self.clearing_mask(msg.available_clearings)
            case GameMessages.EXTEND_DECREE_ACTION_MESSAGE_1:
                assert isinstance(msg, ExtendDecreeActionMessage1)
                return self.decree_type_mask()
            case GameMessages.EXTEND_DECREE_CARD_MESSAGE_1:
                assert isinstance(msg, ExtendDecreeCardMessage1)
                return self.card_mask(msg.available_cards)
            case GameMessages.EXTEND_DECREE_ACTION_MESSAGE_2:
                assert isinstance(msg, ExtendDecreeActionMessage2)
                return self.decree_type_mask(allow_none=True)
            case GameMessages.EXTEND_DECREE_CARD_MESSAGE_2:
                assert isinstance(msg, ExtendDecreeCardMessage2)
                return self.card_mask(msg.available_cards)
            case GameMessages.DECREE_BUILD_MESSAGE:
                assert isinstance(msg, DecreeBuildMessage)
                return self.clearing_mask(msg.available_clearings)
            case GameMessages.TURMOIL_LEADER_MESSAGE:
                assert isinstance(msg, TurmoilLeaderMessage)
                return self.eyrie_leader_mask(msg.available_leaders)

            # Woodland Alliance Messages

            case GameMessages.ALLIANCE_NO_BASE_MESSAGE:
                assert isinstance(msg, AllianceNoBaseMessage)
                return self.card_mask(msg.supporters)
            case GameMessages.MOBILIZE_MESSAGE:
                assert isinstance(msg, MobilizeMessage)
                return self.card_mask(msg.available_cards)
            case GameMessages.TRAIN_MESSAGE:
                assert isinstance(msg, TrainMessage)
                return self.card_mask(msg.available_cards)
            case GameMessages.REVOLT_CLEARING_MESSAGE:
                assert isinstance(msg, RevoltClearingMessage)
                return self.clearing_mask(msg.available_clearings)
            case GameMessages.REVOLT_DISCARD_MESSAGE:
                assert isinstance(msg, RevoltDiscardMessage)
                return self.card_mask(msg.valid_supporters)
            case GameMessages.SPREAD_SYMPATHY_CLEARING_MESSAGE:
                assert isinstance(msg, SpreadSympathyClearingMessage)
                return self.clearing_mask(msg.available_clearings)
            case GameMessages.SPREAD_SYMPATHY_DISCARD_MESSAGE:
                assert isinstance(msg, SpreadSympathyDiscardMessage)
                return self.card_mask(msg.available_supporters)
            case GameMessages.ALLIANCE_RECRUIT_MESSAGE:
                assert isinstance(msg, AllianceRecruitMessage)
                return self.clearing_mask(msg.available_clearings)
            case GameMessages.ORGANIZE_MESSAGE:
                assert isinstance(msg, OrganizeMessage)
                return self.warrior_mask(msg.game_state.woodland_alliance.units)
            case GameMessages.TRIGGERER_OUTRAGE_MESSAGE:
                assert isinstance(msg, TriggererOutrageMessage)
                return self.card_mask(msg.valid_cards)
            case GameMessages.ALLIANCE_OUTRAGE_MESSAGE:
                assert isinstance(msg, AllianceOutrageMessage)
                return self.card_mask(msg.triggerer_hand)

            # Vagabond Messages

            case GameMessages.CHOOSE_CHARACTER_MESSAGE:
                assert isinstance(msg, ChooseCharacterMessage)
                return self.vagabond_characters_mask()
            case GameMessages.VAGABOND_PLACEMENT_MESSAGE:
                assert isinstance(msg, VagabondPlacementMessage)
                return self.forest_mask(msg.available_forests)
            case GameMessages.RANGER_REPAIR_MESSAGE:
                assert isinstance(msg, RangerRepairMessage)
                return self.item_mask([], [], msg.available_damaged, msg.exhausted_damaged)
            case GameMessages.TINKER_CARD_MESSAGE:
                assert isinstance(msg, TinkerCardMessage)
                return self.card_mask(msg.available_cards)
            case GameMessages.THIEF_STEAL_MESSAGE:
                assert isinstance(msg, ThiefStealMessage)
                return self.faction_mask(msg.available_players, msg.game_state)
            case GameMessages.SLIP_MESSAGE:
                assert isinstance(msg, SlipMessage)
                return self.space_mask(msg.available_spaces)
            case GameMessages.REFRESH_ITEM_MESSAGE:
                assert isinstance(msg, RefreshItemMessage)
                return self.item_mask([], msg.undamaged_items, [], msg.damaged_items)
            case GameMessages.VAGABOND_MOVE_MESSAGE:
                assert isinstance(msg, VagabondMoveMessage)
                return self.clearing_mask(msg.clearing_dict)
            case GameMessages.CHOOSE_QUEST_MESSAGE:
                assert isinstance(msg, ChooseQuestMessage)
                return self.quest_mask(msg.available_quests)
            case GameMessages.QUEST_USE_ITEM_TRACK_MESSAGE:
                assert isinstance(msg, QuestUseItemTrackMessage)
                return self.binary_mask()
            case GameMessages.CHOOSE_QUEST_REWARD_MESSAGE:
                assert isinstance(msg, ChooseQuestRewardMessage)
                return self.binary_mask()
            case GameMessages.REPAIR_ITEM_MESSAGE:
                assert isinstance(msg, RepairItemMessage)
                return self.item_mask([], [], msg.available_damaged, msg.exhausted_damaged)
            case GameMessages.EMPTY_SATCHEL_MESSAGE:
                assert isinstance(msg, EmptySatchelMessage)
                return self.item_mask(msg.available_items, msg.exhausted_items, msg.available_damaged_items, msg.exhausted_damaged_items)
            case GameMessages.STRIKE_FACTION_CHOICE_MESSAGE:
                assert isinstance(msg, StrikeFactionChoiceMessage)
                return self.faction_mask(msg.available_factions, msg.game_state)
            case GameMessages.STRIKE_PIECE_TARGETING_MESSAGE:
                assert isinstance(msg, StrikePieceTargetingMessage)
                return self.strike_mask(msg.chosen_faction, msg.available_pieces, msg.game_state)
            case GameMessages.AID_FACTION_CHOICE_MESSAGE:
                assert isinstance(msg, AidFactionChoiceMessage)
                return self.faction_mask(msg.available_factions, msg.game_state)
            case GameMessages.AID_CARD_CHOICE_MESSAGE:
                assert isinstance(msg, AidCardChoiceMessage)
                return self.card_mask(msg.available_cards)
            case GameMessages.AID_EXHAUST_ITEM_CHOICE_MESSAGE:
                assert isinstance(msg, AidExhaustItemChoiceMessage)
                return self.aid_exhaust_item_mask(msg.available_items, msg.bag_track, msg.coin_track, msg.tea_track)
            case GameMessages.AID_TAKE_ITEM_CHOICE_MESSAGE:
                assert isinstance(msg, AidTakeItemChoiceMessage)
                return self.aid_take_item_mask(msg.available_items)
            case GameMessages.BATTLE_DAMAGE_ITEM_MESSAGE:
                assert isinstance(msg, BattleDamageItemMessage)
                return self.battle_damage_item(msg.available_items, msg.exhausted_items, msg.active_bag_count, msg.active_coin_count, msg.active_tea_count)
            case GameMessages.COALITION_CHOICE_MESSAGE:
                assert isinstance(msg, CoalitionChoiceMessage)
                return self.faction_mask(msg.available_factions, msg.game_state)
            case GameMessages.ALLY_MOVEMENT_FACTION_MESSAGE:
                assert isinstance(msg, AllyMovementFactionMessage)
                return self.faction_mask(msg.available_allies, msg.game_state, allow_none=True)
            case GameMessages.ALLY_MOVEMENT_UNITS_MESSAGE:
                assert isinstance(msg, AllyMovementUnitMessage)
                return self.numerical_mask(1, len(msg.from_clearing.units[msg.chosen_ally.faction_id]))
            case GameMessages.CHOOSE_ALLY_MESSAGE:
                assert isinstance(msg, ChooseAllyMessage)
                return self.faction_mask(msg.available_allies, msg.game_state, allow_none=True)
            case GameMessages.ALLY_DAMAGE_SPLIT_MESSAGE:
                assert isinstance(msg, AllyDamageSplitMessage)
                return self.numerical_mask(0, msg.max_damage)
        raise TypeError(f"Invalid GameMessage {msg.type}")

    ### Factionless ###

    def binary_mask(self):
        """Masks all but index 0 and 1"""
        mask = [False] * self.action_size
        mask[0:2] = [True] * 2
        return mask

    def numerical_mask(self, min, max):
        """Masks all but the values between min and max (inclusive)"""
        min += 235
        max += 235
        mask = [False] * self.action_size
        mask[min: max + 1] = [True] * ((max + 1) - min)
        return mask

    def clearing_mask(self, available_clearings: List[Clearing]):
        """Masks out all unavailable clearings or invalid outputs"""
        mask = [False] * self.action_size
        for clearing in available_clearings:
            mask[clearing.index + 66] = True
        return mask

    def card_mask(self, available_cards: List[Card], allow_none=False):
        mask = [False] * self.action_size
        mask[-1] = allow_none

        cards = [
            SWORD_MOUSE,  # 0
            TRAVEL_GEAR_FOX,  # 1
            TRAVEL_GEAR_MOUSE,  # 2
            WOODLAND_RUNNERS,  # 3
            ANVIL,  # 4
            ARMS_TRADER,  # 5
            A_VISIT_TO_FRIENDS,  # 6
            BAKE_SALE,  # 7
            BIRDY_BUNDLE,  # 8
            CROSSBOW_BIRD,  # 9
            CROSSBOW_MOUSE,  # 10
            FOXFOLK_STEEL,  # 11
            GENTLY_USED_KNAPSACK,  # 12
            INVESTMENTS,  # 13
            MOUSE_IN_A_SACK,  # 14
            PROTECTION_RACKET,  # 15
            ROOT_TEA_RABBIT,  # 16
            ROOT_TEA_FOX,  # 17
            ROOT_TEA_MOUSE,  # 18
            SMUGGLERS_TRAIL,  # 19
            # Ambush Cards
            BIRD_AMBUSH,  # 20
            BIRD_AMBUSH_2,  # 21
            FOX_AMBUSH,  # 22
            MOUSE_AMBUSH,  # 23
            RABBIT_AMBUSH,  # 24
            # Dominance Cards
            FOX_DOMINANCE,  # 25
            MOUSE_DOMINANCE,  # 26
            RABBIT_DOMINANCE,  # 27
            BIRD_DOMINANCE,  # 28
            # Favour Cards
            FAVOR_OF_THE_RABBITS,  # 29
            FAVOR_OF_THE_FOXES,  # 30
            FAVOR_OF_THE_MICE,  # 31
            # Misc Cards
            SCOUTING_PARTY,  # 32
            SCOUTING_PARTY_2,  # 33
            COMMAND_WARREN,  # 34
            COMMAND_WARREN_2,  # 35
            COBBLER,  # 36
            COBBLER_2,  # 37
            SAPPERS,  # 38
            SAPPERS_2,  # 39
            BRUTAL_TACTICS,  # 40
            BRUTAL_TACTICS_2,  # 41
            ARMORERS,  # 42
            ARMORERS_2,  # 43
            BETTER_BURROW_BANK,  # 44
            BETTER_BURROW_BANK_2,  # 45
            STAND_AND_DELIVER,  # 46
            STAND_AND_DELIVER_2,  # 47
            TAX_COLLECTOR,  # 48
            TAX_COLLECTOR_2,  # 49
            TAX_COLLECTOR_3,  # 50
            CODEBREAKERS,  # 51
            CODEBREAKERS_2,  # 52
            ROYAL_CLAIM  # 53
        ]
        for i, card in enumerate(cards):
            mask[i + 78] = card in available_cards

        return mask

    def faction_mask(
            self, available_factions: List[Faction], game_state: GameState, allow_none=False):
        mask = [False] * self.action_size
        mask[-1] = allow_none
        offset = 62

        mask[0 + offset] = game_state.marquise in available_factions
        mask[1 + offset] = game_state.eyrie_dynasties in available_factions
        mask[2 + offset] = game_state.woodland_alliance in available_factions
        mask[3 + offset] = game_state.vagabond in available_factions

        return mask

    def warrior_mask(
            self, available_warriors: List[Pawn], allow_none=False):
        mask = [False] * self.action_size

        mask[-1] = allow_none

        base_offset = 179

        faction_offsets = {Factions.MARQUISE_DE_CAT.value: 0, Factions.EYRIE_DYNASTY.value: 25,
                           Factions.WOODLAND_ALLIANCE.value: 45, Factions.VAGABOND.value: 55}

        for warrior in available_warriors:
            mask[warrior.id + faction_offsets[warrior.faction.faction_id] +
                 base_offset] = True
        return mask

    def piece_mask(self, available_pieces: List[Piece], allow_none=False):
        mask = [False] * self.action_size
        mask[-1] = allow_none

        offset = 132
        for piece in available_pieces:
            mask[self._get_piece_offset(piece) + piece.id + offset] = True
        return mask

    def _get_piece_offset(self, piece) -> int:
        # 7 Roosts # 0 - 6
        # 6 Sawmills 7 - 12
        # 6 Workshops - 13 - 18
        # 6 Recruiters - 19 - 24
        # 8 Wood - 25 - 32
        # 1 Keep - 33
        # 3 Alliance Bases - 34 - 36
        # 10 Sympathy - 37 - 46
        ROOST_OFFSET = 0
        SAWMILL_OFFSET = 7
        WORKSHOP_OFFSET = 13
        RECRUITER_OFFSET = 19
        WOOD_OFFSET = 25
        KEEP_OFFSET = 33
        ALLIANCE_OFFSET = 34
        SYMPATHY_OFFSET = 37

        offset_types = {"Roost": ROOST_OFFSET, "Sawmill": SAWMILL_OFFSET, "Workshop": WORKSHOP_OFFSET, "Recruiter": RECRUITER_OFFSET, "Wood Token": WOOD_OFFSET, "Keep Token": KEEP_OFFSET,
                        "Alliance Fox Base": ALLIANCE_OFFSET, "Alliance Mouse Base": ALLIANCE_OFFSET + 2, "Alliance Rabbit Base": ALLIANCE_OFFSET + 1, "Sympathy Token": SYMPATHY_OFFSET}
        return offset_types[piece.name]

    def action_mask(
            self, available_actions: List[Action], allow_none=False):
        mask = [False] * self.action_size
        mask[-1] = allow_none
        offset = 2

        for action in available_actions:
            if action is not None:
                mask[action.id.value - 1 + offset] = True

        return mask

    ### Marquise ###

    def wood_mask(self, available_wood: List[Wood]):
        mask = [False] * self.action_size
        offset = 263
        for wood in available_wood:
            mask[wood.id + offset] = True
        return mask

    def marquise_building_type_mask(self, available_building_types: List[Union[Type[Sawmill], Type[Recruiter], Type[Workshop]]]):
        mask = [False] * self.action_size
        offset = 260
        mask[0 + offset] = Sawmill in available_building_types
        mask[1 + offset] = Recruiter in available_building_types
        mask[2 + offset] = Workshop in available_building_types
        return mask

    ### Eyrie Dynasty ###

    def eyrie_leader_mask(self, available_leaders: List[EyrieLeaders]):
        mask = [False] * self.action_size
        offset = 271
        mask[0 + offset] = EyrieLeaders.Despot in available_leaders
        mask[1 + offset] = EyrieLeaders.Commander in available_leaders
        mask[2 + offset] = EyrieLeaders.Charismatic in available_leaders
        mask[3 + offset] = EyrieLeaders.Builder in available_leaders
        return mask

    def decree_type_mask(self, allow_none=False):
        mask = [False] * self.action_size
        offset = 275
        mask[-1] = allow_none
        mask[0 + offset:4 + offset] = [True] * 4
        return mask

    ### Vagabond ###

    def vagabond_characters_mask(self):
        mask = [False] * self.action_size
        offset = 279
        mask[0 + offset:3 + offset] = [True] * 3
        return mask

    def forest_mask(self, available_forest: List[Forest]):
        mask = [False] * self.action_size
        offset = 282
        for forest in available_forest:
            mask[forest.index + offset] = True
        return mask

    def space_mask(self, available_spaces: List[Space]):
        mask = [False] * self.action_size
        CLEARING_OFFSET = 66
        FOREST_OFFSET = 282
        for space in available_spaces:
            if isinstance(space, Forest):
                mask[space.index + FOREST_OFFSET] = True
            else:
                mask[space.index + CLEARING_OFFSET] = True

        return mask

    def quest_mask(self, available_quests: List[QuestCard]):
        mask = [False] * self.action_size
        offset = 289
        quests = [RABBIT_ERRAND, FOX_ERRAND, MOUSE_ESCORT, RABBIT_EXPEL_BANDITS, MOUSE_EXPEL_BANDITS, RABBIT_FEND_BEAR, MOUSE_FEND_BEAR,
                  FUNDRAISING, RABBIT_SPEECH, FOX_SPEECH, RABBIT_GUARD_DUTY, MOUSE_GUARD_DUTY, FOX_LOGISTICS_HELP, MOUSE_LOGISTICS_HELP, REPAIR_A_SHED]
        for i, card in enumerate(quests):
            mask[i + offset] = card in available_quests
        return mask

    def aid_take_item_mask(self, available_items: List[Items]):
        mask = [False] * self.action_size
        offset = 304
        mask[-1] = True

        for i, item in enumerate(Items):
            mask[i + offset] = item in available_items

        return mask

    def item_mask(self, available_items: List[Items], exhausted_items: List[Items], damaged_items: List[Items], exhausted_damaged_items: List[Items]):
        mask = [False] * self.action_size
        all_items = [available_items, exhausted_items,
                     damaged_items, exhausted_damaged_items]

        idx = 0

        for item_list in all_items:
            for item in list(Items):
                mask[idx + 304] = item in item_list
                idx += 1

        return mask

    def strike_mask(self, chosen_faction: Faction, available_pieces: List[Piece], game_state: GameState):
        if game_state.vagabond.vagabond_pawn.space.get_faction_warrior_count(chosen_faction.faction_id) > 0:
            return self.warrior_mask(available_pieces)
        return self.piece_mask(available_pieces)

    def aid_exhaust_item_mask(self, available_items: List[Items], bag_track: int, coin_track: int, tea_track: int):
        mask = [False] * self.action_size

        offset = 304

        for i, item in enumerate(Items):
            mask[i + offset] = item in available_items

        mask[336] = tea_track > 0
        mask[337] = coin_track > 0
        mask[338] = bag_track > 0

        return mask

    def battle_damage_item(self, available_items: List[Items], exhausted_items: List[Items], bag_track: int, coin_track: int, tea_track: int):
        mask = [False] * self.action_size
        items_list = list(Items)

        available_offset = 304
        for i, item in enumerate(items_list):
            mask[i + available_offset] = item in available_items

        exhausted_offset = 312
        for i, item in enumerate(items_list):
            mask[exhausted_offset + i] = item in exhausted_items

        mask[336] = tea_track > 0
        mask[337] = coin_track > 0
        mask[338] = bag_track > 0
        return mask
