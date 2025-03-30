from enum import Enum, auto
from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from utils.callback_handler import GameAction


class GameMessages(Enum):
    AMBUSH_MESSAGE = auto()
    BATTLE_START_MESSAGE = auto()
    BATTLE_END_MESSAGE = auto()
    BATTLE_USE_CARD_MESSAGE = auto()
    PIECE_TARGETING_MESSAGE = auto()
    MOVE_MESSAGE = auto()
    MOVE_UNITS_MESSAGE = auto()
    CRAFT_MESSAGE = auto()
    DISCARD_CHOICE_MESSAGE = auto()
    ACTION_CHOICE_MESSAGE = auto()
    CHOOSE_DOMINANCE_MESSAGE = auto()
    STAND_AND_DELIVER_MESSAGE = auto()
    TAX_COLLECTOR_MESSAGE = auto()
    CODEBREAKERS_MESSAGE = auto()
    CLAIM_DOMINANCE_SUIT_MESSAGE = auto()
    CLAIM_DOMINANCE_CARD_MESSAGE = auto()

    BATTLE_CLEARING_CHOICE_MESSAGE = auto()
    BATTLE_TARGET_CHOICE_MESSAGE = auto()

    # Marquise messages
    KEEP_CLEARING_MESSAGE = auto()
    MARCH_1_MESSAGE = auto()
    MARCH_1_UNITS_MESSAGE = auto()
    MARCH_2_MESSAGE = auto()
    MARCH_2_CHOICE_MESSAGE = auto()
    MARCH_2_UNITS_MESSAGE = auto()
    OVERWORK_MESSAGE = auto()
    OVERWORK_DISCARD_MESSAGE = auto()
    MARQUISE_BUILDING_MESSAGE = auto()
    WOOD_REMOVAL_MESSAGE = auto()
    MARQUISE_SETUP_BUILDINGS_MESSAGE = auto()
    MARQUISE_SETUP_SAWMILL_MESSAGE = auto()
    MARQUISE_SETUP_WORKSHOP_MESSAGE = auto()
    MARQUISE_SETUP_RECRUITER_MESSAGE = auto()
    MARQUISE_BUILDING_TYPE_MESSAGE = auto()
    MARQUISE_SPEND_BIRD_CARD_MESSAGE = auto()
    FIELD_HOSPITAL_MESSAGE = auto()

    # Eyrie Dynasties Messages
    ROOSTLESS_MESSAGE = auto()
    ROOST_SETUP_MESSAGE = auto()
    LEADER_SETUP_MESSAGE = auto()
    DECREE_RECRUIT_CLEARING_MESSAGE = auto()
    EXTEND_DECREE_MESSAGE_1 = auto()
    EXTEND_DECREE_MESSAGE_2 = auto()
    DECREE_BUILD_MESSAGE = auto()
    TURMOIL_LEADER_MESSAGE = auto()

    # Woodland Alliance Messages
    ALLIANCE_NO_BASE_MESSAGE = auto()
    MOBILIZE_MESSAGE = auto()
    TRAIN_MESSAGE = auto()
    REVOLT_CLEARING_MESSAGE = auto()
    REVOLT_DISCARD_MESSAGE = auto()
    SPREAD_SYMPATHY_CLEARING_MESSAGE = auto()
    SPREAD_SYMPATHY_DISCARD_MESSAGE = auto()
    ALLIANCE_RECRUIT_MESSAGE = auto()
    ORGANIZE_MESSAGE = auto()
    BETTER_BURROW_BANK_MESSAGE = auto()
    TRIGGERER_OUTRAGE_MESSAGE = auto()
    ALLIANCE_OUTRAGE_MESSAGE = auto()

    # Vagabond Messages
    CHOOSE_CHARACTER_MESSAGE = auto()
    VAGABOND_PLACEMENT_MESSAGE = auto()
    RANGER_REPAIR_MESSAGE = auto()
    TINKER_CARD_MESSAGE = auto()
    THIEF_STEAL_MESSAGE = auto()
    SLIP_MESSAGE = auto()
    REFRESH_ITEM_MESSAGE = auto()
    VAGABOND_MOVE_MESSAGE = auto()
    CHOOSE_QUEST_MESSAGE = auto()
    QUEST_USE_ITEM_TRACK_MESSAGE = auto()
    CHOOSE_QUEST_REWARD_MESSAGE = auto()
    REPAIR_ITEM_MESSAGE = auto()
    EMPTY_SATCHEL_MESSAGE = auto()
    STRIKE_FACTION_CHOICE_MESSAGE = auto()
    STRIKE_PIECE_TARGETING_MESSAGE = auto()
    AID_FACTION_CHOICE_MESSAGE = auto()
    AID_CARD_CHOICE_MESSAGE = auto()
    AID_EXHAUST_ITEM_CHOICE_MESSAGE = auto()
    AID_TAKE_ITEM_CHOICE_MESSAGE = auto()
    BATTLE_DAMAGE_ITEM_MESSAGE = auto()
    COALITION_CHOICE_MESSAGE = auto()
    ALLY_MOVEMENT_MESSAGE = auto()
    CHOOSE_ALLY_MESSAGE = auto()
    ALLY_DAMAGE_SPLIT_MESSAGE = auto()


