from __future__ import annotations
from math import inf
from typing import TYPE_CHECKING, List, Dict
import numpy as np
from src.controllers.messages.game_messages import GameMessages
from src.utils.root_types import Factions, Suits, Items, EyrieLeaders, RECRUIT, MOVE, BUILD, BATTLE
from src.factions.vagabond.vagabond_characters import RangerCharacter, TinkerCharacter, ThiefCharacter, Characters
from src.actions.action_group_registry import ActionGroupRegistry, ActionIDs
from src.factions.vagabond.quests import *
from src.pieces.piece_with_id import PieceWithID
from src.cards.cards import *

# Enum .value is a Python-level property and the encoder runs on every decision
_MARQUISE_ID = Factions.MARQUISE_DE_CAT.value
_EYRIE_ID = Factions.EYRIE_DYNASTY.value
_ALLIANCE_ID = Factions.WOODLAND_ALLIANCE.value
_VAGABOND_ID = Factions.VAGABOND.value
_CRAFTABLE_ITEM_VALUES = [Items.TEA.value, Items.HAMMER.value, Items.SWORD.value,
                          Items.BOOTS.value, Items.COINS.value, Items.BAG.value, Items.CROSSBOW.value]
_MESSAGE_COUNT = len(GameMessages)


if TYPE_CHECKING:
    from src.actions.action_handler import ActionGroup
    from src.utils.game_state import GameState
    from src.factions.faction import Faction
    from src.board.clearing import Clearing
    from src.board.forest import Forest
    from src.cards.card import Card
    from src.controllers.nn_controllers.battle_data import BattleData
    # from src.pieces.factionless.buildings.ruin import Ruin


