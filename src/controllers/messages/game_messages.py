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
    CRAFT_MESSAGE = auto()
    DISCARD_CHOICE_MESSAGE = auto()
    ACTION_CHOICE_MESSAGE = auto()
    CHOOSE_DOMINANCE_MESSAGE = auto()

    BATTLE_CLEARING_CHOICE_MESSAGE = auto()
    BATTLE_TARGET_CHOICE_MESSAGE = auto()

    # Marquise messages
    KEEP_CLEARING_MESSAGE = auto()
    MARCH_1_MESSAGE = auto()
    MARCH_2_MESSAGE = auto()
    OVERWORK_MESSAGE = auto()
    MARQUISE_BUILDING_MESSAGE = auto()
    WOOD_REMOVAL_MESSAGE = auto()
    MARQUISE_SETUP_BUILDINGS_MESSAGE = auto()
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


class GameMessage:
    def __init__(self, type) -> None:
        self.type = type

# region Factionless Messages


class AmbushMessage(GameMessage):
    def __init__(
        self, friendly_faction, enemy_faction, clearing, is_attacker, been_ambushed, available_ambush_cards
    ) -> None:
        super().__init__(GameMessages.AMBUSH_MESSAGE)
        self.friendly_faction = friendly_faction
        self.enemy_faction = enemy_faction
        self.clearing = clearing
        self.is_attacker = is_attacker
        self.been_ambushed = been_ambushed
        self.available_ambush_cards = available_ambush_cards

    def __repr__(self) -> str:
        return f"Ambush Message[\n    Friendly Faction: {str(self.friendly_faction)},\n    Enemy Faction: {str(self.enemy_faction)},\n    Clearing: {self.clearing.index},\n    Is Attacker: {self.is_attacker},\n    Been Ambushed: {self.been_ambushed},\n]"


class BattleUseCardMessage(GameMessage):
    def __init__(self, card_type):
        super().__init__(GameMessages.BATTLE_USE_CARD_MESSAGE)
        self.card_type = card_type


class BattleEndMessage(GameMessage):
    def __init__(self, friendly_faction, enemy_faction, clearing, is_attacker, battle_callbacks, attacker_roll, defender_roll) -> None:
        super().__init__(GameMessages.BATTLE_END_MESSAGE)
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
    def __init__(self, available_players):
        super().__init__(GameMessages.BETTER_BURROW_BANK_MESSAGE)
        self.available_players = available_players


class PieceTargetingMessage(GameMessage):
    def __init__(self, friendly_faction, enemy_faction, remaining_dmg, targets) -> None:
        super().__init__(GameMessages.PIECE_TARGETING_MESSAGE)
        self.friendly_faction = friendly_faction
        self.enemy_faction = enemy_faction
        self.remaining_dmg = remaining_dmg
        self.targets = targets


class ChooseDominanceMessage(GameMessage):
    def __init__(self, available_cards):
        super().__init__(GameMessages.CHOOSE_DOMINANCE_MESSAGE)
        self.available_cards = available_cards


class MoveMessage(GameMessage):
    def __init__(self, available_moves) -> None:
        super().__init__(GameMessages.MOVE_MESSAGE)
        self.available_moves = available_moves


class CraftMessage(GameMessage):
    def __init__(self, crafting_options) -> None:
        super().__init__(GameMessages.CRAFT_MESSAGE)
        self.crafting_options = crafting_options


class DiscardChoiceMessage(GameMessage):
    def __init__(self, discard_options, num_to_discard) -> None:
        super().__init__(GameMessages.DISCARD_CHOICE_MESSAGE)
        self.discard_options = discard_options
        self.num_to_discard = num_to_discard


class ActionChoiceMessage(GameMessage):
    def __init__(self, available_actions) -> None:
        super().__init__(GameMessages.ACTION_CHOICE_MESSAGE)
        self.available_actions = available_actions


class BattleClearingChoiceMessage(GameMessage):
    def __init__(self, available_clearings):
        super().__init__(GameMessages.BATTLE_CLEARING_CHOICE_MESSAGE)
        self.available_clearings = available_clearings


class BattleTargetChoiceMessage(GameMessage):
    def __init__(self, battle_target_list):
        super().__init__(GameMessages.BATTLE_TARGET_CHOICE_MESSAGE)
        self.battle_target_list = battle_target_list

# endregion

# region Marquise Messages


class KeepClearingMessage(GameMessage):
    def __init__(self, available_clearings):
        super().__init__(GameMessages.KEEP_CLEARING_MESSAGE)
        self.available_clearings = available_clearings


class March1Message(GameMessage):
    def __init__(self, available_moves) -> None:
        super().__init__(GameMessages.MARCH_1_MESSAGE)
        self.available_moves = available_moves


class March2Message(GameMessage):
    def __init__(self, available_moves) -> None:
        super().__init__(GameMessages.MARCH_2_MESSAGE)
        self.available_moves = available_moves


class OverworkMessage(GameMessage):
    def __init__(self, available_clearings, hand):
        super().__init__(GameMessages.OVERWORK_MESSAGE)
        self.available_clearings = available_clearings
        if not isinstance(self.available_clearings, list):
            self.available_clearings = [available_clearings]
        self.hand = hand


