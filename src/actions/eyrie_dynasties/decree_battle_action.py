from __future__ import annotations
from typing import TYPE_CHECKING
from src.utils.root_types import Suits, suit_matches
from src.actions.factionless.battle_action import BattleAction
from src.controllers.messages.game_messages import BattleClearingChoiceMessage, BattleTargetChoiceMessage
from src.actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from src.factions.eyrie_dynasties import EyrieDynasties
    from src.utils.game_state import GameState


class DecreeBattleAction(BattleAction):
    def __init__(self, suit: Suits, name="Decree Battle", max_uses=1, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.suit = suit
        id_dict = {Suits.FOX: ActionIDs.DECREE_BATTLE_FOX, Suits.MOUSE: ActionIDs.DECREE_BATTLE_MOUSE,
                   Suits.RABBIT: ActionIDs.DECREE_BATTLE_RABBIT, Suits.BIRD: ActionIDs.DECREE_BATTLE_BIRD}
        self.id = id_dict[self.suit]
        self.turmoil_action = True

    def can_perform(self, executor: EyrieDynasties, game_state=None):
        valid_clearings = self._get_valid_battle_clearings(
            game_state, executor)
        return len(valid_clearings) > 0 and any(len(self._get_valid_battle_targets(clearing, executor, game_state)) > 0 for clearing in valid_clearings)

    def _get_valid_battle_clearings(self, game_state: GameState, executor):
        valid_clearings = super()._get_valid_battle_clearings(game_state, executor)
        return [clearing for clearing in valid_clearings if suit_matches(self.suit, clearing.get_suit())]

    def perform(self, game_state: GameState, executor: EyrieDynasties):
        # 1. Choose clearing to battle on and who to battle against

        valid_clearings = self._get_valid_battle_clearings(
            game_state, executor)

        response = yield BattleClearingChoiceMessage(game_state, self.action_group, valid_clearings)
        clearing = response.chosen_clearing
        game_state.selected_clearing = clearing
        valid_targets = self._get_valid_battle_targets(
            clearing, executor, game_state)

        response = yield BattleTargetChoiceMessage(game_state, self.action_group, valid_targets)
        target = response.chosen_target
        game_state.selected_clearing = None
        # 2. battle
        yield from self.battle(clearing, target, executor, game_state)
        super(BattleAction, self).perform(game_state, executor)
