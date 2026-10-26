from __future__ import annotations
from src.actions.action_handler import Action
from src.controllers.messages.game_messages import StandAndDeliverMessage
from typing import TYPE_CHECKING
from src.actions.action_group_registry import ActionIDs
import numpy as np

if TYPE_CHECKING:
    from src.factions.faction import Faction
    from src.cards.card import Card


class StandAndDeliverAction(Action):
    def __init__(self, name="Stand and Deliver", max_uses=1, is_action_group_modifier=True, group_spanning=True):
        super().__init__(name, max_uses, is_action_group_modifier, group_spanning=group_spanning)
        self.id = ActionIDs.STAND_AND_DELIVER

    def can_perform(self, executor, game_state):
        return super().can_perform(executor, game_state) and any(len(faction.hand) > 0 and faction.faction_id != executor.faction_id for faction in game_state.faction_list)

    def perform(self, game_state, executor):
        # 1. Choose other player
        available_players = [
            faction for faction in game_state.faction_list if faction.faction_id != executor.faction_id and len(faction.hand) > 0]
        response = yield StandAndDeliverMessage(game_state, self.action_group, available_players)
        chosen_player: Faction = response.chosen_player

        # 2. Take a random card from that player
        card = np.random.choice(chosen_player.hand)
        chosen_player.hand.remove(card)
        executor.hand.append(card)
        self.logger.info(
            f" - {executor} has taken a '{card}' from {chosen_player} and given them 1 Victory Point")

        # 3. That player receives a victory point
        chosen_player.add_vp(1)
        return super().perform(game_state, executor)
