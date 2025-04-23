from __future__ import annotations
from src.cards.cards import *
from src.pieces.marquise_de_cat.marquise_buildings import Recruiter, Sawmill, Workshop
from src.utils.root_types import EyrieLeaders, BUILD, BATTLE, RECRUIT, MOVE
from src.actions.action_handler import ActionGroup
from src.pieces.piece_with_id import PieceWithID
from src.factions.vagabond.vagabond_characters import Characters
from src.factions.vagabond.quests import *
import logging

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.utils.game_state import GameState


logger = logging.getLogger()


def decode_binary_choice(output):
    return output == 0


def decode_numerical_selection(output):
    return output


def decode_action_output(output, action_size, action_group: ActionGroup):
    actions = [None] * action_size
    for action in action_group.actions:
        if action is not None:
            # NOTE: If multiple actions have the same ID this won't work - such as the Decree Recruits
            actions[action.id.value - 1] = action
    return actions[output]


def decode_card_output(output):
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

    if output == 59:
        logger.debug("Returning None")
        return None

    logger.debug(cards[output])
    return cards[output]


def decode_faction_output(output, game_state: GameState):
    factions = [
        game_state.marquise,
        game_state.eyrie_dynasties,
        game_state.woodland_alliance,
        game_state.vagabond
    ]
    if output == 59:
        return None
    return factions[output]


def decode_clearing_output(output, game_state: GameState):
    return game_state.board.clearings[output]


def decode_piece_output(output, game_state: GameState):

    pieces = []
    # 7 Roosts
    for i in range(7):
        pieces.append(PieceWithID.get_by_id("Roost", i))

    # 6 Sawmills
    for i in range(6):
        pieces.append(PieceWithID.get_by_id("Sawmill", i))

    # 6 Workshops
    for i in range(6):
        pieces.append(PieceWithID.get_by_id("Workshop", i))

    # 6 Recruiters
    for i in range(6):
        pieces.append(PieceWithID.get_by_id("Recruiter", i))

    # 8 Wood
    for i in range(8):
        pieces.append(PieceWithID.get_by_id("Wood Token", i)
                      )
    # 1 Keep
    pieces.append(PieceWithID.get_by_id("Keep Token", 0))

    # 3 Alliance Bases
    pieces.append(PieceWithID.get_by_id("Alliance Fox Base", 0))
    pieces.append(PieceWithID.get_by_id("Alliance Rabbit Base", 0))
    pieces.append(PieceWithID.get_by_id("Alliance Mouse Base", 0))

    # 10 Sympathy
    for i in range(10):
        pieces.append(PieceWithID.get_by_id("Sympathy Token", i))
    assert pieces[output] is not None
    return pieces[output]


def decode_warrior_output(output):
    warriors = []

    for i in range(25):
        warriors.append(PieceWithID.get_by_id("Marquise de Cat Pawn", i))

    for i in range(20):
        warriors.append(PieceWithID.get_by_id(
            "Eyrie Dynasties Pawn", i))

    for i in range(10):
        warriors.append(PieceWithID.get_by_id(
            "Woodland Alliance Pawn", i))

    warriors.append(PieceWithID.get_by_id("Vagabond Pawn", 0))

    assert warriors[output]
    return warriors[output]


# Marquise

# Building Types

def decode_marquise_building_types(output):
    building_types = [Sawmill, Recruiter, Workshop]
    return building_types[output]


def decode_wood_output(output, game_state: GameState):
    return [wood for wood in game_state.marquise.wood if wood.id == output][0]

# Eyrie Dynasty


def decode_leader_output(output):
    leader_mapping = {0: EyrieLeaders.Despot, 1: EyrieLeaders.Commander,
                      2: EyrieLeaders.Charismatic, 3: EyrieLeaders.Builder}
    return leader_mapping[output]


def decode_decree_type_output(output):
    decree_type_mapping = {0: RECRUIT, 1: MOVE, 2: BATTLE, 3: BUILD, 59: None}
    return decree_type_mapping[output]

# Vagabond


def decode_character_output(output):
    if output == 0:
        return Characters.THIEF
    elif output == 1:
        return Characters.TINKER
    elif output == 2:
        return Characters.RANGER


def decode_forest_output(output, game_state: GameState):
    return game_state.board.forests[output]


def decode_space_output(output, game_state: GameState):
    # Clearings and then forests
    spaces = []
    spaces.extend(game_state.board.clearings)
    spaces.extend(game_state.board.forests)
    return spaces[output]


def decode_quest_output(output):
    quests = [RABBIT_ERRAND, FOX_ERRAND, MOUSE_ESCORT, RABBIT_EXPEL_BANDITS, MOUSE_EXPEL_BANDITS, RABBIT_FEND_BEAR, MOUSE_FEND_BEAR,
              FUNDRAISING, RABBIT_SPEECH, FOX_SPEECH, RABBIT_GUARD_DUTY, MOUSE_GUARD_DUTY, FOX_LOGISTICS_HELP, MOUSE_LOGISTICS_HELP, REPAIR_A_SHED]
    return quests[output]


def decode_aid_take_item_output(output):
    if output >= len(Items):
        return None
    return list(Items)[output]


def decode_item_output(output):

    # Treat the output layer as being split up into 4 blocks, with each block containing one of every item type
    # Blocks:
    # 0. Available Items
    # 1. Exhausted Items
    # 2. Damaged Items
    # 3. Exhausted and Damaged Items

    num_item_types = len(Items)

    item_index = output % num_item_types
    item = list(Items)[item_index]

    item_state = output // num_item_types

    is_exhausted = item_state in [1, 3]
    is_damaged = item_state in [2, 3]

    return item, is_exhausted, is_damaged


def decode_strike_output(output, chosen_faction: Faction, game_state: GameState):
    # If the targeted enemy has any warriors - return warrior
    if game_state.vagabond.vagabond_pawn.space.get_faction_warrior_count(chosen_faction.faction_id) > 0:
        return decode_warrior_output(output)
    else:
        return decode_piece_output(output, game_state)


def decode_aid_exhaust_item(output):
    items = list(Items)
    items.extend([Items.TEA, Items.BAG, Items.COINS])
    use_item_track = output >= len(Items)
    item = items[output]
    return item, use_item_track


def decode_battle_damage_item(output):
    items_list = list(Items)
    track_items = [Items.TEA, Items.BAG, Items.COINS]

    n = len(items_list)

    if output < n:
        # Not exhausted, no track
        return items_list[output], False, False

    elif output < 2 * n:
        # Exhausted, no track
        return items_list[output - n], True, False

    else:
        # Use track items
        return track_items[output - 2 * n], False, True