class GameMessage:
    def __init__(self, game_state, type, action_group) -> None:
        self.game_state = game_state
        self.type = type
        self.action_group = action_group

# region Factionless Messages


class AmbushMessage(GameMessage):
    def __init__(
        self, game_state, action_group, friendly_faction, enemy_faction, clearing, is_attacker, been_ambushed, available_ambush_cards
    ) -> None:
        super().__init__(game_state, GameMessages.AMBUSH_MESSAGE, action_group)
        self.friendly_faction = friendly_faction
        self.enemy_faction = enemy_faction
        self.clearing = clearing
        self.is_attacker = is_attacker
        self.been_ambushed = been_ambushed
        self.available_ambush_cards = available_ambush_cards

    def __repr__(self) -> str:
        return f"Ambush Message[\n    Friendly Faction: {str(self.friendly_faction)},\n    Enemy Faction: {str(self.enemy_faction)},\n    Clearing: {self.clearing.index},\n    Is Attacker: {self.is_attacker},\n    Been Ambushed: {self.been_ambushed},\n]"


class BattleUseCardMessage(GameMessage):
    def __init__(self, game_state, action_group, card_type):
        super().__init__(game_state, GameMessages.BATTLE_USE_CARD_MESSAGE, action_group)
        self.card_type = card_type


class BattleEndMessage(GameMessage):
    def __init__(self, game_state, action_group, friendly_faction, enemy_faction, clearing, is_attacker, battle_callbacks, attacker_roll, defender_roll) -> None:
        super().__init__(game_state, GameMessages.BATTLE_END_MESSAGE, action_group)
        self.friendly_faction = friendly_faction
        self.enemy_faction = enemy_faction
        self.clearing = clearing
        self.is_attacker = is_attacker
        self.battle_callbacks = battle_callbacks
        self.attacker_roll = attacker_roll
        self.defender_roll = defender_roll

    def __repr__(self) -> str:
        return f"Battle End Message[\n    Friendly Faction: {str(self.friendly_faction)},\n    Enemy Faction: {str(self.enemy_faction)},\n    Clearing: {self.clearing.index},\n    Is Attacker: {self.is_attacker},\n    Battle Callbacks: {self.battle_callbacks},\n    Attacker Dice Roll: {self.attacker_roll},\n    Defender Dice Roll: {self.defender_roll}\n]"


class BetterBurrowBankMessage(GameMessage):
    def __init__(self, game_state, action_group, available_players):
        super().__init__(game_state, GameMessages.BETTER_BURROW_BANK_MESSAGE, action_group)
        self.available_players = available_players


class ClaimDominanceSuitMessage(GameMessage):
    def __init__(self, game_state, action_group, available_dominance_cards):
        super().__init__(game_state, GameMessages.CLAIM_DOMINANCE_SUIT_MESSAGE, action_group)
        self.available_dominance_cards = available_dominance_cards


class ClaimDominanceCardMessage(GameMessage):
    def __init__(self, game_state, action_group, available_discard_cards):
        super().__init__(game_state, GameMessages.CLAIM_DOMINANCE_CARD_MESSAGE, action_group)
        self.available_discard_cards = available_discard_cards


