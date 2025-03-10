from enum import Enum, auto
from typing import Literal


class Suits(Enum):
    FOX = 1
    RABBIT = 2
    MOUSE = 3
    BIRD = 4  # The bird is a wild card


# A type containing all non-wild (bird) suits
BASE_SUITS = Literal[Suits.FOX, Suits.MOUSE, Suits.RABBIT]


class GamePhase(Enum):
    BIRDSONG = auto()
    DAYLIGHT = auto()
    EVENING = auto()


class Items(Enum):
    BOOTS = auto()
    SWORD = auto()
    BAG = auto()
    HAMMER = auto()
    TEA = auto()
    COINS = auto()
    CROSSBOW = auto()
    TORCH = auto()

# Factions - Union


class Factions(Enum):
    MARQUISE_DE_CAT = 1
    EYRIE_DYNASTY = 2
    WOODLAND_ALLIANCE = 3
    VAGABOND = 4


# Eyrie Decree Types
RECRUIT = 1
MOVE = 2
BATTLE = 3
BUILD = 4


class EyrieLeaders(Enum):

    def __new__(cls, value, vizier_1, vizier_2):
        member = object.__new__(cls)
        member._value_ = value
        member.vizier_1 = vizier_1
        member.vizier_2 = vizier_2
        return member

    Despot = (0, MOVE, BUILD)
    Commander = (1, MOVE, BATTLE)
    Charismatic = (2, RECRUIT, BATTLE)
    Builder = (3, RECRUIT, MOVE)
