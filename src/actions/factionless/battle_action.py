from __future__ import annotations
import numpy as np
from src.actions.action_handler import Action
from src.controllers.messages.game_messages import BattleClearingChoiceMessage, BattleTargetChoiceMessage, AmbushMessage, ChooseAllyMessage
from src.controllers.messages.controller_messages import AmbushResponse
from src.utils.root_types import EyrieLeaders, Factions, Items, Suits

from typing import TYPE_CHECKING, List

from src.utils.callback_handler import BattleCallbackTimes
from src.utils.colour_utils import set_print_colour
from src.actions.action_group_registry import ActionIDs
from src.controllers.nn_controllers.battle_data import BattleData

if TYPE_CHECKING:
    from src.utils.game_state import GameState
    from src.board.clearing import Clearing
    from src.factions.faction import Faction
    from src.factions.vagabond.vagabond import Vagabond


class BattleModifiers():
    def __init__(self, attacker: Faction, defender: Faction, clearing: Clearing):
        # Extra hits dealt by the attacker (to the defender) and by the defender (to the attacker)
        self.attacker_damage_modifier = 0
        self.defender_damage_modifier = 0
        # Armorers: the rolled hits dealt by that side are ignored
        self.ignore_attacker_rolled_hits = False
        self.ignore_defender_rolled_hits = False
        self.attacker = attacker
        self.defender = defender
        self.clearing = clearing


