
from __future__ import annotations
from actions.action_handler import Action
from controllers.messages.game_messages import CodebreakersMessage
from typing import TYPE_CHECKING
from actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from factions.faction import Faction


class CodebreakersAction(Action):
    def __init__(self, name="Codebreakers", max_uses=1, is_action_group_modifier=True, group_spanning=True):
        super().__init__(name, max_uses, is_action_group_modifier, group_spanning)
        self.id = ActionIDs.CODEBREAKERS

    def can_perform(self, executor, game_state=None):
        return super().can_perform(executor, game_state) and any(len(faction.hand) > 0 and faction.faction_id != executor.faction_id for faction in game_state.faction_list)

    def perform(self, game_state, executor):
        available_players = [
            faction for faction in game_state.faction_list if faction.faction_id != executor.faction_id]

        response = yield CodebreakersMessage(game_state, self.action_group, available_players)
        chosen_player: Faction = response.chosen_player
        # TODO: Make interact with Neural networks
        print(f" - {chosen_player}'s Hand: {chosen_player.hand}")

        return super().perform(game_state, executor)
