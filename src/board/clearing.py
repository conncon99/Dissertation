from __future__ import annotations
from src.board.space import Space
from typing import Dict, TYPE_CHECKING, List, Optional
from src.utils.root_types import BASE_SUITS, Factions, EyrieLeaders, Items
from src.controllers.messages.game_messages import PieceTargetingMessage, AllyDamageSplitMessage
from src.utils.colour_utils import set_print_colour
import logging

if TYPE_CHECKING:
    from src.pieces.token import Token
    from src.factions.faction import Faction
    from src.pieces.building import Building
    from src.board.forest import Forest
    from src.utils.game_state import GameState
    from src.factions.vagabond.vagabond import Vagabond
    from src.actions.action_handler import ActionGroup

REMOVAL_DAMAGE = 999


class Clearing(Space):
    def __init__(self, index, suit: BASE_SUITS, slots: List[Building], adjacent_forests: List[Forest], adjacent_clearings: List[Clearing], game_state: GameState) -> None:
        super().__init__(index, game_state)
        self._suit = suit
        self.slots = slots
        self.adjacent_clearings = adjacent_clearings
        self.adjacent_forests = adjacent_forests
        self.tokens: Dict[int, List[Token]] = {
            faction.faction_id: [] for faction in self.game_state.faction_list}

    def __repr__(self):
        return f"Clearing {self.index}"

    def get_owner(self):
        """Gets the faction id with the largest number of pieces in a clearing"""
        piece_count = {
            faction.faction_id: 0 for faction in self.game_state.faction_list}
        # Counts warriors (the Vagabond pawn is not a warrior and is dropped below)
        for faction_id in piece_count.keys():
            piece_count[faction_id] += len(self.units[faction_id])
        # Counts Buildings
        for slot in self.slots:
            if slot and slot.faction:
                piece_count[slot.faction.faction_id] += 1
        # Tokens and pawns do not contribute to rule (2.5)

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

    def has_keep(self) -> bool:
        """Only the Marquise can place pieces in the clearing with the keep (6.2.2)"""
        return any(token.name == "Keep Token" for token_list in self.tokens.values() for token in token_list)

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

    def damage(self, victim: Faction, attacker: Faction, amount: int, logger: logging.Logger, action_group: Optional[ActionGroup] = None):

        victim_warrior_count = self.get_faction_warrior_count(
            victim.faction_id)

        if amount > 0 and victim.faction_id == Factions.VAGABOND.value:
            yield from self._handle_vagabond_take_damage(
                victim, attacker, amount, logger, action_group)
        elif amount > 0:
            for i in range(min(victim_warrior_count, amount)):
                self.units[victim.faction_id][0].damage(
                    1, attacker, action_group)
            remaining_dmg = max(amount - victim_warrior_count, 0)
            if remaining_dmg > 0:
                logger.debug(
                    f" - Remaining damage after warriors: {remaining_dmg}")
                pass
            targets = []
            for slot in self.slots:
                if slot and slot.faction and slot.faction.faction_id == victim.faction_id:
                    targets.append(slot)
            if len(self.tokens[victim.faction_id]) > 0:
                targets.extend(self.tokens[victim.faction_id])

            while remaining_dmg > 0 and len(targets) > 0:
                self.game_state.active_player = victim
                response = yield PieceTargetingMessage(self.game_state, action_group, attacker, victim, targets)
                chosen_target = response.target
                self.game_state.active_player = self.game_state.current_player

                from src.pieces.woodland_alliance.alliance_buildings import AllianceBase
                from src.pieces.woodland_alliance.alliance_tokens import Sympathy

                if isinstance(chosen_target, Sympathy) or isinstance(chosen_target, AllianceBase):
                    yield from chosen_target.destroy(attacker, action_group)
                else:
                    chosen_target.destroy(attacker, action_group)
                remaining_dmg -= 1
                targets.remove(chosen_target)

        set_print_colour(attacker.print_colour)
        logger.info(
            f" - {attacker} Dealt {amount} damage to {victim} on clearing {self.index}")
        set_print_colour(victim.print_colour)
        # Marquise Field Hospital ability
        if victim.faction_id == Factions.MARQUISE_DE_CAT.value and amount > 0 and victim.keep is not None:
            # Each Marquise unit only has 1 health and there is no way to modify this
            marquise_units_destroyed = min(amount, victim_warrior_count)
            yield from victim.use_field_hospital(
                self, marquise_units_destroyed, action_group)

        if attacker.faction_id == Factions.EYRIE_DYNASTY.value:
            if attacker.eyrie_leader == EyrieLeaders.Despot and attacker.gained_despot_bonus:
                attacker.add_vp(1)
            attacker.gained_despot_bonus = False
        return
        yield

    def _handle_vagabond_take_damage(self, victim: Vagabond, attacker: Faction, amount: int, logger: logging.Logger, action_group: Optional[ActionGroup] = None):
        if amount == REMOVAL_DAMAGE:
            logger.info(f" - {victim} cannot be removed, dealing 3 damage")
            yield from victim.vagabond_pawn.damage(3, attacker, action_group)
            return
        elif victim.battle_ally is not None:
            self.game_state.active_player = victim
            response = yield AllyDamageSplitMessage(self.game_state, action_group, min(amount, self.get_faction_warrior_count(victim.battle_ally.faction_id)))
            chosen_damage_split = response.chosen_damage_split
            self.game_state.active_player = self.game_state.current_player
            if chosen_damage_split != 0:
                logger.info(
                    f" - Allied faction '{victim.battle_ally}' has taken {chosen_damage_split} hits for the {victim}")
                yield from self.damage(victim.battle_ally, attacker,
                                       chosen_damage_split, logger, action_group)
            yield from victim.vagabond_pawn.damage(
                amount - chosen_damage_split, attacker, action_group)
            if chosen_damage_split > amount - chosen_damage_split:
                from src.factions.vagabond.relationship_track import HOSTILE

                logger.info(
                    f" - Allied faction '{victim.battle_ally}' has taken more hits than the {victim} and has become hostile")
                victim.relationship_track.relationship_level[victim.battle_ally.faction_id] = HOSTILE
            return
            yield
        yield from victim.vagabond_pawn.damage(amount, attacker, action_group)
        return
        yield