class TaxCollectorMessage(GameMessage):
    def __init__(self, game_state, action_group, available_units):
        super().__init__(game_state, GameMessages.TAX_COLLECTOR_MESSAGE, action_group)
        self.available_units = available_units


class CodebreakersMessage(GameMessage):
    def __init__(self, game_state, action_group, available_players):
        super().__init__(game_state, GameMessages.CODEBREAKERS_MESSAGE, action_group)
        self.available_players = available_players


class PieceTargetingMessage(GameMessage):
    def __init__(self, game_state, action_group, friendly_faction, enemy_faction, targets) -> None:
        super().__init__(game_state, GameMessages.PIECE_TARGETING_MESSAGE, action_group)
        self.friendly_faction = friendly_faction
        self.enemy_faction = enemy_faction
        self.targets = targets


class ChooseDominanceMessage(GameMessage):
    def __init__(self, game_state, action_group, available_cards):
        super().__init__(game_state, GameMessages.CHOOSE_DOMINANCE_MESSAGE, action_group)
        self.available_cards = available_cards


class MoveMessage(GameMessage):
    def __init__(self, game_state, action_group, available_moves) -> None:
        super().__init__(game_state, GameMessages.MOVE_MESSAGE, action_group)
        self.available_moves = available_moves


class CraftMessage(GameMessage):
    def __init__(self, game_state, action_group, crafting_options) -> None:
        super().__init__(game_state, GameMessages.CRAFT_MESSAGE, action_group)
        self.crafting_options = crafting_options


class DiscardChoiceMessage(GameMessage):
    def __init__(self, game_state, action_group, discard_options) -> None:
        super().__init__(game_state, GameMessages.DISCARD_CHOICE_MESSAGE, action_group)
        self.discard_options = discard_options


class ActionChoiceMessage(GameMessage):
    def __init__(self, game_state, action_group, available_actions) -> None:
        super().__init__(game_state, GameMessages.ACTION_CHOICE_MESSAGE, action_group)
        self.available_actions = available_actions


class StandAndDeliverMessage(GameMessage):
    def __init__(self, game_state, action_group, available_players):
        super().__init__(game_state, GameMessages.STAND_AND_DELIVER_MESSAGE, action_group)
        self.available_players = available_players


class BattleClearingChoiceMessage(GameMessage):
    def __init__(self, game_state, action_group, available_clearings):
        super().__init__(game_state, GameMessages.BATTLE_CLEARING_CHOICE_MESSAGE, action_group)
        self.available_clearings = available_clearings


class BattleTargetChoiceMessage(GameMessage):
    def __init__(self, game_state, action_group, battle_target_list):
        super().__init__(game_state, GameMessages.BATTLE_TARGET_CHOICE_MESSAGE, action_group)
        self.battle_target_list = battle_target_list

# endregion

# region Marquise Messages


class KeepClearingMessage(GameMessage):
    def __init__(self, game_state, action_group, available_clearings):
        super().__init__(game_state, GameMessages.KEEP_CLEARING_MESSAGE, action_group)
        self.available_clearings = available_clearings


class March1Message(GameMessage):
    def __init__(self, game_state, action_group, available_moves) -> None:
        super().__init__(game_state, GameMessages.MARCH_1_MESSAGE, action_group)
        self.available_moves = available_moves


class March2Message(GameMessage):
    def __init__(self, game_state, action_group, available_moves) -> None:
        super().__init__(game_state, GameMessages.MARCH_2_MESSAGE, action_group)
        self.available_moves = available_moves


class OverworkMessage(GameMessage):
    def __init__(self, game_state, action_group, available_clearings, hand):
        super().__init__(game_state, GameMessages.OVERWORK_MESSAGE, action_group)
        self.available_clearings = available_clearings
        if not isinstance(self.available_clearings, list):
            self.available_clearings = [available_clearings]
        self.hand = hand


class MarquiseBuildingMessage(GameMessage):
    def __init__(self, game_state, action_group, clearing_building_options):
        super().__init__(game_state, GameMessages.MARQUISE_BUILDING_MESSAGE, action_group)
        self.clearing_building_options = clearing_building_options


class WoodRemovalMessage(GameMessage):
    def __init__(self, game_state, action_group, wood_list):
        super().__init__(game_state, GameMessages.WOOD_REMOVAL_MESSAGE, action_group)
        self.wood_list = wood_list


