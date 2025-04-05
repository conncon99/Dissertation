from __future__ import annotations
from actions.action_handler import Action
from utils.root_types import Items
from typing import TYPE_CHECKING
from board.clearing import Clearing
from controllers.messages.game_messages import AidCardChoiceMessage, AidFactionChoiceMessage, AidExhaustItemChoiceMessage, AidTakeItemChoiceMessage
from controllers.messages.controller_messages import AidExhaustItemChoiceResponse
from actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from factions.vagabond.vagabond import Vagabond
    from factions.faction import Faction
    from cards.card import Card


class AidAction(Action):
    def __init__(self, name='Aid', max_uses=None, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.id = ActionIDs.AID

    def can_perform(self, executor: Vagabond, game_state=None):
        return executor.satchel.has_available_item() and isinstance(executor.vagabond_pawn.space, Clearing) \
            and any(executor.vagabond_pawn.space.get_faction_piece_count(faction.faction_id) and executor.faction_id != faction.faction_id for faction in game_state.faction_list) \
            and any(card.suit == executor.vagabond_pawn.space.get_suit() for card in executor.hand)

    def perform(self, game_state, executor: Vagabond):
        # 1. Get available players to aid

        assert isinstance(executor.vagabond_pawn.space, Clearing)
        available_players = [
            faction for faction in game_state.faction_list if executor.vagabond_pawn.space.get_faction_piece_count(faction.faction_id) > 0 and faction.faction_id != executor.faction_id]

        # 2. Choose player to aid
        response = yield AidFactionChoiceMessage(game_state, self.action_group, available_players)
        chosen_faction: Faction = response.chosen_faction

        # 3. Choose and exhaust item
        available_items = [
            item for item, amount in executor.satchel.available_items.items() for _ in range(amount)]
        exhaust_item_response: AidExhaustItemChoiceResponse = yield AidExhaustItemChoiceMessage(game_state, self.action_group, available_items, executor.active_bag_count, executor.active_coin_count, executor.active_tea_count)

        executor.satchel.exhaust_item(
            exhaust_item_response.chosen_item, exhaust_item_response.use_item_track)

        # 4. Get available cards to give aided player

        available_cards = [card for card in executor.hand if card.suit ==
                           executor.vagabond_pawn.space.get_suit()]

        # 5. Choose card to give to aided player

        response = yield AidCardChoiceMessage(game_state, self.action_group, available_cards)
        chosen_card: Card = response.chosen_card

        chosen_faction.hand.append(chosen_card)
        executor.hand.remove(chosen_card)
        print(f" - Given card '{chosen_card}' to {chosen_faction}")

        executor.relationship_track.aid_faction(chosen_faction.faction_id)

        # 6. Choose item (or None) to take from aided player's satchel

        available_items = [None]
        if len(chosen_faction.items) > 0:
            available_items.extend(chosen_faction.items)

        response = yield AidTakeItemChoiceMessage(game_state, self.action_group, available_items)
        taken_item: Items = response.chosen_item

        # 7. Take item and add it to available items in satchel

        if taken_item is not None:
            print(
                f" - Taken {taken_item.name.capitalize()} from {chosen_faction}")
            chosen_faction.items.remove(taken_item)
            executor.satchel.add_item(taken_item)
        else:
            print(f" - No item taken from {chosen_faction}")

        return super().perform(game_state, executor)
