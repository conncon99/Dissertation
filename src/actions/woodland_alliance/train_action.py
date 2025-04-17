from __future__ import annotations
from src.actions.action_handler import Action
from typing import TYPE_CHECKING
from src.controllers.messages.game_messages import TrainMessage
from src.utils.root_types import Suits
from src.actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from src.factions.woodland_alliance import WoodlandAlliance


class TrainAction(Action):
    def __init__(self, name="Train", max_uses=None, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.id = ActionIDs.TRAIN

    def can_perform(self, executor: WoodlandAlliance, game_state=None):
        return len(executor.hand) > 0 and super().can_perform(executor, game_state) and (len(executor.units) + executor.officers) < executor.max_warriors and any(base is not None for base in executor.bases.values()) and self.get_available_cards_for_suits(executor)

    def get_available_cards_for_suits(self, executor: WoodlandAlliance):
        available_suits = [suit for suit,
                           base in executor.bases.items() if base is not None]
        return [card for card in executor.hand if card.suit in available_suits or card.suit == Suits.BIRD]

    def perform(self, game_state, executor: WoodlandAlliance):

        available_cards = self.get_available_cards_for_suits(executor)
        response = yield TrainMessage(game_state, self.action_group, available_cards)
        chosen_card = response.chosen_card

        executor.discard_card(chosen_card)
        executor.officers += 1
        self.logger.info(
            f" - Increased Officers to {executor.officers} by expending '{chosen_card}'")

        return super().perform(game_state, executor)
