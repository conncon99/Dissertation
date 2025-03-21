from __future__ import annotations
from cards.cards import *
from pieces.marquise_de_cat.marquise_buildings import Recruiter, Sawmill, Workshop
from actions.action_handler import ActionGroup
from pieces.piece_with_id import PieceWithID

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from utils.game_state import GameState


def decode_binary_choice(output):
    return output == 0


def decode_numerical_selection(output):
    return output


def decode_action_output(output, action_size, action_group: ActionGroup):
    actions = [None] * action_size
    for action in action_group.actions:
        if action is not None:
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
        ROYAL_CLAIM,  # 53
        None  # 54
    ]
    return cards[output]


def decode_faction_output(output, game_state: GameState):
    factions = [
        game_state.marquise,
        game_state.eyrie_dynasties,
        game_state.woodland_alliance,
        game_state.vagabond
    ]
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

# Wood


def decode_wood_output(output, game_state: GameState):
    return [wood for wood in game_state.marquise.wood if wood.id == output][0]


### MASKS ###

class Masker:

    def __init__(self, action_size: int = 55):
        self.action_size = action_size

    def binary_mask(self):
        return [i < 2 for i in range(self.action_size)]

    def card_mask(self, available_cards, allow_none=False):
        mask = [False] * self.action_size
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

        for i in range(len(cards)):
            mask[i] = cards[i] in available_cards

        if allow_none:
            mask[54] = True

        return mask

    def faction_mask(self, available_factions, game_state: GameState):
        mask = [False] * self.action_size
        mask[0] = game_state.marquise in available_factions
        mask[1] = game_state.eyrie_dynasties in available_factions
        mask[2] = game_state.woodland_alliance in available_factions
        mask[3] = game_state.vagabond in available_factions
        return mask

    def clearing_mask(self, available_clearings, game_state: GameState):
        mask = [False] * self.action_size
        for i, clearing in enumerate(game_state.board.clearings):
            mask[i] = clearing in available_clearings

        return mask

    def warrior_mask(self, available_units):
        mask = [False] * self.action_size
        EYRIE_OFFSET = 25
        WOODLAND_ALLIANCE_OFFSET = 45
        VAGABOND_OFFSET = 55

        for unit in available_units:
            if unit.name == "Eyrie Dynasties Pawn":
                mask[EYRIE_OFFSET + unit.id] = True
            elif unit.name == "Woodland Alliance Pawn":
                mask[WOODLAND_ALLIANCE_OFFSET + unit.id] = True
            elif unit.name == "Vagabond Pawn":
                mask[VAGABOND_OFFSET + unit.id] = True
            else:
                mask[unit.id] = True
        return mask

    def piece_mask(self, available_pieces):
        mask = [False] * self.action_size

        for piece in available_pieces:
            mask[self._get_piece_offset(piece) + piece.id] = True
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
                        "Alliance Fox Base": ALLIANCE_OFFSET, "Alliance Mouse Base": ALLIANCE_OFFSET, "Alliance Rabbit Base": ALLIANCE_OFFSET, "Sympathy Token": SYMPATHY_OFFSET}
        return offset_types[piece.name]

    def action_mask(self, available_actions):
        mask = [False] * self.action_size

        for action in available_actions:
            if action is not None:
                mask[action.id.value - 1] = True
            else:
                mask[-1] = True

        if None in available_actions:
            mask[54] = True

        return mask

    # Marquise

    def marquise_building_type_mask(self, available_building_types):
        mask = [False] * self.action_size
        mask[0] = Sawmill in available_building_types
        mask[1] = Recruiter in available_building_types
        mask[2] = Workshop in available_building_types
        return mask

    def wood_mask(self, available_wood):
        mask = [False] * self.action_size
        ids = [wood.id for wood in available_wood]
        for id in ids:
            mask[id] = True
        return mask
