from __future__ import annotations
from pieces.pawn import Pawn
from typing import TYPE_CHECKING
from utils.colour_utils import set_print_colour
from controllers.messages.game_messages import BattleDamageItemMessage
from controllers.messages.controller_messages import BattleDamageItemResponse

if TYPE_CHECKING:
    from factions.vagabond.vagabond import Vagabond


class VagabondPawn(Pawn):
    def __init__(self, space, faction: Vagabond):
        super().__init__(space, faction)
        faction.vagabond_pawn = self

    def damage(self, amount, attacker, action_group):
        set_print_colour(self.faction.print_colour)
        for _ in range(amount):
            self.faction: Vagabond
            if not self.faction.satchel.has_available_item() and not self.faction.satchel.has_available_exhausted_items() and self.faction.active_bag_count == 0 and self.faction.active_coin_count == 0 and self.faction.active_tea_count == 0:
                print(f" - {self.faction} has no undamaged items")
                break
            available_items = [
                item for item, amount in self.faction.satchel.available_items.items() for _ in range(amount)]
            exhausted_items = [
                item for item, amount in self.faction.satchel.exhausted_items.items() for _ in range(amount)]
            response: BattleDamageItemResponse = self.faction.controller.send_game_message(
                BattleDamageItemMessage(self.faction.game_state, action_group, available_items, exhausted_items, self.faction.active_bag_count, self.faction.active_coin_count, self.faction.active_tea_count))
            self.faction.satchel.damage_item(
                response.chosen_item, response.is_exhausted, response.use_item_track)
        set_print_colour(attacker.print_colour)

    def destroy(self, attacker, action_group=None):
        print(" - Vagabond cannot be destroyed")
        return
