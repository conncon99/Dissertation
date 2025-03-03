from typing import Any, List, Callable, TYPE_CHECKING, Dict
from enum import Enum, auto
from controllers.messages.controller_messages import ActionChoiceResponse
from controllers.messages.game_messages import ActionChoiceMessage
from utils.root_types import GamePhase

if TYPE_CHECKING:
    from factions.faction import Faction
    from controllers.base_controllers.controller import Controller


class CallbackTimes(Enum):
    DOMINANCE_TIME = auto()
    BIRDSONG_START = auto()
    IN_BIRDSONG = auto()
    DAYLIGHT_START = auto()
    IN_DAYLIGHT = auto()
    EVENING_START = auto()
    IN_EVENING = auto()

    def get_phase(self):
        if self == CallbackTimes.BIRDSONG_START or self == CallbackTimes.IN_BIRDSONG or CallbackTimes.DOMINANCE_TIME:
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


# class GameAction:

#     def __init__(self, controller: 'Controller', actions: List[Callable], remaining_actions: int = 1, is_optional: bool = False) -> None:
#         """Holds groups of game actions. -1 remaining actions indicates an action can be taken infinite times."""
#         self.actions = actions
#         self.remaining_actions = remaining_actions
#         self.is_optional = is_optional
#         self.controller = controller
#         if self.is_optional or self.remaining_actions == -1:
#             self.actions.append(self._exit_action)

#     def __call__(self, *args: Any, **kwds: Any) -> Any:
#         if not isinstance(self.actions, list):
#             self.actions = [self.actions]
#         while self.remaining_actions > 0 or self.remaining_actions == -1:
#             if len(self.actions) == 1:
#                 # Don't bother sending a message if there are no options
#                 chosen_action = self.actions[0]
#             else:
#                 chosen_action = self.controller.send_game_message(
#                     ActionChoiceMessage(self)).chosen_action

#             if chosen_action == self._exit_action:
#                 break
#             self.remaining_actions += chosen_action(*args, **kwds)

#     def _exit_action(self):
#         """A dummy callable that causes the loop to be exited once called"""
#         pass
