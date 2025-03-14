from __future__ import annotations
from pieces.building import Building
from utils.root_types import Suits
from typing import TYPE_CHECKING
from controllers.messages.game_messages import AllianceNoBaseMessage
import math
from utils.colour_utils import set_print_colour

if TYPE_CHECKING:
    from factions.woodland_alliance import WoodlandAlliance
    from board.clearing import Clearing


class AllianceBase(Building):
    def __init__(self, suit: Suits, clearing: Clearing, faction: WoodlandAlliance, slot_idx: int):
        super().__init__(clearing, faction, slot_idx, f"Alliance {suit} Base")
        self.suit = suit
        faction.bases[self.suit] = self

    def damage(self, amount, attacker, action_group):
        return self.destroy(attacker, action_group)

    def destroy(self, attacker, action_group):
        set_print_colour(self.faction.print_colour)
        self.faction.bases[self.suit] = None
        # Discard all matching and bird supporters
        print(
            f" - {self.suit.name.capitalize()} Base Destroyed, discarding all Bird and {self.suit.name.capitalize()} supporters")
        for card in self.faction.supporters:
            if card.suit == self.suit or card.suit == Suits.BIRD:
                self.faction.supporters.remove(card)
                self.faction.discard_card(card)

        # Remove half of all officers (rounded up)
        self.faction.officers -= math.ceil(self.faction.officers/2)
        print(
            f" - Lost half of all officers - down to {self.faction.officers}")

        # If no bases are left, discard supporters down to 5
        if all(base is None for base in self.faction.bases.values()):
            print(f" - No bases remaining, discarding supporters down to 5")
            if self.faction.supporters != []:
                chosen_discards = self.faction.controller.send_game_message(AllianceNoBaseMessage(
                    self.faction.game_state, action_group, self.faction.supporters, abs(5-len(self.faction.supporters)))).chosen_cards

                for card in chosen_discards:
                    self.faction.discard_card(card)
                    self.faction.supporters.remove(card)
        set_print_colour(attacker.print_colour)
        return super().destroy(attacker, action_group)