class MarquiseBuildingMessage(GameMessage):
    def __init__(self, clearing_building_options):
        super().__init__(GameMessages.MARQUISE_BUILDING_MESSAGE)
        self.clearing_building_options = clearing_building_options


class WoodRemovalMessage(GameMessage):
    def __init__(self, wood_list, cost):
        super().__init__(GameMessages.WOOD_REMOVAL_MESSAGE)
        self.wood_list = wood_list
        self.cost = cost


class MarquiseBuildingSetupMessage(GameMessage):
    def __init__(self, available_clearings):
        super().__init__(GameMessages.MARQUISE_SETUP_BUILDINGS_MESSAGE)
        self.available_clearings = available_clearings


class MarquiseSpendBirdCardMessage(GameMessage):
    def __init__(self, bird_cards):
        super().__init__(GameMessages.MARQUISE_SPEND_BIRD_CARD_MESSAGE)
        self.bird_cards = bird_cards


class FieldHospitalMessage(GameMessage):
    def __init__(self, available_cards):
        super().__init__(GameMessages.FIELD_HOSPITAL_MESSAGE)
        self.available_cards = available_cards

# endregion

# region Eyrie Dynasties Messages


class RoostlessMessage(GameMessage):
    def __init__(self, available_clearings):
        super().__init__(GameMessages.ROOSTLESS_MESSAGE)
        self.available_clearings = available_clearings


class RoostSetupMessage(GameMessage):
    def __init__(self, available_clearings):
        super().__init__(GameMessages.ROOST_SETUP_MESSAGE)
        self.available_clearings = available_clearings


class LeaderSetupMessage(GameMessage):
    def __init__(self, leader_choices):
        super().__init__(GameMessages.LEADER_SETUP_MESSAGE)
        self.leader_choices = leader_choices


class DecreeRecruitClearingMessage(GameMessage):
    def __init__(self, available_clearings):
        super().__init__(GameMessages.DECREE_RECRUIT_CLEARING_MESSAGE)
        self.available_clearings = available_clearings


class ExtendDecreeMessage1(GameMessage):
    def __init__(self, available_cards, decree_types):
        super().__init__(GameMessages.EXTEND_DECREE_MESSAGE_1)
        self.decree_types = decree_types
        self.available_cards = available_cards


class ExtendDecreeMessage2(GameMessage):
    def __init__(self, available_cards, decree_types):
        super().__init__(GameMessages.EXTEND_DECREE_MESSAGE_2)
        self.decree_types = decree_types
        self.available_cards = available_cards


class DecreeBuildMessage(GameMessage):
    def __init__(self, available_clearings):
        super().__init__(GameMessages.DECREE_BUILD_MESSAGE)
        self.available_clearings = available_clearings


class TurmoilLeaderMessage(GameMessage):
    def __init__(self, available_leaders):
        super().__init__(GameMessages.TURMOIL_LEADER_MESSAGE)
        self.available_leaders = available_leaders


# endregion

# region Woodland Alliance Messages

class AllianceNoBaseMessage(GameMessage):
    def __init__(self, supporters, num_to_discard):
        super().__init__(GameMessages.ALLIANCE_NO_BASE_MESSAGE)
        self.supporters = supporters
        self.num_to_discard = num_to_discard


class MobilizeMessage(GameMessage):
    def __init__(self, available_cards):
        super().__init__(GameMessages.MOBILIZE_MESSAGE)
        self.available_cards = available_cards


class TrainMessage(GameMessage):
    def __init__(self, available_cards):
        super().__init__(GameMessages.TRAIN_MESSAGE)
        self.available_cards = available_cards


class RevoltClearingMessage(GameMessage):
    def __init__(self, available_clearings):
        super().__init__(GameMessages.REVOLT_CLEARING_MESSAGE)
        self.available_clearings = available_clearings


class RevoltDiscardMessage(GameMessage):
    def __init__(self, valid_supporters):
        super().__init__(GameMessages.REVOLT_DISCARD_MESSAGE)
        self.valid_supporters = valid_supporters
        self.num_to_discard = 2


class SpreadSympathyClearingMessage(GameMessage):
    def __init__(self, available_clearings):
        super().__init__(GameMessages.SPREAD_SYMPATHY_CLEARING_MESSAGE)
        self.available_clearings = available_clearings


class SpreadSympathyDiscardMessage(GameMessage):
    def __init__(self, available_supporters, num_to_discard):
        super().__init__(GameMessages.SPREAD_SYMPATHY_DISCARD_MESSAGE)
        self.available_supporters = available_supporters
        self.num_to_discard = num_to_discard


class AllianceRecruitMessage(GameMessage):
    def __init__(self, available_clearings):
        super().__init__(GameMessages.ALLIANCE_RECRUIT_MESSAGE)
        self.available_clearings = available_clearings


class OrganizeMessage(GameMessage):
    def __init__(self, available_units):
        super().__init__(GameMessages.ORGANIZE_MESSAGE)
        self.available_units = available_units