class MarquiseBuildingSetupMessage(GameMessage):
    def __init__(self, game_state, action_group, available_clearings):
        super().__init__(game_state, GameMessages.MARQUISE_SETUP_BUILDINGS_MESSAGE, action_group)
        self.available_clearings = available_clearings


class MarquiseSpendBirdCardMessage(GameMessage):
    def __init__(self, game_state, action_group, bird_cards):
        super().__init__(game_state, GameMessages.MARQUISE_SPEND_BIRD_CARD_MESSAGE, action_group)
        self.bird_cards = bird_cards


class FieldHospitalMessage(GameMessage):
    def __init__(self, game_state, action_group, available_cards):
        super().__init__(game_state, GameMessages.FIELD_HOSPITAL_MESSAGE, action_group)
        self.available_cards = available_cards

# endregion

# region Eyrie Dynasties Messages


class RoostlessMessage(GameMessage):
    def __init__(self, game_state, action_group, available_clearings):
        super().__init__(game_state, GameMessages.ROOSTLESS_MESSAGE, action_group)
        self.available_clearings = available_clearings


class RoostSetupMessage(GameMessage):
    def __init__(self, game_state, action_group, available_clearings):
        super().__init__(game_state, GameMessages.ROOST_SETUP_MESSAGE, action_group)
        self.available_clearings = available_clearings


class LeaderSetupMessage(GameMessage):
    def __init__(self, game_state, action_group, leader_choices):
        super().__init__(game_state, GameMessages.LEADER_SETUP_MESSAGE, action_group)
        self.leader_choices = leader_choices


class DecreeRecruitClearingMessage(GameMessage):
    def __init__(self, game_state, action_group, available_clearings):
        super().__init__(game_state, GameMessages.DECREE_RECRUIT_CLEARING_MESSAGE, action_group)
        self.available_clearings = available_clearings


class ExtendDecreeMessage1(GameMessage):
    def __init__(self, game_state, action_group, available_cards, decree_types):
        super().__init__(game_state, GameMessages.EXTEND_DECREE_MESSAGE_1, action_group)
        self.decree_types = decree_types
        self.available_cards = available_cards


class ExtendDecreeMessage2(GameMessage):
    def __init__(self, game_state, action_group, available_cards, decree_types):
        super().__init__(game_state, GameMessages.EXTEND_DECREE_MESSAGE_2, action_group)
        self.decree_types = decree_types
        self.available_cards = available_cards


class DecreeBuildMessage(GameMessage):
    def __init__(self, game_state, action_group, available_clearings):
        super().__init__(game_state, GameMessages.DECREE_BUILD_MESSAGE, action_group)
        self.available_clearings = available_clearings


class TurmoilLeaderMessage(GameMessage):
    def __init__(self, game_state, action_group, available_leaders):
        super().__init__(game_state, GameMessages.TURMOIL_LEADER_MESSAGE, action_group)
        self.available_leaders = available_leaders


# endregion

# region Woodland Alliance Messages

class AllianceNoBaseMessage(GameMessage):
    def __init__(self, game_state, action_group, supporters):
        super().__init__(game_state, GameMessages.ALLIANCE_NO_BASE_MESSAGE, action_group)
        self.supporters = supporters


class MobilizeMessage(GameMessage):
    def __init__(self, game_state, action_group, available_cards):
        super().__init__(game_state, GameMessages.MOBILIZE_MESSAGE, action_group)
        self.available_cards = available_cards


class TrainMessage(GameMessage):
    def __init__(self, game_state, action_group, available_cards):
        super().__init__(game_state, GameMessages.TRAIN_MESSAGE, action_group)
        self.available_cards = available_cards


class RevoltClearingMessage(GameMessage):
    def __init__(self, game_state, action_group, available_clearings):
        super().__init__(game_state, GameMessages.REVOLT_CLEARING_MESSAGE, action_group)
        self.available_clearings = available_clearings


class RevoltDiscardMessage(GameMessage):
    def __init__(self, game_state, action_group, valid_supporters):
        super().__init__(game_state, GameMessages.REVOLT_DISCARD_MESSAGE, action_group)
        self.valid_supporters = valid_supporters


