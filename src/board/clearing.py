from __future__ import annotations
from board.space import Space
from typing import Dict, TYPE_CHECKING, List
from utils.root_types import BASE_SUITS, Factions, Suits, EyrieLeaders, Items
from controllers.messages.game_messages import PieceTargetingMessage
from utils.colour_utils import set_print_colour

if TYPE_CHECKING:
    from pieces.token import Token
    from factions.faction import Faction
    from pieces.building import Building
    from board.forest import Forest
    from utils.game_settings import GameSettings
    from factions.vagabond.vagabond import Vagabond

REMOVAL_DAMAGE = 999


class Clearing(Space):
    def __init__(self, index, suit: BASE_SUITS, slots: List[Building], adjacent_forests: List[Forest], adjacent_clearings: List[Clearing], settings: GameSettings) -> None:
        super().__init__(index, settings)
        self._suit = suit
        self.slots = slots
        self.adjacent_clearings = adjacent_clearings
        self.adjacent_forests = adjacent_forests
        self.tokens: Dict[Factions, List[Token]] = {
            faction_id: [] for faction_id in self.settings.faction_ids}

    def get_owner(self):
        """Gets the faction id with the largest number of pieces in a clearing"""
        piece_count = {
            faction_id: 0 for faction_id in self.settings.faction_ids}
        # Counts warriors
        for faction_id in piece_count.keys():
            piece_count[faction_id] += len([self.units[faction_id]])
        # Counts Buildings
        for slot in self.slots:
            if slot and slot.faction:
                piece_count[slot.faction.faction_id] += 1
        # Counts Tokens
        for token_list in self.tokens.values():
            for token in token_list:
                piece_count[token.faction.faction_id] += 1

        if Factions.VAGABOND.value in piece_count.keys():
            del piece_count[Factions.VAGABOND.value]

        max_pieces = max(piece_count.values())
        factions_with_max = [
            key for key, value in piece_count.items() if value == max_pieces and value > 0]

        # Handles Ties
        if len(factions_with_max) == 1:
            return factions_with_max[0]
        else:
            # Lord of the Forest: Eyrie win ties for control
            if Factions.EYRIE_DYNASTY.value in factions_with_max:
                return Factions.EYRIE_DYNASTY.value
            return None

    def get_suit(self):
        return self._suit

    def has_free_slots(self) -> bool:
        return any(slot is None for slot in self.slots)

    def get_first_free_slot(self) -> int:
        return self.slots.index(None)

    def get_faction_warrior_count(self, faction_id: Factions) -> int:
        return len(self.units[faction_id])

    def get_faction_piece_count(self, faction_id: Factions) -> int:
        count = len(self.units[faction_id]) + \
            len(self.tokens[faction_id])
        for slot in self.slots:
            if slot and slot.faction and slot.faction.faction_id == faction_id:
                count += 1
        return count

    def damage(self, victim: Faction, attacker: Faction, amount):

        victim_warrior_count = self.get_faction_warrior_count(
            victim.faction_id)

        # The clearing is defenceless
        if (victim_warrior_count == 0 or victim.faction_id == Factions.VAGABOND.value and victim.satchel.get_non_damaged_count(Items.SWORD) == 0) and amount != REMOVAL_DAMAGE:
            print(f" - {victim} is defenceless")
            amount += 1

        if amount > 0 and victim.faction_id == Factions.VAGABOND.value:
            if amount == REMOVAL_DAMAGE:
                print(f" - {victim} cannot be removed, dealing 3 damage")
                victim.vagabond_pawn.damage(3, attacker)
            else:
                victim.vagabond_pawn.damage(amount, attacker)
        elif amount > 0:
            for i in range(min(victim_warrior_count, amount)):
                self.units[victim.faction_id][0].damage(1, attacker)
            remaining_dmg = max(amount - victim_warrior_count, 0)
            if remaining_dmg > 0:
                print(f" - Remaining damage after warriors: {remaining_dmg}")
            targets = []
            for slot in self.slots:
                if slot and slot.faction and slot.faction.faction_id == victim.faction_id:
                    targets.append(slot)
            if len(self.tokens[victim.faction_id]) > 0:
                targets.extend(self.tokens[victim.faction_id])

            chosen_targets = victim.controller.send_game_message(
                PieceTargetingMessage(attacker, victim, min(
                    remaining_dmg, len(targets)), targets))
            for target in chosen_targets.targets:
                target.destroy(attacker)
                remaining_dmg -= 1

        set_print_colour(attacker.print_colour)
        print(
            f" - {attacker} Dealt {amount} damage to {victim} on clearing {self.index}")
        set_print_colour(victim.print_colour)
        # Marquise Field Hospital ability
        if victim.faction_id == Factions.MARQUISE_DE_CAT.value and amount > 0 and victim.keep is not None:
            # Each Marquise unit only has 1 health and there is no way to modify this
            marquise_units_destroyed = min(amount, victim_warrior_count)
            victim.use_field_hospital(self, marquise_units_destroyed)

        if attacker.faction_id == Factions.EYRIE_DYNASTY.value:
            if attacker.eyrie_leader == EyrieLeaders.Despot and attacker.gained_despot_bonus:
                attacker.add_vp(1)
            attacker.gained_despot_bonus = False
