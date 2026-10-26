from __future__ import annotations
from src.pieces.building import Building
from src.utils.root_types import Suits
from typing import TYPE_CHECKING
from src.controllers.messages.game_messages import AllianceNoBaseMessage
import math
from src.utils.colour_utils import set_print_colour

if TYPE_CHECKING:
    from src.factions.woodland_alliance import WoodlandAlliance
    from src.board.clearing import Clearing


class AllianceBase(Building):
    def __init__(self, suit: Suits, clearing: Clearing, faction: WoodlandAlliance, slot_idx: int):
        super().__init__(clearing, faction, slot_idx,
                         f"Alliance {suit.name.capitalize()} Base")
        self.suit = suit
        faction.bases[self.suit] = self

    def damage(self, amount, attacker, action_group):
        return self.destroy(attacker, action_group)

    def destroy(self, attacker, action_group):
        set_print_colour(self.faction.print_colour)
        self.faction.bases[self.suit] = None
        # Discard all matching and bird supporters
        self.logger.info(
            f" - {self.suit.name.capitalize()} Base Destroyed, discarding all Bird and {self.suit.name.capitalize()} supporters")
        for card in self.faction.supporters:
            if card.suit == self.suit or card.suit == Suits.BIRD:
                self.faction.supporters.remove(card)
                self.faction.discard_card(card)

        # Remove half of all officers (rounded up)
        self.faction.officers -= math.ceil(self.faction.officers/2)
        self.logger.info(
            f" - Lost half of all officers - down to {self.faction.officers}")

        # If no bases are left, discard supporters down to 5
        if all(base is None for base in self.faction.bases.values()):
            self.logger.info(
                f" - No bases remaining, discarding supporters down to 5")
            num_to_discard = abs(5 - len(self.faction.supporters))
            for i in range(num_to_discard):
                if self.faction.supporters == []:
                    break
                self.faction.game_state.active_player = self.faction
                response = yield AllianceNoBaseMessage(self.faction.game_state, action_group, self.faction.supporters)
                chosen_discard = response.chosen_card
                self.faction.game_state.active_player = attacker
                self.faction.discard_card(chosen_discard)
                self.faction.supporters.remove(chosen_discard)

        set_print_colour(attacker.print_colour)
        return super().destroy(attacker, action_group)