class SpreadSympathyClearingMessage(GameMessage):
    def __init__(self, game_state, action_group, available_clearings):
        super().__init__(game_state, GameMessages.SPREAD_SYMPATHY_CLEARING_MESSAGE, action_group)
        self.available_clearings = available_clearings


class SpreadSympathyDiscardMessage(GameMessage):
    def __init__(self, game_state, action_group, available_supporters):
        super().__init__(game_state, GameMessages.SPREAD_SYMPATHY_DISCARD_MESSAGE, action_group)
        self.available_supporters = available_supporters


class AllianceRecruitMessage(GameMessage):
    def __init__(self, game_state, action_group, available_clearings):
        super().__init__(game_state, GameMessages.ALLIANCE_RECRUIT_MESSAGE, action_group)
        self.available_clearings = available_clearings


class OrganizeMessage(GameMessage):
    def __init__(self, game_state, action_group, available_units):
        super().__init__(game_state, GameMessages.ORGANIZE_MESSAGE, action_group)
        self.available_units = available_units


class TriggererOutrageMessage(GameMessage):
    def __init__(self, game_state, action_group, valid_cards):
        super().__init__(game_state, GameMessages.TRIGGERER_OUTRAGE_MESSAGE, action_group)
        self.valid_cards = valid_cards


class AllianceOutrageMessage(GameMessage):
    def __init__(self, game_state, action_group, triggerer_hand):
        super().__init__(game_state, GameMessages.ALLIANCE_OUTRAGE_MESSAGE, action_group)
        self.triggerer_hand = triggerer_hand


# endregion

# region Vagabond Messages

class ChooseCharacterMessage(GameMessage):
    def __init__(self, game_state, action_group, available_characters):
        super().__init__(game_state, GameMessages.CHOOSE_CHARACTER_MESSAGE, action_group)
        self.available_characters = available_characters


class VagabondPlacementMessage(GameMessage):
    def __init__(self, game_state, action_group, available_forests):
        super().__init__(game_state, GameMessages.VAGABOND_PLACEMENT_MESSAGE, action_group)
        self.available_forests = available_forests


class RangerRepairMessage(GameMessage):
    def __init__(self, game_state, action_group, available_damaged, exhausted_damaged):
        super().__init__(game_state, GameMessages.RANGER_REPAIR_MESSAGE, action_group)
        self.available_damaged = available_damaged
        self.exhausted_damaged = exhausted_damaged


class TinkerCardMessage(GameMessage):
    def __init__(self, game_state, action_group, available_cards):
        super().__init__(game_state, GameMessages.TINKER_CARD_MESSAGE, action_group)
        self.available_cards = available_cards


class ThiefStealMessage(GameMessage):
    def __init__(self, game_state, action_group, available_players):
        super().__init__(game_state, GameMessages.THIEF_STEAL_MESSAGE, action_group)
        self.available_players = available_players


class SlipMessage(GameMessage):
    def __init__(self, game_state, action_group, available_spaces):
        super().__init__(game_state, GameMessages.SLIP_MESSAGE, action_group)
        self.available_spaces = available_spaces


class RefreshItemMessage(GameMessage):
    def __init__(self, game_state, action_group, damaged_items, undamaged_items, remaining_refreshes):
        super().__init__(game_state, GameMessages.REFRESH_ITEM_MESSAGE, action_group)
        self.damaged_items = damaged_items
        self.undamaged_items = undamaged_items
        self.remaining_refreshes = remaining_refreshes


class VagabondMoveMessage(GameMessage):
    def __init__(self, game_state, action_group, clearing_dict):
        super().__init__(game_state, GameMessages.VAGABOND_MOVE_MESSAGE, action_group)
        self.clearing_dict = clearing_dict


class ChooseQuestMessage(GameMessage):
    def __init__(self, game_state, action_group, available_quests):
        super().__init__(game_state, GameMessages.CHOOSE_QUEST_MESSAGE, action_group)
        self.available_quests = available_quests


class ChooseQuestRewardMessage(GameMessage):
    def __init__(self, game_state, action_group):
        super().__init__(game_state, GameMessages.CHOOSE_QUEST_REWARD_MESSAGE, action_group)


