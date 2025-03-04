from __future__ import annotations
from actions.action_handler import Action
from cards.cards import DOMINANCE_CARDS
from typing import TYPE_CHECKING
from utils.root_types import Factions
from controllers.messages.game_messages import ChooseDominanceMessage
from factions.vagabond.relationship_track import HOSTILE, INDIFFERENT

if TYPE_CHECKING:
    from cards.card import DominanceCard
    from utils.game_state import GameState
    from factions.faction import Faction
    from factions.vagabond.vagabond import Vagabond


class PlayDominanceAction(Action):
    def __init__(self, name="Play Dominance", max_uses=1, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)

    def can_perform(self, executor, game_state=None):
        if executor.faction_id != Factions.VAGABOND.value:
            return any(card in executor.hand for card in DOMINANCE_CARDS) and not executor.dominance and executor.victory_points >= 10 and super().can_perform(executor, game_state)
        else:
            return len(game_state.faction_list) >= 4 and any(card in executor.hand for card in DOMINANCE_CARDS) and not executor.dominance and executor.victory_points >= 10 and any(faction.dominance is None and faction.faction_id != executor.faction_id for faction in game_state.faction_list) and super().can_perform(executor, game_state)

    def perform(self, game_state, executor):
        # 1. Choose which dominance card to use if we have multiple
        available_dominance_cards = [
            card for card in executor.hand if card in DOMINANCE_CARDS]

        if len(available_dominance_cards) > 1:
            chosen_card: DominanceCard = executor.controller.send_game_message(
                ChooseDominanceMessage(available_dominance_cards)).chosen_card
        else:
            chosen_card: DominanceCard = available_dominance_cards[0]

        # 2. Activate the dominance card

        if executor.faction_id != Factions.VAGABOND.value:
            chosen_card.owner = executor
            chosen_card.activate(game_state.board)
            print(f" - {executor} has activated {chosen_card}")
        else:
            # Get the player other than the vagabond with the lowest VP
            # On a tie the vagabond chooses between the tied players
            lowest_scoring_factions = self._get_lowest_scoring_factions(
                game_state, executor)

            if len(lowest_scoring_factions) == 1:
                chosen_faction: Faction = lowest_scoring_factions[0]
            else:
                # TODO: Choose faction
                chosen_faction: Faction = lowest_scoring_factions[0]
            executor.dominance = chosen_faction
            # If the faction is hostile, move their relationship to indifferent
            if executor.relationship_track.relationship_level[chosen_faction.faction_id] == HOSTILE:
                executor.relationship_track.relationship_level[chosen_faction.faction_id] = INDIFFERENT
            executor.relationship_track.relationship_level
            executor.hand.remove(chosen_card)
            print(
                f" - {executor} has activated {chosen_card} to form a coalition with {chosen_faction}")
        return super().perform(game_state, executor)

    def _get_lowest_scoring_factions(self, game_state: GameState, executor: Faction):
        lowest_score = 999
        lowest_scoring_factions = []

        for faction in game_state.faction_list:
            if faction.faction_id == executor.faction_id or faction.dominance:
                continue

            if faction.victory_points < lowest_score:
                lowest_score = faction.victory_points
                lowest_scoring_factions.clear()
                lowest_scoring_factions.append(faction)
            elif faction.victory_points == lowest_score:
                lowest_scoring_factions.append(faction)
        return lowest_scoring_factions
