from typing import Any, List, Callable, TYPE_CHECKING, Dict
from enum import Enum, auto
from src.controllers.messages.controller_messages import ActionChoiceResponse
from src.controllers.messages.game_messages import ActionChoiceMessage
from src.utils.root_types import GamePhase

if TYPE_CHECKING:
    from src.factions.faction import Faction
    from src.controllers.base_controllers.controller import Controller


class CallbackTimes(Enum):
    DOMINANCE_TIME = auto()
    BIRDSONG_START = auto()
    IN_BIRDSONG = auto()
    DAYLIGHT_START = auto()
    IN_DAYLIGHT = auto()
    EVENING_START = auto()
    IN_EVENING = auto()

    def get_phase(self):
        if self == CallbackTimes.BIRDSONG_START or self == CallbackTimes.IN_BIRDSONG or self == CallbackTimes.DOMINANCE_TIME:
            return GamePhase.BIRDSONG
        elif self == CallbackTimes.DAYLIGHT_START or self == CallbackTimes.IN_DAYLIGHT:
            return GamePhase.DAYLIGHT
        elif self == CallbackTimes.EVENING_START or self == CallbackTimes.IN_EVENING:
            return GamePhase.EVENING
        return None


class BattleCallbackTimes(Enum):
    BATTLE_START_ATTACKER = auto()
    BATTLE_START_DEFENDER = auto()
    IN_BATTLE_ATTACKER = auto()
    IN_BATTLE_DEFENDER = auto()
    IN_BATTLE = auto()