class RepairItemMessage(GameMessage):
    def __init__(self, game_state, action_group, available_damaged, exhausted_damaged):
        super().__init__(game_state, GameMessages.REPAIR_ITEM_MESSAGE, action_group)
        self.available_damaged = available_damaged
        self.exhausted_damaged = exhausted_damaged


class EmptySatchelMessage(GameMessage):
    def __init__(self, game_state, action_group, available_items, exhausted_items, available_damaged_items, exhausted_damaged_items):
        super().__init__(game_state, GameMessages.EMPTY_SATCHEL_MESSAGE, action_group)
        self.available_items = available_items
        self.exhausted_items = exhausted_items
        self.available_damaged_items = available_damaged_items
        self.exhausted_damaged_items = exhausted_damaged_items


class StrikeFactionChoiceMessage(GameMessage):
    def __init__(self, game_state, action_group, available_factions):
        super().__init__(game_state, GameMessages.STRIKE_FACTION_CHOICE_MESSAGE, action_group)
        self.available_factions = available_factions


class StrikePieceTargetingMessage(GameMessage):
    def __init__(self, game_state, action_group, available_pieces):
        super().__init__(game_state, GameMessages.STRIKE_PIECE_TARGETING_MESSAGE, action_group)
        self.available_pieces = available_pieces


class AidFactionChoiceMessage(GameMessage):
    def __init__(self, game_state, action_group, available_factions):
        super().__init__(game_state, GameMessages.AID_FACTION_CHOICE_MESSAGE, action_group)
        self.available_factions = available_factions


class AidCardChoiceMessage(GameMessage):
    def __init__(self, game_state, action_group, available_cards):
        super().__init__(game_state, GameMessages.AID_CARD_CHOICE_MESSAGE, action_group)
        self.available_cards = available_cards


class AidExhaustItemChoiceMessage(GameMessage):
    def __init__(self, game_state, action_group, available_items, bag_track, coin_track, tea_track):
        super().__init__(game_state, GameMessages.AID_EXHAUST_ITEM_CHOICE_MESSAGE, action_group)
        self.available_items = available_items
        self.bag_track = bag_track
        self.coin_track = coin_track
        self.tea_track = tea_track


class AidTakeItemChoiceMessage(GameMessage):
    def __init__(self, game_state, action_group, available_items):
        super().__init__(game_state, GameMessages.AID_TAKE_ITEM_CHOICE_MESSAGE, action_group)
        self.available_items = available_items


class BattleDamageItemMessage(GameMessage):
    def __init__(self, game_state, action_group, available_items, exhausted_items, active_bag_count, active_coin_count, active_tea_count):
        super().__init__(game_state, GameMessages.BATTLE_DAMAGE_ITEM_MESSAGE, action_group)
        self.available_items = available_items
        self.exhausted_items = exhausted_items
        self.active_bag_count = active_bag_count
        self.active_coin_count = active_coin_count
        self.active_tea_count = active_tea_count


class CoalitionChoiceMessage(GameMessage):
    def __init__(self, game_state, action_group, available_factions):
        super().__init__(game_state, GameMessages.COALITION_CHOICE_MESSAGE, action_group)
        self.available_factions = available_factions


class AllyMovementMessage(GameMessage):
    def __init__(self, game_state, action_group, available_allies, from_clearing):
        super().__init__(game_state, GameMessages.ALLY_MOVEMENT_MESSAGE, action_group)
        self.available_allies = available_allies
        self.from_clearing = from_clearing


class ChooseAllyMessage(GameMessage):
    def __init__(self, game_state, action_group, available_allies):
        super().__init__(game_state, GameMessages.CHOOSE_ALLY_MESSAGE, action_group)
        self.available_allies = available_allies


class AllyDamageSplitMessage(GameMessage):
    def __init__(self, game_state, action_group, max_damage):
        super().__init__(game_state, GameMessages.ALLY_DAMAGE_SPLIT_MESSAGE, action_group)
        self.max_damage = max_damage


class QuestUseItemTrackMessage(GameMessage):
    def __init__(self, game_state, action_group, available_count, track_count):
        super().__init__(game_state, GameMessages.QUEST_USE_ITEM_TRACK_MESSAGE, action_group)
        self.available_count = available_count
        self.track_count = track_count

# endregion
