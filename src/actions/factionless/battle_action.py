from __future__ import annotations
import random
from actions.action_handler import Action
from controllers.messages.game_messages import BattleClearingChoiceMessage, BattleTargetChoiceMessage, AmbushMessage
from controllers.messages.controller_messages import AmbushResponse
from utils.root_types import EyrieLeaders, Factions, Items, Suits

from typing import TYPE_CHECKING, List

from utils.callback_handler import BattleCallbackTimes
from utils.colour_utils import set_print_colour

if TYPE_CHECKING:
    from utils.game_state import GameState
    from board.clearing import Clearing
    from factions.faction import Faction
    from factions.vagabond.vagabond import Vagabond


class BattleModifier():
    def __init__(self, attacker: Faction, defender: Faction, clearing: Clearing):
        self.attacker_damage_modifier = 0
        self.defender_damage_modifier = 0
        self.attacker = attacker
        self.defender = defender
        self.clearing = clearing


class BattleAction(Action):

    def __init__(self, name="Battle", max_uses=None, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)

    def can_perform(self, executor, game_state):
        # ensure there exists a clearing to battle on
        if self.times_used >= self.max_uses:
            return False
        for clearing in game_state.board.clearings:
            if clearing.get_faction_warrior_count(executor.faction_id) == 0:
                continue
            for faction in game_state.faction_list:
                if faction.faction_id == executor.faction_id:
                    continue
                elif clearing.get_faction_piece_count(faction.faction_id) > 0:
                    return True
        return False

    def _get_valid_battle_clearings(self, game_state: GameState, executor: Faction) -> List[Clearing]:
        valid_clearings = []
        for clearing in game_state.board.clearings:
            if clearing.get_faction_piece_count(executor.faction_id) == 0:
                continue
            for faction in game_state.faction_list:
                if faction.faction_id == executor.faction_id:
                    continue
                if clearing.get_faction_piece_count(faction.faction_id) > 0:
                    valid_clearings.append(clearing)
                    break
        return valid_clearings

    def _get_valid_battle_targets(self, clearing: Clearing, executor: Faction, game_state: GameState):
        valid_targets = []
        for faction in game_state.faction_list:
            if faction.faction_id == executor.faction_id:
                continue
            if clearing.get_faction_piece_count(faction.faction_id) > 0:
                valid_targets.append(faction)
        return valid_targets

    def perform(self, game_state, executor):
        # 1. Choose clearing to battle on and who to battle against
        clearing = executor.controller.send_game_message(
            BattleClearingChoiceMessage(self._get_valid_battle_clearings(game_state, executor))).chosen_clearing
        target = executor.controller.send_game_message(BattleTargetChoiceMessage(
            self._get_valid_battle_targets(clearing, executor, game_state))).chosen_target
        # 2. battle
        self.battle(clearing, target, executor)
        self.times_used += 1

    def battle(self, clearing: Clearing, defender: Faction, attacker: Faction):
        battle_modifier = BattleModifier(attacker, defender, clearing)

        from cards.card import AmbushCard

        available_ambush_cards = [
            card for card in defender.hand if isinstance(card, AmbushCard) and (card.suit == clearing.get_suit() or card.suit == Suits.BIRD)]

        if available_ambush_cards != []:
            # If they have multiple ambush cards choose one, otherwise use the only one
            ambush_response: AmbushResponse = defender.controller.send_game_message(
                AmbushMessage(defender, attacker, clearing, False, False, available_ambush_cards))
            if ambush_response.ambush_card is not None:
                ambush_response.ambush_card._callback(battle_modifier)

        friendly_warrior_count = clearing.get_faction_warrior_count(
            attacker.faction_id) if attacker.faction_id != Factions.VAGABOND.value else attacker.satchel.get_non_damaged_count(Items.SWORD)
        enemy_warrior_count = clearing.get_faction_warrior_count(
            defender.faction_id) if defender.faction_id != Factions.VAGABOND.value else defender.satchel.get_non_damaged_count(Items.SWORD)

        roll1 = random.randint(0, 3)
        roll2 = random.randint(0, 3)
        # Attackers take the higher roll, with damage being limited by the number of warriors
        if defender.faction_id == Factions.WOODLAND_ALLIANCE.value:
            # Woodland Alliance Guerilla Warfare
            attacker_dmg = min(min(roll1, roll2), friendly_warrior_count)
            defender_dmg = min(max(roll1, roll2), enemy_warrior_count)
        else:
            attacker_dmg = min(max(roll1, roll2), friendly_warrior_count)
            defender_dmg = min(min(roll1, roll2), enemy_warrior_count)
        if attacker.faction_id == Factions.EYRIE_DYNASTY.value and attacker.eyrie_leader == EyrieLeaders.Commander:
            attacker_dmg += 1

        for callback in defender.battle_callbacks[BattleCallbackTimes.IN_BATTLE_ATTACKER]:
            callback(battle_modifier)
        for callback in attacker.battle_callbacks[BattleCallbackTimes.IN_BATTLE_DEFENDER]:
            callback(battle_modifier)
        for callback in attacker.battle_callbacks[BattleCallbackTimes.IN_BATTLE]:
            callback(battle_modifier)

        attacker_dmg += battle_modifier.attacker_damage_modifier
        defender_dmg += battle_modifier.defender_damage_modifier
        attacker_dmg = max(attacker_dmg, 0)
        defender_dmg = max(defender_dmg, 0)

        clearing.damage(victim=defender, attacker=attacker,
                        amount=attacker_dmg)
        clearing.damage(victim=attacker, attacker=defender,
                        amount=defender_dmg)
        set_print_colour(attacker.print_colour)
