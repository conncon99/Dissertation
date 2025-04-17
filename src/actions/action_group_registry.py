from enum import Enum, auto


class ActionGroupRegistry:
    """A singleton registry to track unique ActionGroup integer IDs."""

    _instance = None  # Store the single instance of the class

    def __new__(cls):
        """Ensure only one instance of ActionGroupRegistry exists."""
        if cls._instance is None:
            cls._instance = super(ActionGroupRegistry, cls).__new__(cls)
            cls._instance._id_registry = {}  # Maps unique identifier strings to integer IDs
        return cls._instance

    def get_unique_id(self) -> int:
        """Returns a globally unique integer ID for a given identifier."""
        identifier = 0
        while True:
            if identifier not in self._id_registry:
                self._id_registry[identifier] = identifier
                break
            else:
                identifier += 1  # Increment counter for the next ID

        return self._id_registry[identifier]

    @classmethod
    def reset(cls):
        """Resets the singleton instance and clears all stored IDs."""
        if cls._instance is not None:
            cls._instance._id_registry.clear()  # Clear existing mappings
        cls._instance = None  # Reset the singleton instance

    @classmethod
    def get_registery_size(cls) -> int:
        if cls._instance is None:
            return 0
        return len(cls._instance._id_registry)


class ActionIDs(Enum):  # 59
    # Cards - 7
    BETTER_BURROW_BANK = auto()
    CLAIM_DOMINANCE = auto()
    CODEBREAKERS = auto()
    DOMINANCE = auto()
    ROYAL_CLAIM = auto()
    STAND_AND_DELIVER = auto()
    TAX_COLLECTOR = auto()

    # Eyrie Dynasties - 20
    DECREE_BATTLE_FOX = auto()
    DECREE_BATTLE_MOUSE = auto()
    DECREE_BATTLE_BIRD = auto()
    DECREE_BATTLE_RABBIT = auto()

    DECREE_BUILD_FOX = auto()
    DECREE_BUILD_MOUSE = auto()
    DECREE_BUILD_BIRD = auto()
    DECREE_BUILD_RABBIT = auto()

    DECREE_MOVE_FOX = auto()
    DECREE_MOVE_MOUSE = auto()
    DECREE_MOVE_BIRD = auto()
    DECREE_MOVE_RABBIT = auto()

    DECREE_RECRUIT_FOX = auto()
    DECREE_RECRUIT_MOUSE = auto()
    DECREE_RECRUIT_BIRD = auto()
    DECREE_RECRUIT_RABBIT = auto()

    EXTEND_DECREE = auto()
    REPLENISH_HAND = auto()
    ROOSTLESS = auto()
    SCORE_VP = auto()

    # Factionless - 6
    BATTLE = auto()
    CRAFT = auto()
    DRAW_AND_DISCARD = auto()
    MOVE = auto()
    MOVE_UNITS = auto()
    PLAY_DOMINANCE = auto()

    # Marquise - 6
    MARCH = auto()
    MARQUISE_BUILD = auto()
    OVERWORK = auto()
    PLACE_WOOD = auto()
    MARQUISE_RECRUIT = auto()
    SPEND_BIRD_CARD = auto()

    # Vagabond - 13
    AID = auto()
    EMPTY_SATCHEL = auto()
    EVENINGS_REST = auto()
    EXPLORE = auto()
    QUEST = auto()
    REFRESH = auto()
    REPAIR = auto()
    SLIP = auto()
    SPECIAL = auto()
    STRIKE = auto()
    VAGABOND_BATTLE = auto()
    VAGABOND_CRAFT = auto()
    VAGABOND_MOVE = auto()

    # Woodland Alliance - 7
    ALLIANCE_RECRUIT = auto()
    MOBILIZE = auto()
    MODIFY_EVENING_ACTION = auto()
    ORGANIZE = auto()
    REVOLT = auto()
    SPREAD_SYMPATHY = auto()
    TRAIN = auto()
