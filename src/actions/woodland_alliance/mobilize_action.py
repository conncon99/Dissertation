from __future__ import annotations
from actions.action_handler import Action
from typing import TYPE_CHECKING
from controllers.messages.game_messages import MobilizeMessage
from actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from factions.woodland_alliance import WoodlandAlliance


class MobilizeAction(Action):
    def __init__(self, name="Mobilize", max_uses=None, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.id = ActionIDs.MOBILIZE

    def can_perform(self, executor: WoodlandAlliance, game_state=None):
        return len(executor.hand) > 0 and super().can_perform(executor, game_state) and ((len(executor.supporters) < 5 and executor.get_base_count() == 0) or executor.get_base_count() > 0)

    def perform(self, game_state, executor: WoodlandAlliance):
        chosen_card = executor.controller.send_game_message(
            MobilizeMessage(executor.hand)).chosen_card
        executor.hand.remove(chosen_card)
        executor.add_supporter(chosen_card)
        print(f" - Added '{chosen_card}' to Supporters")
        return super().perform(game_state, executor)
