from __future__ import annotations
from actions.action_handler import Action
from utils.root_types import Factions
from controllers.messages.game_messages import TaxCollectorMessage
from typing import TYPE_CHECKING
from actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from pieces.pawn import Pawn


class TaxCollectorAction(Action):
    def __init__(self, name="Tax Collector", max_uses=1, is_action_group_modifier=True, group_spanning=True):
        super().__init__(name, max_uses, is_action_group_modifier, group_spanning)
        self.id = ActionIDs.STAND_AND_DELIVER

    def can_perform(self, executor, game_state=None):
        return super().can_perform(executor, game_state) and len(executor.units) > 0 and len(executor.deck.deck) + len(executor.deck.discard) > 0 and executor.faction_id != Factions.VAGABOND.value

    def perform(self, game_state, executor):
        # 1. Choose warrior to remove

        response = yield TaxCollectorMessage(game_state, self.action_group, executor.units)
        chosen_unit: Pawn = response.chosen_unit
        print(
            f" - {executor} removed its own warrior on clearing {chosen_unit.space.index}")
        chosen_unit.destroy(None, self.action_group)

        # 2. Draw a card
        card = executor.deck.draw(1)
        if card != []:
            print(f" - {executor} drew '{card[0].name}'")
            executor.hand.append(card[0])
        return super().perform(game_state, executor)
