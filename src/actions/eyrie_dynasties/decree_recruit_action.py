from __future__ import annotations
from actions.action_handler import Action
from typing import TYPE_CHECKING
from utils.root_types import Suits, EyrieLeaders, Factions
from pieces.pawn import Pawn
from controllers.messages.game_messages import DecreeRecruitClearingMessage
from pieces.marquise_de_cat.marquise_tokens import Keep

if TYPE_CHECKING:
    from factions.eyrie_dynasties import EyrieDynasties
    from board.clearing import Clearing


class DecreeRecruitAction(Action):
    def __init__(self, suit: Suits, name="Decree Recruit", max_uses=1, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.suit = suit

    def can_perform(self, executor, game_state=None):
        return True

    def perform(self, game_state, executor: EyrieDynasties):
        valid_roosts = [
            roost for roost in executor.roosts if roost.get_suit() == self.suit]

        if not valid_roosts:
            print(
                f" - No {self.suit.name.capitalize()} roosts found: TURMOIL TRIGGERED")
            executor.trigger_turmoil()
            return

        if len(executor.units) >= executor.max_warriors:
            print(f" - Cannot place any more warriors: TURMOIL TRIGGERED")
            executor.trigger_turmoil()
            return

        available_clearings = [roost.space for roost in valid_roosts if not any(isinstance(
            token, Keep) for token in roost.space.tokens[Factions.MARQUISE_DE_CAT.value])]

        roost_clearing: Clearing = executor.controller.send_game_message(
            DecreeRecruitClearingMessage(available_clearings)).chosen_clearing
        Pawn(roost_clearing, executor)

        if executor.eyrie_leader == EyrieLeaders.Charismatic:
            if len(executor.units) >= executor.max_warriors:
                print(f" - Cannot place any more warriors: TURMOIL TRIGGERED")
                executor.trigger_turmoil()
                return
            Pawn(roost_clearing, executor)

        return super().perform(game_state, executor)