class ObservationSpace:

    @classmethod
    def encode_game_state(cls, game_state: GameState, message_type: GameMessages, action_group: ActionGroup):
        observation_space = [
            #### GENERAL ####
            # Active faction id (who is using this)
            game_state.current_player.faction_id / 4,
            game_state.turn_count / game_state.turn_limit,  # Current Turn Count
            game_state.current_phase.value / 3,  # Current Phase
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
            cls._encode_dominance(game_state.marquise.dominance),
            # Eyrie Dynasties Dominance Status
            cls._encode_dominance(game_state.eyrie_dynasties.dominance),
            # Woodland Alliance Dominance Status
            cls._encode_dominance(game_state.woodland_alliance.dominance),
            # Vagabond Coalition Status
            cls._encode_coalition(game_state.vagabond.dominance)
        ]

        # Marquise Crafted Items
        observation_space.extend(
            cls._encode_crafted_items(game_state.marquise.items))
        # Eyrie Dynasties Crafted Items
        observation_space.extend(cls._encode_crafted_items(
            game_state.eyrie_dynasties.items))
        # Woodland Alliance Crafted Items
        observation_space.extend(cls._encode_crafted_items(
            game_state.woodland_alliance.items))
        # Vagabond Crafted Items
        observation_space.extend(
            cls._encode_crafted_items(game_state.vagabond.items))

        #### HANDS #####

        # One hot encoded hand (54 cards)
        observation_space.extend(cls._encode_hand(
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
        observation_space.extend(cls._encode_active_cards(
            game_state.marquise.active_cards))
        observation_space.extend(cls._encode_active_cards(
            game_state.eyrie_dynasties.active_cards))
        observation_space.extend(cls._encode_active_cards(
            game_state.woodland_alliance.active_cards))
        observation_space.extend(cls._encode_active_cards(
            game_state.vagabond.active_cards))

        #### BOARD ####

        # For each clearing

        piece_counts = cls._count_pieces_by_space(game_state)
        for clearing in game_state.board.clearings:
            observation_space.extend(
                cls._encode_clearing(clearing, game_state, piece_counts))

        # For each Forest
        for forest in game_state.board.forests:
            observation_space.extend(cls._encode_forest(forest))

        #### MARQUISE SPECIFIC ####
        observation_space.extend(cls._encode_marquise_data(game_state))

        #### EYRIE DYNASTIES SPECIFIC ####
        observation_space.extend(cls._encode_eyrie_data(game_state))

        #### WOODLAND ALLIANCE SPECIFIC ####
        observation_space.extend(
            cls._encode_woodland_alliance_data(game_state, game_state.current_player.faction_id))

        #### VAGABOND SPECIFIC ####
        observation_space.extend(cls._encode_vagabond_data(game_state))

        #### GameMessage ####
        observation_space.extend(cls._encode_game_message(message_type))

        #### Battles ####
        observation_space.extend(cls._encode_battle(game_state))

        ### Selected Objects ####
        observation_space.extend(cls._encode_selected_faction(game_state))
        observation_space.extend(cls._encode_selected_clearing(game_state))
        observation_space.extend(cls._encode_to_clearing(game_state))
        observation_space.extend(cls._encode_selected_suit(game_state))

        #### Action Groups ####
        if action_group:
            # Action Group ID
            observation_space.append(
                0 if ActionGroupRegistry.get_registery_size() == 0 else action_group.id / ActionGroupRegistry.get_registery_size())
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
            observation_space.extend(
                cls._encode_action_list(action_group.actions))
        else:
            # Action Group ID
            observation_space.append(0.0)
            # Is action group ordered
            observation_space.append(0.0)
            # Can action space be aborted
            observation_space.append(0.0)
            # Max actions
            observation_space.append(0.0)
            # Remaining actions
            observation_space.append(0.0)
            observation_space.extend(
                cls._encode_action_list(None))
        return np.array(observation_space)

    @classmethod
    def _encode_dominance(cls, dominance: Suits) -> float:
        return 0.0 if dominance is None else dominance.value / 4

    @classmethod
    def _encode_coalition(cls, coalition_partner: Faction) -> float:
        return 0.0 if coalition_partner is None else coalition_partner.faction_id / 4

    @classmethod
    def _encode_crafted_items(cls, crafted_items: List[Items]) -> List[float]:
        crafted_values = [i.value for i in crafted_items]
        tea, hammer, sword, boots, coins, bag, crossbow = (
            crafted_values.count(value) for value in _CRAFTABLE_ITEM_VALUES)
        return [
            1.0 if tea >= 1 else 0.0,  # Tea-1
            1.0 if tea >= 2 else 0.0,  # Tea-2
            1.0 if tea == 3 else 0.0,  # Tea-3

            1.0 if hammer == 1 else 0.0,  # Hammer-1

            1.0 if sword >= 1 else 0.0,  # Sword-1
            1.0 if sword >= 2 else 0.0,  # Sword-2
            1.0 if sword == 3 else 0.0,  # Sword-3

            1.0 if boots >= 1 else 0.0,  # Boots-1
            1.0 if boots >= 2 else 0.0,  # Boots-2
            1.0 if boots >= 3 else 0.0,  # Boots-3
            1.0 if boots == 4 else 0.0,  # Boots-4

            1.0 if coins >= 1 else 0.0,  # Coins-1
            1.0 if coins >= 2 else 0.0,  # Coins-2
            1.0 if coins == 3 else 0.0,  # Coins-3

            1.0 if bag >= 1 else 0.0,  # Bag-1
            1.0 if bag >= 2 else 0.0,  # Bag-2
            1.0 if bag >= 3 else 0.0,  # Bag-3
            1.0 if bag == 4 else 0.0,  # Bag-4

            1.0 if crossbow >= 1 else 0.0,  # Crossbow-1
            1.0 if crossbow == 2 else 0.0,  # Crossbow-2
        ]

    @classmethod
    def _encode_hand(cls, hand: List[Card]) -> List[float]:
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

    @classmethod
    def _encode_active_cards(cls, active_cards: List[Card]) -> List[float]:
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

    @classmethod
    def _count_pieces_by_space(cls, game_state: GameState) -> Dict[str, Dict[Clearing, int]]:
        """Counts each piece type per space in one pass, instead of rescanning every piece per clearing"""
        def count(pieces):
            counts = {}
            for piece in pieces:
                counts[piece.space] = counts.get(piece.space, 0) + 1
            return counts

        marquise = game_state.marquise
        return {
            "wood": count(marquise.wood),
            "keep": count([marquise.keep] if marquise.keep else []),
            "recruiters": count(marquise.recruiters),
            "workshops": count(marquise.workshops),
            "sawmills": count(marquise.sawmills),
            "roosts": count(game_state.eyrie_dynasties.roosts),
            "sympathy": count(game_state.woodland_alliance.sympathy),
            "bases": count(base for base in game_state.woodland_alliance.bases.values() if base is not None),
        }

    @classmethod
    def _encode_clearing(cls, clearing: Clearing, game_state: GameState, piece_counts=None) -> List[float]:
        if piece_counts is None:
            piece_counts = cls._count_pieces_by_space(game_state)
        owner = clearing.get_owner()
        return [
            # Clearing faction ruler
            owner / 5 if owner else 1.0,
            # Clearing suit
            clearing.get_suit().value / 3,
            # Total clearing slots
            len(clearing.slots) / 3,
            # Available clearing slots
            sum(slot is None for slot in clearing.slots) / len(clearing.slots),
            # Marquise de cat warrior count (normalized via max faction warrior count)
            len(clearing.units[_MARQUISE_ID]) /
            game_state.marquise.max_warriors,
            # Eyrie Dynasties warrior count
            len(clearing.units[_EYRIE_ID]) /
            game_state.eyrie_dynasties.max_warriors,
            # Woodland Alliance warrior count
            len(clearing.units[_ALLIANCE_ID]) /
            game_state.woodland_alliance.max_warriors,
            # is vagabond pawn on this space?
            len(clearing.units[_VAGABOND_ID]),

            # MARQUISE
            # Wood one hot encoded
            piece_counts["wood"].get(clearing, 0) / game_state.marquise.max_wood,

            # has Keep?
            1.0 if clearing in piece_counts["keep"] else 0.0,

            # Recruiter count
            piece_counts["recruiters"].get(
                clearing, 0) / game_state.marquise.max_recruiters,

            # Workshop count
            piece_counts["workshops"].get(
                clearing, 0) / game_state.marquise.max_workshops,

            # Sawmill Count
            piece_counts["sawmills"].get(
                clearing, 0) / game_state.marquise.max_sawmills,

            # EYRIE DYNASTIES
            # has Roost?
            1.0 if clearing in piece_counts["roosts"] else 0.0,

            # WOODLAND ALLIANCE
            # has Sympathy
            1.0 if clearing in piece_counts["sympathy"] else 0.0,
            # has Base
            1.0 if clearing in piece_counts["bases"] else 0.0,

            # Vagabond
            # has Ruin
            1.0 if any(slot and slot.name == "Ruin"
                       for slot in clearing.slots) else 0.0
        ]

    @classmethod
    def _encode_forest(cls, forest: Forest) -> List[float]:
        return [
            # Is the vagabond pawn in this forest
            1.0 if forest.units[_VAGABOND_ID] else 0.0
        ]

    @classmethod
    def _encode_id_clearing(cls, piece_type: str, id: int, game_state: GameState) -> float:
        piece = PieceWithID.get_by_id(piece_type, id)
        return 0 if piece is None else (piece.space.index + 1) / len(game_state.board.clearings) + 1

    @classmethod
    def _encode_id_clearings(cls, piece_type: str, count: int, game_state: GameState) -> List[float]:
        """_encode_id_clearing for ids 0..count-1"""
        pieces = PieceWithID._instances.get(piece_type, {})
        clearing_count = len(game_state.board.clearings)
        encoded = []
        for i in range(count):
            piece = pieces.get(i, None)
            encoded.append(0 if piece is None else (
                piece.space.index + 1) / clearing_count + 1)
        return encoded

    @classmethod
    def _encode_marquise_data(cls, game_state: GameState) -> List[float]:
        marquise_data = [
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
            len(game_state.marquise.units) / game_state.marquise.max_warriors]

        # 8 Wood Token Clearings
        marquise_data.extend(cls._encode_id_clearings(
            "Wood Token", game_state.marquise.max_wood, game_state))

        # 6 Sawmills
        marquise_data.extend(cls._encode_id_clearings(
            "Sawmill", game_state.marquise.max_sawmills, game_state))

        # 6 Workshops
        marquise_data.extend(cls._encode_id_clearings(
            "Workshop", game_state.marquise.max_workshops, game_state))

        # 6 Recruiters
        marquise_data.extend(cls._encode_id_clearings(
            "Recruiter", game_state.marquise.max_recruiters, game_state))

        # 25 Warriors
        marquise_data.extend(cls._encode_id_clearings(
            "Marquise de Cat Pawn", game_state.marquise.max_warriors, game_state))

        return marquise_data

    @classmethod
    def _encode_eyrie_data(cls, game_state: GameState) -> List[float]:
        eyrie_data = [
            # number of roosts
            len(game_state.eyrie_dynasties.roosts) /
            game_state.eyrie_dynasties.max_roosts,

            # number of units
            len(game_state.eyrie_dynasties.units) /
            game_state.eyrie_dynasties.max_warriors,

            # Eyrie Leader ID
            game_state.eyrie_dynasties.eyrie_leader.value /
            4 if game_state.eyrie_dynasties.eyrie_leader else 0.0,

            # remaining leaders
            1.0 if EyrieLeaders.Despot in game_state.eyrie_dynasties.remaining_leaders else 0.0,
            1.0 if EyrieLeaders.Commander in game_state.eyrie_dynasties.remaining_leaders else 0.0,
            1.0 if EyrieLeaders.Charismatic in game_state.eyrie_dynasties.remaining_leaders else 0.0,
            1.0 if EyrieLeaders.Builder in game_state.eyrie_dynasties.remaining_leaders else 0.0,
        ]
        eyrie_data.extend(cls._encode_decree(game_state, RECRUIT))
        eyrie_data.extend(cls._encode_decree(game_state, MOVE))
        eyrie_data.extend(cls._encode_decree(game_state, BATTLE))
        eyrie_data.extend(cls._encode_decree(game_state, BUILD))

        # 7 Roosts
        eyrie_data.extend(cls._encode_id_clearings(
            "Roost", game_state.eyrie_dynasties.max_roosts, game_state))

        # 20 Warriors
        eyrie_data.extend(cls._encode_id_clearings(
            "Eyrie Dynasties Pawn", game_state.eyrie_dynasties.max_warriors, game_state))

        return eyrie_data

    @classmethod
    def _encode_decree(cls, game_state: GameState, decree_type: int) -> List[float]:
        decree_output = []
        for suit in Suits:
            decree_output.append(sum(
                # Normalized by 56 for 54 cards + 2 royal viziers
                1.0 for card in game_state.eyrie_dynasties.decree_cards[decree_type] if card.suit == suit) / 56.0)
        return decree_output

    @classmethod
    def _encode_woodland_alliance_data(cls, game_state: GameState, faction_id: int) -> List[float]:
        alliance_data = [
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
            0.0 if faction_id != _ALLIANCE_ID else (sum(
                1.0 for card in game_state.woodland_alliance.supporters if card.suit == Suits.FOX) / 54.0),
            0.0 if faction_id != _ALLIANCE_ID else (sum(
                1.0 for card in game_state.woodland_alliance.supporters if card.suit == Suits.RABBIT) / 54.0),
            0.0 if faction_id != _ALLIANCE_ID else (sum(
                1.0 for card in game_state.woodland_alliance.supporters if card.suit == Suits.MOUSE) / 54.0),
            0.0 if faction_id != _ALLIANCE_ID else (sum(
                1.0 for card in game_state.woodland_alliance.supporters if card.suit == Suits.BIRD) / 54.0),
        ]

        # 10 Sympathy
        alliance_data.extend(cls._encode_id_clearings(
            "Sympathy Token", game_state.woodland_alliance.max_sympathy, game_state))
        # The base encodings below reuse the last sympathy loop index, as before
        i = game_state.woodland_alliance.max_sympathy - 1

        alliance_data.append(
            cls._encode_id_clearing("Alliance Fox Base", i, game_state))
        alliance_data.append(
            cls._encode_id_clearing("Alliance Rabbit Base", i, game_state))
        alliance_data.append(
            cls._encode_id_clearing("Alliance Mouse Base", i, game_state))

        # 10 Warriors
        alliance_data.extend(cls._encode_id_clearings(
            "Woodland Alliance Pawn", game_state.woodland_alliance.max_warriors, game_state))

        return alliance_data

    @classmethod
    def _encode_vagabond_data(cls, game_state: GameState) -> List[float]:
        vagabond_data = [
            # Vagabond Character
            cls._encode_vagabond_character(game_state.vagabond.character),
            # Bag Track Count
            game_state.vagabond.active_bag_count / 3.0,
            # Tea Track Count
            game_state.vagabond.active_tea_count / 3.0,
            # Coin track count
            game_state.vagabond.active_coin_count / 3.0,
            # Marquise De Cat relatonship status
            game_state.vagabond.relationship_track.relationship_level[
                _MARQUISE_ID] / 4.0,
            # Eyrie Dynasties relationship status
            game_state.vagabond.relationship_track.relationship_level[
                _EYRIE_ID] / 4.0,
            # Woodland Alliance relationship status
            game_state.vagabond.relationship_track.relationship_level[
                _ALLIANCE_ID] / 4.0,
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
        vagabond_data.extend(cls._encode_satchel_list(
            game_state.vagabond.satchel.available_items))
        # One hot encoded exhausted satchel items
        vagabond_data.extend(cls._encode_satchel_list(
            game_state.vagabond.satchel.exhausted_items))
        # One hot encoded exhausted damaged satchel items
        vagabond_data.extend(cls._encode_satchel_list(
            game_state.vagabond.satchel.exhausted_damaged_items))
        # One hot encoded damaged satchel items
        vagabond_data.extend(cls._encode_satchel_list(
            game_state.vagabond.satchel.available_damaged_items))
        vagabond_data.extend([1.0 if game_state.vagabond.battle_ally and game_state.vagabond.battle_ally.faction_id == _MARQUISE_ID else 0,
                              1.0 if game_state.vagabond.battle_ally and game_state.vagabond.battle_ally.faction_id == _EYRIE_ID else 0,
                              1.0 if game_state.vagabond.battle_ally and game_state.vagabond.battle_ally.faction_id == _ALLIANCE_ID else 0,
                              1.0 if game_state.vagabond.battle_ally and game_state.vagabond.battle_ally.faction_id == _VAGABOND_ID else 0,])
        return vagabond_data

    @classmethod
    def _encode_satchel_list(cls, item_list: Dict[Items, int]) -> List[float]:
        boots = item_list[Items.BOOTS]
        sword = item_list[Items.SWORD]
        bag = item_list[Items.BAG]
        hammer = item_list[Items.HAMMER]
        tea = item_list[Items.TEA]
        coins = item_list[Items.COINS]
        crossbow = item_list[Items.CROSSBOW]
        torch = item_list[Items.TORCH]
        return [
            1.0 if boots >= 1 else 0.0,
            1.0 if boots >= 2 else 0.0,
            1.0 if boots >= 3 else 0.0,
            1.0 if boots == 4 else 0.0,

            1.0 if sword >= 1 else 0.0,
            1.0 if sword >= 2 else 0.0,
            1.0 if sword >= 3 else 0.0,
            1.0 if sword == 4 else 0.0,

            1.0 if bag >= 1 else 0.0,
            1.0 if bag >= 2 else 0.0,
            1.0 if bag >= 3 else 0.0,
            1.0 if bag == 4 else 0.0,

            1.0 if hammer >= 1 else 0.0,
            1.0 if hammer >= 2 else 0.0,
            1.0 if hammer == 3 else 0.0,

            1.0 if tea >= 1 else 0.0,
            1.0 if tea >= 2 else 0.0,
            1.0 if tea == 3 else 0.0,

            1.0 if coins >= 1 else 0.0,
            1.0 if coins >= 2 else 0.0,
            1.0 if coins == 3 else 0.0,

            1.0 if crossbow >= 1 else 0.0,
            1.0 if crossbow == 2 else 0.0,

            1.0 if torch == 1 else 0.0
        ]
        # 4 Boots
        # 4 Bags,
        # 4 Swords
        # 3 Hammers
        # 3 Tea, 3 Coins, 2 Crossbows, 1 Torch

    @classmethod
    def _encode_vagabond_character(cls, character: Characters) -> List[float]:
        if isinstance(character, ThiefCharacter):
            return 0.0
        elif isinstance(character, TinkerCharacter):
            return 0.5
        else:
            return 1.0

    @classmethod
    def _encode_game_message(cls, message_type: GameMessages):
        message_encoding = [0.0] * _MESSAGE_COUNT
        if message_type:
            value = message_type.value
            if isinstance(value, int) and 1 <= value <= _MESSAGE_COUNT:
                message_encoding[value - 1] = 1.0
        return message_encoding

    @classmethod
    def _encode_action_list(cls, action_list: List[Action]) -> List[float]:
        if action_list is None:
            return [0.0 for i in range(len(ActionIDs))]

        actions_id_list = [action.id for action in action_list]
        encoded_list = []
        for actionID in ActionIDs:
            encoded_list.append(1.0 if actionID in actions_id_list else 0.0)
        return encoded_list

    @classmethod
    def _encode_battle(cls, game_state: GameState):
        if game_state.battle_data is None:
            return [0.0] * 9
        return [
            game_state.battle_data.attacker.faction_id /
            len(game_state.faction_list),
            game_state.battle_data.defender.faction_id /
            len(game_state.faction_list),
            0.0 if game_state.battle_data.been_ambushed is None else (
                1.0 if game_state.battle_data.been_ambushed else 0.5),
            1.0 if game_state.battle_data.used_ambush else 0.5,
            game_state.battle_data.attacker_roll / 3,
            game_state.battle_data.defender_roll / 3,
            (game_state.battle_data.battle_clearing.index + 1) /
            (len(game_state.board.clearings) + 1),
            game_state.battle_data.attacker_damage_modifier,
            game_state.battle_data.defender_damage_modifier
        ]

    @classmethod
    def _encode_selected_clearing(cls, game_state: GameState):
        selected_list = []
        for clearing in game_state.board.clearings:
            selected_list.append(
                1.0 if clearing == game_state.selected_clearing else 0.0)
        return selected_list

    @classmethod
    def _encode_to_clearing(cls, game_state: GameState):
        to_list = []
        for clearing in game_state.board.clearings:
            to_list.append(
                1.0 if clearing == game_state.selected_to_clearing else 0.0)
        return to_list

    @classmethod
    def _encode_selected_suit(cls, game_state: GameState):
        return [1.0 if game_state.selected_suit == Suits.FOX else 0.0,
                1.0 if game_state.selected_suit == Suits.RABBIT else 0.0,
                1.0 if game_state.selected_suit == Suits.MOUSE else 0.0,
                1.0 if game_state.selected_suit == Suits.BIRD else 0.0,]

    @classmethod
    def _encode_selected_faction(cls, game_state: GameState):
        return [
            1.0 if game_state.selected_faction and game_state.selected_faction.faction_id == _MARQUISE_ID else 0,
            1.0 if game_state.selected_faction and game_state.selected_faction.faction_id == _EYRIE_ID else 0,
            1.0 if game_state.selected_faction and game_state.selected_faction.faction_id == _ALLIANCE_ID else 0,
            1.0 if game_state.selected_faction and game_state.selected_faction.faction_id == _VAGABOND_ID else 0,
        ]