class TriggererOutrageMessage(GameMessage):
    def __init__(self, valid_cards):
        super().__init__(GameMessages.TRIGGERER_OUTRAGE_MESSAGE)
        self.valid_cards = valid_cards


class AllianceOutrageMessage(GameMessage):
    def __init__(self, triggerer_hand):
        super().__init__(GameMessages.ALLIANCE_OUTRAGE_MESSAGE)
        self.triggerer_hand = triggerer_hand


# endregion

# region Vagabond Messages

class ChooseCharacterMessage(GameMessage):
    def __init__(self, available_characters):
        super().__init__(GameMessages.CHOOSE_CHARACTER_MESSAGE)
        self.available_characters = available_characters


class VagabondPlacementMessage(GameMessage):
    def __init__(self, available_forests):
        super().__init__(GameMessages.VAGABOND_PLACEMENT_MESSAGE)
        self.available_forests = available_forests


class RangerRepairMessage(GameMessage):
    def __init__(self, available_damaged, exhausted_damaged):
        super().__init__(GameMessages.RANGER_REPAIR_MESSAGE)
        self.available_damaged = available_damaged
        self.exhausted_damaged = exhausted_damaged


class TinkerCardMessage(GameMessage):
    def __init__(self, available_cards):
        super().__init__(GameMessages.TINKER_CARD_MESSAGE)
        self.available_cards = available_cards


class ThiefStealMessage(GameMessage):
    def __init__(self, available_players):
        super().__init__(GameMessages.THIEF_STEAL_MESSAGE)
        self.available_players = available_players


class SlipMessage(GameMessage):
    def __init__(self, available_spaces):
        super().__init__(GameMessages.SLIP_MESSAGE)
        self.available_spaces = available_spaces


class RefreshItemMessage(GameMessage):
    def __init__(self, damaged_items, undamaged_items, remaining_refreshes):
        super().__init__(GameMessages.REFRESH_ITEM_MESSAGE)
        self.damaged_items = damaged_items
        self.undamaged_items = undamaged_items
        self.remaining_refreshes = remaining_refreshes


class VagabondMoveMessage(GameMessage):
    def __init__(self, clearing_dict):
        super().__init__(GameMessages.VAGABOND_MOVE_MESSAGE)
        self.clearing_dict = clearing_dict


class ChooseQuestMessage(GameMessage):
    def __init__(self, available_quests):
        super().__init__(GameMessages.CHOOSE_QUEST_MESSAGE)
        self.available_quests = available_quests


class ChooseQuestRewardMessage(GameMessage):
    def __init__(self):
        super().__init__(GameMessages.CHOOSE_QUEST_REWARD_MESSAGE)


class RepairItemMessage(GameMessage):
    def __init__(self, available_damaged, exhausted_damaged):
        super().__init__(GameMessages.REPAIR_ITEM_MESSAGE)
        self.available_damaged = available_damaged
        self.exhausted_damaged = exhausted_damaged


class EmptySatchelMessage(GameMessage):
    def __init__(self, available_items, exhausted_items, available_damaged_items, exhausted_damaged_items):
        super().__init__(GameMessages.EMPTY_SATCHEL_MESSAGE)
        self.available_items = available_items
        self.exhausted_items = exhausted_items
        self.available_damaged_items = available_damaged_items
        self.exhausted_damaged_items = exhausted_damaged_items


class StrikeFactionChoiceMessage(GameMessage):
    def __init__(self, available_factions):
        super().__init__(GameMessages.STRIKE_FACTION_CHOICE_MESSAGE)
        self.available_factions = available_factions


class StrikePieceTargetingMessage(GameMessage):
    def __init__(self, available_pieces):
        super().__init__(GameMessages.STRIKE_PIECE_TARGETING_MESSAGE)
        self.available_pieces = available_pieces


class AidFactionChoiceMessage(GameMessage):
    def __init__(self, available_factions):
        super().__init__(GameMessages.AID_FACTION_CHOICE_MESSAGE)
        self.available_factions = available_factions


class AidCardChoiceMessage(GameMessage):
    def __init__(self, available_cards):
        super().__init__(GameMessages.AID_CARD_CHOICE_MESSAGE)
        self.available_cards = available_cards


class AidExhaustItemChoiceMessage(GameMessage):
    def __init__(self, available_items):
        super().__init__(GameMessages.AID_EXHAUST_ITEM_CHOICE_MESSAGE)
        self.available_items = available_items


class AidTakeItemChoiceMessage(GameMessage):
    def __init__(self, available_items):
        super().__init__(GameMessages.AID_TAKE_ITEM_CHOICE_MESSAGE)
        self.available_items = available_items


class BattleDamageItemMessage(GameMessage):
    def __init__(self, available_items, exhausted_items, active_bag_count, active_coint_count, active_tea_count):
        super().__init__(GameMessages.BATTLE_DAMAGE_ITEM_MESSAGE)
        self.available_items = available_items
        self.exhausted_items = exhausted_items
        self.active_bag_count = active_bag_count
        self.active_coint_count = active_coint_count
        self.active_tea_count = active_tea_count


# endregion
