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


class ActionIDs(Enum):
    # Cards
    BETTER_BURROW_BANK = 1
    CLAIM_DOMINANCE = 2
    CODEBREAKERS = 3
    DOMINANCE = 4
    ROYAL_CLAIM = 5
    STAND_AND_DELIVER = 6
    TAX_COLLECTOR = 7

    # Eyrie Dynasties
    DECREE_BATTLE = 8
    DECREE_BUILD = 9
    DECREE_MOVE = 10
    DECREE_RECRUIT = 11
    EXTEND_DECREE = 12
    REPLENISH_HAND = 13
    ROOSTLESS = 14
    SCORE_VP = 15

    # Factionless
    BATTLE = 16
    CRAFT = 17
    DRAW_AND_DISCARD = 18
    MOVE = 19
    PLAY_DOMINANCE = 20

    # Marquise
    MARCH = 21
    MARQUISE_BUILD = 22
    OVERWORK = 23
    PLACE_WOOD = 24
    MARQUISE_RECRUIT = 25
    SPEND_BIRD_CARD = 26

    # Vagabond
    AID = 27
    EMPTY_SATCHEL = 28
    EVENINGS_REST = 29
    EXPLORE = 30
    QUEST = 31
    REFRESH = 32
    REPAIR = 33
    SLIP = 34
    SPECIAL = 35
    STRIKE = 36
    VAGABOND_BATTLE = 37
    VAGABOND_CRAFT = 38
    VAGABOND_MOVE = 39

    # Woodland Alliance
    ALLIANCE_RECRUIT = 40
    MOBILIZE = 41
    MODIFY_EVENING_ACTION = 42
    ORGANIZE = 43
    REVOLT = 44
    SPREAD_SYMPATHY = 45
    TRAIN = 46