class BattleAction(Action):

    def __init__(self, name="Battle", max_uses=None, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.id = ActionIDs.BATTLE

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
            # Battles are started from clearings with your warriors or pawn (4.3)
            if clearing.get_faction_warrior_count(executor.faction_id) == 0:
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
        response = yield BattleClearingChoiceMessage(game_state, self.action_group, self._get_valid_battle_clearings(game_state, executor))
        clearing = response.chosen_clearing
        game_state.selected_clearing = clearing

        response = yield BattleTargetChoiceMessage(game_state, self.action_group, self._get_valid_battle_targets(clearing, executor, game_state))
        target = response.chosen_target
        game_state.selected_faction = target
        # 2. battle
        yield from self.battle(clearing, target, executor, game_state)
        self.times_used += 1
        game_state.selected_clearing = None
        game_state.selected_faction = None

    def battle(self, clearing: Clearing, defender: Faction, attacker: Faction, game_state: GameState):
        battle_modifier = BattleModifiers(attacker, defender, clearing)

        from src.cards.card import AmbushCard

        available_ambush_cards = [
            card for card in defender.hand if isinstance(card, AmbushCard) and (card.suit == clearing.get_suit() or card.suit == Suits.BIRD)]
        ambush_response = None
        # Step 1: Defender may ambush (4.3.1)
        if available_ambush_cards != []:
            # If they have multiple ambush cards choose one, otherwise use the only one
            game_state.battle_data = BattleData(
                attacker, defender, clearing, attacker.faction_id == game_state.current_player.faction_id)
            game_state.active_player = defender
            ambush_response: AmbushResponse = yield AmbushMessage(game_state, self.action_group, defender, attacker, clearing, False, False, available_ambush_cards)
            game_state.active_player = game_state.current_player
            if ambush_response.ambush_card is not None:
                yield from ambush_response.ambush_card._callback(
                    game_state, self.action_group, battle_modifier)
                # If no attacking warriors or pawns remain, the battle ends immediately (4.3.1.II)
                if attacker.faction_id != Factions.VAGABOND.value and clearing.get_faction_warrior_count(attacker.faction_id) == 0:
                    self.logger.info(
                        " - No attacking warriors remain after the ambush, ending the battle")
                    game_state.battle_data = None
                    return

        was_ambushed = ambush_response is not None and ambush_response.ambush_card is not None

        # The Vagabond may attack alongside an allied faction (9.2.9.II.c)
        chosen_ally = None
        if attacker.faction_id == Factions.VAGABOND.value:
            # Get allies excluding the other faction involved
            available_allies = attacker.get_allied_warriors_in_clearing(
                clearing)
            if defender in available_allies:
                available_allies.remove(defender)

            if available_allies != []:
                available_allies.append(None)
                game_state.battle_data = BattleData(attacker, defender, clearing, attacker.faction_id ==
                                                    game_state.current_player.faction_id, was_ambushed)
                game_state.active_player = attacker
                response = yield ChooseAllyMessage(game_state, self.action_group, available_allies)
                chosen_ally = response.chosen_ally
                game_state.active_player = game_state.current_player
                attacker.battle_ally = chosen_ally
                if chosen_ally is not None:
                    self.logger.info(
                        f" - Attacking with '{chosen_ally}' as ally")

        # Step 2: Roll dice. Maximum rolled hits is limited by the number of warriors (4.3.2.I)
        if attacker.faction_id == Factions.VAGABOND.value:
            friendly_warrior_count = attacker.satchel.get_non_damaged_count(
                Items.SWORD)
            if chosen_ally is not None:
                friendly_warrior_count += clearing.get_faction_warrior_count(
                    chosen_ally.faction_id)
        else:
            friendly_warrior_count = clearing.get_faction_warrior_count(
                attacker.faction_id)
        enemy_warrior_count = clearing.get_faction_warrior_count(
            defender.faction_id) if defender.faction_id != Factions.VAGABOND.value else defender.satchel.get_non_damaged_count(Items.SWORD)

        roll1 = np.random.randint(0, 4)
        roll2 = np.random.randint(0, 4)
        # Attackers take the higher roll, with damage being limited by the number of warriors
        if defender.faction_id == Factions.WOODLAND_ALLIANCE.value:
            # Woodland Alliance Guerilla Warfare
            attacker_dmg = min(min(roll1, roll2), friendly_warrior_count)
            defender_dmg = min(max(roll1, roll2), enemy_warrior_count)
        else:
            attacker_dmg = min(max(roll1, roll2), friendly_warrior_count)
            defender_dmg = min(min(roll1, roll2), enemy_warrior_count)

        if game_state.use_manual_rolling:
            attacker_dmg = int(input("Enter Attacker Damage: "))
            defender_dmg = int(input("Enter Defender Damage: "))

        self.logger.debug(
            f" - Attacker ({attacker}) Damage before mods: {attacker_dmg}")
        self.logger.debug(
            f" - Defender ({defender}) Damage before mods: {defender_dmg}")

        def refresh_battle_data():
            game_state.battle_data = BattleData(attacker, defender, clearing, attacker.faction_id == game_state.current_player.faction_id, was_ambushed,
                                                attacker_damage_modifier=battle_modifier.attacker_damage_modifier, defender_damage_modifier=battle_modifier.defender_damage_modifier, attacker_roll=attacker_dmg, defender_roll=defender_dmg)

        # Step 3: Use effects (4.3.3). Extra hits are not limited by the number of warriors
        if attacker.faction_id == Factions.EYRIE_DYNASTY.value and attacker.eyrie_leader == EyrieLeaders.Commander:
            battle_modifier.attacker_damage_modifier += 1

        # Defenseless: the attacker deals an extra hit if the defender has no warriors (4.3.3.II)
        if enemy_warrior_count == 0:
            self.logger.info(f" - {defender} is defenseless")
            battle_modifier.attacker_damage_modifier += 1

        refresh_battle_data()

        for owner, callback_time in ((attacker, BattleCallbackTimes.IN_BATTLE_ATTACKER),
                                     (attacker, BattleCallbackTimes.IN_BATTLE),
                                     (defender, BattleCallbackTimes.IN_BATTLE_DEFENDER),
                                     (defender, BattleCallbackTimes.IN_BATTLE)):
            # Copy as cards remove themselves from the list when they are used
            for callback in list(owner.battle_callbacks[callback_time]):
                yield from callback(game_state, self.action_group, battle_modifier)
                refresh_battle_data()

        # Armorers: rolled hits are ignored, extra hits are not
        if battle_modifier.ignore_attacker_rolled_hits:
            attacker_dmg = 0
        if battle_modifier.ignore_defender_rolled_hits:
            defender_dmg = 0

        attacker_dmg = max(attacker_dmg + battle_modifier.attacker_damage_modifier, 0)
        defender_dmg = max(defender_dmg + battle_modifier.defender_damage_modifier, 0)

        # Step 4: Deal hits (4.3.4)
        if attacker.faction_id == Factions.VAGABOND.value:
            attacker.infamy_active = True
        yield from clearing.damage(victim=defender, attacker=attacker,
                                   amount=attacker_dmg, logger=self.logger, action_group=self.action_group)
        attacker_is_vagabond = attacker.faction_id == Factions.VAGABOND.value
        if attacker_is_vagabond:
            attacker.infamy_active = False
        yield from clearing.damage(victim=attacker, attacker=defender,
                                   amount=defender_dmg, logger=self.logger, action_group=self.action_group)
        if attacker_is_vagabond and attacker.battle_ally:
            attacker.battle_ally = None
        set_print_colour(attacker.print_colour)
        game_state.battle_data = None
