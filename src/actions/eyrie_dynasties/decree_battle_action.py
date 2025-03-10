from __future__ import annotations
from typing import TYPE_CHECKING
from utils.root_types import Suits
from actions.factionless.battle_action import BattleAction
from controllers.messages.game_messages import BattleClearingChoiceMessage, BattleTargetChoiceMessage
from actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from factions.eyrie_dynasties import EyrieDynasties


class DecreeBattleAction(BattleAction):
    def __init__(self, suit: Suits, name="Decree Battle", max_uses=1, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.suit = suit
        self.id = ActionIDs.DECREE_BATTLE

    def can_perform(self, executor: EyrieDynasties, game_state=None):
        return True

    def _get_valid_battle_clearings(self, game_state, executor):
        valid_clearings = super()._get_valid_battle_clearings(game_state, executor)
        return [clearing for clearing in valid_clearings if clearing.get_suit() == self.suit]

    def perform(self, game_state, executor: EyrieDynasties):
        # 1. Choose clearing to battle on and who to battle against

        valid_clearings = self._get_valid_battle_clearings(
            game_state, executor)

        if not valid_clearings:
            print(
                f"No valid clearings found for suit {self.suit}: TURMOIL TRIGGERED")
            executor.trigger_turmoil()
            return

        clearing = executor.controller.send_game_message(
            BattleClearingChoiceMessage(valid_clearings)).chosen_clearing

        valid_targets = self._get_valid_battle_targets(
            clearing, executor, game_state)

        if not valid_targets:
            print(
                f"No valid targets found for suit {self.suit}: TURMOIL TRIGGERED")
            executor.trigger_turmoil()
            return

        target = executor.controller.send_game_message(
            BattleTargetChoiceMessage(valid_targets)).chosen_target

        # 2. battle
        self.battle(clearing, target, executor)
        super(BattleAction, self).perform(game_state, executor)
