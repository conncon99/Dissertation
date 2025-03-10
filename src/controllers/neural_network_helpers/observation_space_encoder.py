from __future__ import annotations
from math import inf
from typing import TYPE_CHECKING, List, Dict
import numpy as np
from controllers.messages.game_messages import GameMessages, GameMessage
from utils.root_types import Factions, Suits, Items, EyrieLeaders, RECRUIT, MOVE, BUILD, BATTLE
from pieces.factionless.buildings.ruin import Ruin
from factions.vagabond.vagabond_characters import RangerCharacter, TinkerCharacter, ThiefCharacter, Characters
from actions.action_group_registry import ActionGroupRegistry, ActionIDs
from factions.vagabond.quests import *
from cards.cards import *


if TYPE_CHECKING:
    from actions.action_handler import ActionGroup
    from utils.game_state import GameState
    from factions.faction import Faction
    from board.clearing import Clearing
    from board.forest import Forest
    from cards.card import Card


class ObservationSpace:
    def __init__(self):
        pass

    def encode_game_state(self, game_state: GameState, message_type: GameMessages, action_group: ActionGroup):
        observation_space = [
            #### GENERAL ####
            # Active faction id (who is using this)
            game_state.current_player.faction_id / 4,
            game_state.turn_count / game_state.turn_limit,  # Current Turn Count
            game_state.current_player / 4,  # Current Player
            game_state.current_phase / 3,  # Current Phase
            # Marquise de Cat Turn order
            game_state.faction_list.index(
                game_state.marquise) / len(game_state.faction_list) - 1,
            # Eyrie Dynasties Turn order
            game_state.faction_list.index(
                game_state.eyrie_dynasties) / len(game_state.faction_list) - 1,
            # Woodland Alliance Turn order
            game_state.faction_list.index(
                game_state.woodland_alliance) / len(game_state.faction_list) - 1,
            # Vagabond Turn order
            game_state.faction_list.index(
                game_state.vagabond) / len(game_state.faction_list) - 1,

            game_state.marquise.victory_points / 30,  # Marquise Victory Points
            game_state.eyrie_dynasties.victory_points /
            30,  # Eyrie Dynasties Victory Points
            game_state.woodland_alliance.victory_points /
            30,  # Woodland Alliance Victory Points
            game_state.vagabond.victory_points / 30,  # Vagabond Victory Points

            # Marquise Dominance Status
            self._encode_dominance(game_state.marquise.dominance),
            # Eyrie Dynasties Dominance Status
            self._encode_dominance(game_state.eyrie_dynasties.dominance),
            # Woodland Alliance Dominance Status
            self._encode_dominance(game_state.woodland_alliance.dominance),
            # Vagabond Coalition Status
            self._encode_coalition(game_state.vagabond.dominance)
        ]

        # Marquise Crafted Items
        observation_space.extend(
            self._encode_crafted_items(game_state.marquise.items))
        # Eyrie Dynasties Crafted Items
        observation_space.extend(self._encode_crafted_items(
            game_state.eyrie_dynasties.items))
        # Woodland Alliance Crafted Items
        observation_space.extend(self._encode_crafted_items(
            game_state.woodland_alliance.items))
        # Vagabond Crafted Items
        observation_space.extend(
            self._encode_crafted_items(game_state.vagabond.items))

        #### HANDS #####

        # One hot encoded hand (54 cards)
        observation_space.extend(self.encode_hand(
            game_state.current_player.hand))

        # Marquise de Cat hand length
        observation_space.append(len(game_state.marquise.hand) / 54.0)

        # Eyrie Dynastied hand length
        observation_space.append(len(game_state.eyrie_dynasties.hand) / 54.0)

        # Woodland Alliance hand length
        observation_space.append(len(game_state.woodland_alliance.hand) / 54.0)

        # Vagabond hand length
        observation_space.append(len(game_state.vagabond.hand) / 54.0)

        # One hot encoded active cards for each faction
        observation_space.extend(self.encode_active_cards(
            game_state.marquise.active_cards))
        observation_space.extend(self.encode_active_cards(
            game_state.eyrie_dynasties.active_cards))
        observation_space.extend(self.encode_active_cards(
            game_state.woodland_alliance.active_cards))
        observation_space.extend(self.encode_active_cards(
            game_state.vagabond.active_cards))

        #### BOARD ####

        # For each clearing

        for clearing in game_state.board.clearings:
            observation_space.extend(
                self.encode_clearing(clearing, game_state))

        # For each Forest
        for forest in game_state.board.forests:
            observation_space.extend(self.encode_forest(forest))

        #### MARQUISE SPECIFIC ####
        observation_space.extend(self.encode_marquise_data(game_state))

        #### EYRIE DYNASTIES SPECIFIC ####
        observation_space.extend(self.encode_eyrie_data(game_state))

        #### WOODLAND ALLIANCE SPECIFIC ####
        observation_space.extend(
            self.encode_woodland_alliance_data(game_state, game_state.current_player.faction_id))

        #### VAGABOND SPECIFIC ####
        observation_space.extend(self.encode_vagabond_data(game_state))

        #### GameMessage ####
        observation_space.append(self.encode_game_message(message_type))

        #### Action Groups ####
        # Action Group ID
        observation_space.append(
            action_group.id / ActionGroupRegistry.get_registery_size())
        # Is action group ordered
        observation_space.append(1.0 if action_group.ordered else 0.0)
        # Can action space be aborted
        observation_space.append(1.0 if action_group.can_abort else 0.0)
        # Max actions
        observation_space.append(
            1.0 if action_group.max_total_uses == inf else action_group.max_total_uses / 15.0)
        # Remaining actions
        observation_space.append(1.0 if action_group.max_total_uses ==
                                 inf else action_group.total_uses / (action_group.max_total_uses + 1))
        # one hot encoded available actions - all 0 if not ActionChoiceMessage
        observation_space.extend(self.encode_action_list(action_group.actions))

        return np.array(observation_space)

    def _encode_dominance(self, dominance: Suits) -> float:
        return 0.0 if dominance is None else dominance.value / 4

    def _encode_coalition(self, coalition_partner: Faction) -> float:
        return 0.0 if coalition_partner is None else coalition_partner.faction_id / 4

    def _encode_crafted_items(self, crafted_items: List[Items]) -> List[float]:
        craftable_item_list = [Items.TEA, Items.HAMMER, Items.SWORD,
                               Items.BOOTS, Items.COINS, Items.BAG, Items.CROSSBOW]
        item_counts = {item: sum(
            1 for i in crafted_items if i.value == item.value) for item in craftable_item_list}
        return [
            1.0 if item_counts[Items.TEA] >= 1 else 0.0,  # Tea-1
            1.0 if item_counts[Items.TEA] >= 2 else 0.0,  # Tea-2
            1.0 if item_counts[Items.TEA] == 3 else 0.0,  # Tea-3

            1.0 if item_counts[Items.HAMMER] == 1 else 0.0,  # Hammer-1

            1.0 if item_counts[Items.SWORD] >= 1 else 0.0,  # Sword-1
            1.0 if item_counts[Items.SWORD] >= 2 else 0.0,  # Sword-2
            1.0 if item_counts[Items.SWORD] == 3 else 0.0,  # Sword-3

            1.0 if item_counts[Items.BOOTS] >= 1 else 0.0,  # Boots-1
            1.0 if item_counts[Items.BOOTS] >= 2 else 0.0,  # Boots-2
            1.0 if item_counts[Items.BOOTS] >= 3 else 0.0,  # Boots-3
            1.0 if item_counts[Items.BOOTS] == 4 else 0.0,  # Boots-4

            1.0 if item_counts[Items.COINS] >= 1 else 0.0,  # Coins-1
            1.0 if item_counts[Items.COINS] >= 2 else 0.0,  # Coins-2
            1.0 if item_counts[Items.COINS] == 3 else 0.0,  # Coins-3

            1.0 if item_counts[Items.BAG] >= 1 else 0.0,  # Bag-1
            1.0 if item_counts[Items.BAG] >= 2 else 0.0,  # Bag-2
            1.0 if item_counts[Items.BAG] >= 3 else 0.0,  # Bag-3
            1.0 if item_counts[Items.BAG] == 4 else 0.0,  # Bag-4

            1.0 if item_counts[Items.CROSSBOW] >= 1 else 0.0,  # Crossbow-1
            1.0 if item_counts[Items.CROSSBOW] == 2 else 0.0,  # Crossbow-2
        ]

    def encode_hand(self, hand: List[Card]) -> List[float]:
        return [
            1.0 if SWORD_MOUSE in hand else 0.0,
            1.0 if TRAVEL_GEAR_FOX in hand else 0.0,
            1.0 if TRAVEL_GEAR_MOUSE in hand else 0.0,
            1.0 if WOODLAND_RUNNERS in hand else 0.0,
            1.0 if ANVIL in hand else 0.0,
            1.0 if ARMS_TRADER in hand else 0.0,
            1.0 if A_VISIT_TO_FRIENDS in hand else 0.0,
            1.0 if BAKE_SALE in hand else 0.0,
            1.0 if BIRDY_BUNDLE in hand else 0.0,
            1.0 if CROSSBOW_BIRD in hand else 0.0,
            1.0 if CROSSBOW_MOUSE in hand else 0.0,
            1.0 if FOXFOLK_STEEL in hand else 0.0,
            1.0 if GENTLY_USED_KNAPSACK in hand else 0.0,
            1.0 if INVESTMENTS in hand else 0.0,
            1.0 if MOUSE_IN_A_SACK in hand else 0.0,
            1.0 if PROTECTION_RACKET in hand else 0.0,
            1.0 if ROOT_TEA_RABBIT in hand else 0.0,
            1.0 if ROOT_TEA_FOX in hand else 0.0,
            1.0 if ROOT_TEA_MOUSE in hand else 0.0,
            1.0 if SMUGGLERS_TRAIL in hand else 0.0,
            # Ambush Cards
            1.0 if BIRD_AMBUSH in hand else 0.0,
            1.0 if BIRD_AMBUSH_2 in hand else 0.0,
            1.0 if FOX_AMBUSH in hand else 0.0,
            1.0 if MOUSE_AMBUSH in hand else 0.0,
            1.0 if RABBIT_AMBUSH in hand else 0.0,
            # Dominance Cards
            1.0 if FOX_DOMINANCE in hand else 0.0,
            1.0 if MOUSE_DOMINANCE in hand else 0.0,
            1.0 if RABBIT_DOMINANCE in hand else 0.0,
            1.0 if BIRD_DOMINANCE in hand else 0.0,
            # Favour Cards
            1.0 if FAVOR_OF_THE_RABBITS in hand else 0.0,
            1.0 if FAVOR_OF_THE_FOXES in hand else 0.0,
            1.0 if FAVOR_OF_THE_MICE in hand else 0.0,
            # Misc Cards
            1.0 if SCOUTING_PARTY in hand else 0.0,
            1.0 if SCOUTING_PARTY_2 in hand else 0.0,
            1.0 if COMMAND_WARREN in hand else 0.0,
            1.0 if COMMAND_WARREN_2 in hand else 0.0,
            1.0 if COBBLER in hand else 0.0,
            1.0 if COBBLER_2 in hand else 0.0,
            1.0 if SAPPERS in hand else 0.0,
            1.0 if SAPPERS_2 in hand else 0.0,
            1.0 if BRUTAL_TACTICS in hand else 0.0,
            1.0 if BRUTAL_TACTICS_2 in hand else 0.0,
            1.0 if ARMORERS in hand else 0.0,
            1.0 if ARMORERS_2 in hand else 0.0,
            1.0 if BETTER_BURROW_BANK in hand else 0.0,
            1.0 if BETTER_BURROW_BANK_2 in hand else 0.0,
            1.0 if STAND_AND_DELIVER in hand else 0.0,
            1.0 if STAND_AND_DELIVER_2 in hand else 0.0,
            1.0 if TAX_COLLECTOR in hand else 0.0,
            1.0 if TAX_COLLECTOR_2 in hand else 0.0,
            1.0 if TAX_COLLECTOR_3 in hand else 0.0,
            1.0 if CODEBREAKERS in hand else 0.0,
            1.0 if CODEBREAKERS_2 in hand else 0.0,
            1.0 if ROYAL_CLAIM in hand else 0.0
        ]

    def encode_active_cards(self, active_cards: List[Card]) -> List[float]:
        return [
            1.0 if STAND_AND_DELIVER in active_cards else 0.0,
            1.0 if STAND_AND_DELIVER_2 in active_cards else 0.0,
            1.0 if TAX_COLLECTOR in active_cards else 0.0,
            1.0 if TAX_COLLECTOR_2 in active_cards else 0.0,
            1.0 if TAX_COLLECTOR_3 in active_cards else 0.0,
            1.0 if ARMORERS in active_cards else 0.0,
            1.0 if ARMORERS_2 in active_cards else 0.0,
            1.0 if BETTER_BURROW_BANK in active_cards else 0.0,
            1.0 if BETTER_BURROW_BANK_2 in active_cards else 0.0,
            1.0 if BRUTAL_TACTICS in active_cards else 0.0,
            1.0 if BRUTAL_TACTICS_2 in active_cards else 0.0,
            1.0 if COBBLER in active_cards else 0.0,
            1.0 if COBBLER_2 in active_cards else 0.0,
            1.0 if CODEBREAKERS in active_cards else 0.0,
            1.0 if CODEBREAKERS_2 in active_cards else 0.0,
            1.0 if COMMAND_WARREN in active_cards else 0.0,
            1.0 if COMMAND_WARREN_2 in active_cards else 0.0,
            1.0 if ROYAL_CLAIM in active_cards else 0.0,
            1.0 if SAPPERS in active_cards else 0.0,
            1.0 if SAPPERS_2 in active_cards else 0.0,
            1.0 if SCOUTING_PARTY in active_cards else 0.0,
            1.0 if SCOUTING_PARTY_2 in active_cards else 0.0
        ]

    def encode_clearing(self, clearing: Clearing, game_state: GameState) -> List[float]:
        return [
            # Clearing faction ruler
            clearing.get_owner() / 4,
            # Clearing suit
            clearing.get_suit() / 3,
            # Total clearing slots
            len(clearing.slots) / 3,
            # Available clearing slots
            sum(slot is None for slot in clearing.slots) / len(clearing.slots),
            # Marquise de cat warrior count (normalized via max faction warrior count)
            clearing.units[Factions.MARQUISE_DE_CAT.value] /
            game_state.marquise.max_warriors,
            # Eyrie Dynasties warrior count
            clearing.units[Factions.EYRIE_DYNASTY.value] /
            game_state.eyrie_dynasties.max_warriors,
            # Woodland Alliance warrior count
            clearing.units[Factions.WOODLAND_ALLIANCE.value] /
            game_state.woodland_alliance.max_warriors,
            # is vagabond pawn on this space?
            clearing.units[Factions.VAGABOND.value],

            # MARQUISE
            # Wood Count
            sum(1 for wood in game_state.marquise.wood if wood.space ==
                clearing) / game_state.marquise.max_wood,
            # has Keep?
            1.0 if game_state.marquise.keep.space == clearing else 0,

            # Recruiter count
            sum(1 for recruiter in game_state.marquise.recruiters if recruiter.space ==
                clearing) / game_state.marquise.max_recruiters,

            # Workshop count
            sum(1 for workshop in game_state.marquise.workshops if workshop.space ==
                clearing) / game_state.marquise.max_workshops,

            # Sawmill Count
            sum(1 for sawmill in game_state.marquise.sawmills if sawmill.space ==
                clearing) / game_state.marquise.max_sawmills,

            # EYRIE DYNASTIES
            # has Roost?
            1.0 if any(
                roost.space == clearing for roost in game_state.eyrie_dynasties.roosts) else 0.0,

            # WOODLAND ALLIANCE
            # has Sympathy
            1.0 if any(
                sympathy.space == clearing for sympathy in game_state.woodland_alliance.sympathy) else 0.0,
            # has Base
            1.0 if any(base is not None and base.space ==
                       clearing for base in game_state.woodland_alliance.bases.values()) else 0.0,

            # Vagabond
            # has Ruin
            1.0 if any(isinstance(slot, Ruin)
                       for slot in clearing.slots) else 0.0
        ]

    def encode_forest(self, forest: Forest) -> List[float]:
        return [
            # Is the vagabond pawn in this forest
            forest.units[Factions.VAGABOND.value]
        ]

    def encode_marquise_data(self, game_state: GameState) -> List[float]:
        return [
            # number of sawmills
            len(game_state.marquise.sawmills) /
            game_state.marquise.max_sawmills,
            # number of recruiters
            len(game_state.marquise.recruiters) /
            game_state.marquise.max_recruiters,
            # number of workshops
            len(game_state.marquise.workshops) /
            game_state.marquise.max_recruiters,
            # number of wood tokens
            len(game_state.marquise.wood) / game_state.marquise.max_wood,
            # number of units
            len(game_state.marquise.units) / game_state.marquise.max_warriors
        ]

    def encode_eyrie_data(self, game_state: GameState) -> List[float]:
        eyrie_data = [
            # number of roosts
            len(game_state.eyrie_dynasties.roosts) /
            game_state.eyrie_dynasties.max_roosts,

            # number of units
            len(game_state.eyrie_dynasties.units) /
            game_state.eyrie_dynasties.max_warriors,

            # Eyrie Leader ID
            game_state.eyrie_dynasties.eyrie_leader.value / 3,

            # remaining leaders
            1.0 if EyrieLeaders.Despot in game_state.eyrie_dynasties.remaining_leaders else 0.0,
            1.0 if EyrieLeaders.Commander in game_state.eyrie_dynasties.remaining_leaders else 0.0,
            1.0 if EyrieLeaders.Charismatic in game_state.eyrie_dynasties.remaining_leaders else 0.0,
            1.0 if EyrieLeaders.Builder in game_state.eyrie_dynasties.remaining_leaders else 0.0,
        ]
        eyrie_data.extend(self._encode_decree(game_state, RECRUIT))
        eyrie_data.extend(self._encode_decree(game_state, MOVE))
        eyrie_data.extend(self._encode_decree(game_state, BATTLE))
        eyrie_data.extend(self._encode_decree(game_state, BUILD))
        return eyrie_data

    def _encode_decree(self, game_state: GameState, decree_type: int) -> List[float]:
        decree_output = []
        for suit in Suits:
            decree_output.append(sum(
                1.0 for card in game_state.eyrie_dynasties.decree_cards[decree_type] if card.suit == suit) / 56.0)  # Normalized by 56 for 54 cards + 2 royal viziers
        return decree_output

    def encode_woodland_alliance_data(self, game_state: GameState, faction_id: int) -> List[float]:
        return [
            # Number of bases
            game_state.woodland_alliance.get_base_count() / 3.0,
            # Number of supporters
            len(game_state.woodland_alliance.supporters) / 54.0,
            # Number of sympathy tokens
            len(game_state.woodland_alliance.sympathy) /
            game_state.woodland_alliance.max_sympathy,
            # Number of officers
            game_state.woodland_alliance.officers /
            game_state.woodland_alliance.max_warriors,
            # Number of warriors
            len(game_state.woodland_alliance.units) /
            game_state.woodland_alliance.max_warriors,
            # Makeup of supporters - private info for WA only
            0.0 if faction_id != Factions.WOODLAND_ALLIANCE.value else (sum(
                1.0 for card in game_state.woodland_alliance.supporters if card.suit == Suits.FOX) / 54.0),
            0.0 if faction_id != Factions.WOODLAND_ALLIANCE.value else (sum(
                1.0 for card in game_state.woodland_alliance.supporters if card.suit == Suits.RABBIT) / 54.0),
            0.0 if faction_id != Factions.WOODLAND_ALLIANCE.value else (sum(
                1.0 for card in game_state.woodland_alliance.supporters if card.suit == Suits.MOUSE) / 54.0),
            0.0 if faction_id != Factions.WOODLAND_ALLIANCE.value else (sum(
                1.0 for card in game_state.woodland_alliance.supporters if card.suit == Suits.BIRD) / 54.0),
        ]

    def encode_vagabond_data(self, game_state: GameState) -> List[float]:
        vagabond_data = [
            # Vagabond Character
            self._encode_vagabond_character(game_state.vagabond.character),
            # Bag Track Count
            game_state.vagabond.active_bag_count / 3.0,
            # Tea Track Count
            game_state.vagabond.active_tea_count / 3.0,
            # Coin track count
            game_state.vagabond.active_coin_count / 3.0,
            # Marquise De Cat relatonship status
            game_state.vagabond.relationship_track[Factions.MARQUISE_DE_CAT.value] / 4.0,
            # Eyrie Dynasties relationship status
            game_state.vagabond.relationship_track[Factions.EYRIE_DYNASTY.value] / 4.0,
            # Woodland Alliance relationship status
            game_state.vagabond.relationship_track[Factions.WOODLAND_ALLIANCE.value] / 4.0,
            # Completed Fox Quests number
            game_state.vagabond.completed_quests[Suits.FOX] / 5.0,
            # Completed Rabbit Quests number
            game_state.vagabond.completed_quests[Suits.RABBIT] / 5.0,
            # Completed Mouse quests number
            game_state.vagabond.completed_quests[Suits.MOUSE] / 5.0,
            # One hot encoded quests in hand
            1.0 if RABBIT_ERRAND in game_state.vagabond.quest_cards else 0.0,
            1.0 if RABBIT_EXPEL_BANDITS in game_state.vagabond.quest_cards else 0.0,
            1.0 if RABBIT_FEND_BEAR in game_state.vagabond.quest_cards else 0.0,
            1.0 if RABBIT_GUARD_DUTY in game_state.vagabond.quest_cards else 0.0,
            1.0 if RABBIT_SPEECH in game_state.vagabond.quest_cards else 0.0,

            1.0 if MOUSE_ESCORT in game_state.vagabond.quest_cards else 0.0,
            1.0 if MOUSE_EXPEL_BANDITS in game_state.vagabond.quest_cards else 0.0,
            1.0 if MOUSE_FEND_BEAR in game_state.vagabond.quest_cards else 0.0,
            1.0 if MOUSE_GUARD_DUTY in game_state.vagabond.quest_cards else 0.0,
            1.0 if MOUSE_LOGISTICS_HELP in game_state.vagabond.quest_cards else 0.0,

            1.0 if FOX_ERRAND in game_state.vagabond.quest_cards else 0.0,
            1.0 if FOX_LOGISTICS_HELP in game_state.vagabond.quest_cards else 0.0,
            1.0 if FOX_SPEECH in game_state.vagabond.quest_cards else 0.0,
            1.0 if FUNDRAISING in game_state.vagabond.quest_cards else 0.0,
            1.0 if REPAIR_A_SHED in game_state.vagabond.quest_cards else 0.0,
        ]
        # One hot encoded available satchel items
        vagabond_data.extend(self._encode_satchel_list(
            game_state.vagabond.satchel.available_items))
        # One hot encoded exhausted satchel items
        vagabond_data.extend(self._encode_satchel_list(
            game_state.vagabond.satchel.exhausted_items))
        # One hot encoded exhausted damaged satchel items
        vagabond_data.extend(self._encode_satchel_list(
            game_state.vagabond.satchel.exhausted_damaged_items))
        # One hot encoded damaged satchel items
        vagabond_data.extend(self._encode_satchel_list(
            game_state.vagabond.satchel.available_damaged_items))
        return vagabond_data

    def _encode_satchel_list(item_list: Dict[Items, int]) -> List[float]:
        return [
            1.0 if item_list[Items.BOOTS] >= 1 else 0.0,
            1.0 if item_list[Items.BOOTS] >= 2 else 0.0,
            1.0 if item_list[Items.BOOTS] >= 3 else 0.0,
            1.0 if item_list[Items.BOOTS] == 4 else 0.0,

            1.0 if item_list[Items.SWORD] >= 1 else 0.0,
            1.0 if item_list[Items.SWORD] >= 2 else 0.0,
            1.0 if item_list[Items.SWORD] >= 3 else 0.0,
            1.0 if item_list[Items.SWORD] == 4 else 0.0,

            1.0 if item_list[Items.BAG] >= 1 else 0.0,
            1.0 if item_list[Items.BAG] >= 2 else 0.0,
            1.0 if item_list[Items.BAG] >= 3 else 0.0,
            1.0 if item_list[Items.BAG] == 4 else 0.0,

            1.0 if item_list[Items.HAMMER] >= 1 else 0.0,
            1.0 if item_list[Items.HAMMER] >= 2 else 0.0,
            1.0 if item_list[Items.HAMMER] == 3 else 0.0,

            1.0 if item_list[Items.TEA] >= 1 else 0.0,
            1.0 if item_list[Items.TEA] >= 2 else 0.0,
            1.0 if item_list[Items.TEA] == 3 else 0.0,

            1.0 if item_list[Items.COINS] >= 1 else 0.0,
            1.0 if item_list[Items.COINS] >= 2 else 0.0,
            1.0 if item_list[Items.COINS] == 3 else 0.0,

            1.0 if item_list[Items.CROSSBOW] >= 1 else 0.0,
            1.0 if item_list[Items.CROSSBOW] == 2 else 0.0,

            1.0 if item_list[Items.TORCH] == 1 else 0.0
        ]
        # 4 Boots
        # 4 Bags,
        # 4 Swords
        # 3 Hammers
        # 3 Tea, 3 Coins, 2 Crossbows, 1 Torch

    def _encode_vagabond_character(self, character: Characters) -> List[float]:
        if isinstance(character, ThiefCharacter):
            return 0.0
        elif isinstance(character, TinkerCharacter):
            return 0.5
        else:
            return 1.0

    def encode_game_message(message_type: GameMessages):
        return message_type.value / len(GameMessages)

    def encode_action_list(action_list: List[Action]) -> List[float]:
        actions_id_list = [action.id for action in action_list]
        encoded_list = []
        for actionID in ActionIDs:
            encoded_list.append(1.0 if actionID in actions_id_list else 0.0)
        return encoded_list
