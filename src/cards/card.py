from __future__ import annotations
from src.controllers.messages.game_messages import AmbushMessage
from src.utils.root_types import Suits, Items, Factions, EyrieLeaders
from typing import TYPE_CHECKING, Optional
from src.utils.callback_handler import CallbackTimes, BattleCallbackTimes
from src.actions.factionless.battle_action import BattleAction, BattleModifiers
from src.actions.factionless.move_action import MoveAction
from src.controllers.messages.game_messages import BattleUseCardMessage
from src.controllers.messages.controller_messages import AmbushResponse
import logging

if TYPE_CHECKING:
    from src.factions.faction import Faction
    from src.board.clearing import Clearing
    from src.utils.game_state import GameState
    from src.actions.action_handler import Action


class Card:
    """A base class for a playable card"""

    def __init__(self, suit: Suits, name: str, is_persistent: bool, description: str) -> None:
        self.suit = suit
        self.name = name
        self.logger = logging.getLogger()
        self.description = description
        self.is_persistent = is_persistent
        self.is_craftable = False
        self.is_action_adder = False
        self.is_battle_modifier = False
        self.owner: Optional['Faction'] = None

    def __repr__(self):
        return self.name

    def make_craftable(
        self, fox_count=0, mouse_count=0, rabbit_count=0, wild_count=0
    ):
        self.is_craftable = True
        self.crafting_recipe = {
            Suits.FOX: fox_count,
            Suits.MOUSE: mouse_count,
            Suits.RABBIT: rabbit_count,
            Suits.BIRD: wild_count,
        }
        return self

    def make_action_adder(self, callback_time: CallbackTimes, action: Action):
        self.is_action_adder = True
        self.callback_time = callback_time
        self.action = action
        return self

    def make_battle_modifier(self, callback_time: BattleCallbackTimes):
        self.is_battle_modifier = True
        self.callback_time = callback_time
        return self

    def activate(self, game_state: GameState, action_group=None):
        self.game_state = game_state
        if self.is_action_adder:
            assert self.owner
            if self.action.group_spanning:
                for action_group in self.owner.actions[self.callback_time]:
                    action_group.actions.append(self.action)
            else:
                self.owner.actions[self.callback_time][0].actions.append(
                    self.action)
        if self.is_battle_modifier:
            assert self.owner
            self.owner.battle_callbacks[self.callback_time].append(
                self._callback)

    def _callback(self, game_state: GameState, action_group) -> None:
        self.logger.warning("default callback called")


class ItemCard(Card):

    def __init__(self, suit: Suits, name: str, vp_bonus: int, item_bonus: Items) -> None:
        super().__init__(suit, name, False,
                         f"When crafted, grants the owner +{vp_bonus} victory points and a {item_bonus.name.lower()} item. Then this card is discarded.")
        self.vp_bonus = vp_bonus
        self.item_bonus = item_bonus

    def activate(self, game_state: GameState, action_group):
        super().activate(game_state, action_group)
        if not self.owner.dominance:
            # Disdain for Trade
            if self.owner.faction_id == Factions.EYRIE_DYNASTY.value and self.owner.eyrie_leader != EyrieLeaders.Builder:
                self.owner.add_vp(1)
            else:
                self.owner.add_vp(self.vp_bonus)
        self.owner.items.append(self.item_bonus)
        game_state.craftable_items.remove(self.item_bonus)


class DominanceCard(Card):

    def __init__(self, suit: Suits, name: str) -> None:
        if suit == Suits.BIRD:
            description = "You win the game if you rule two opposite clearings at the start of your birdsong."
        else:
            description = f"You win the game if you rule three {suit.name.lower()} clearings at the start of your birdsong."
        super().__init__(suit, name, False, description)
        from src.actions.cards import DominanceAction
        self.make_action_adder(CallbackTimes.DOMINANCE_TIME, DominanceAction())

    def activate(self, game_state: GameState, action_group):
        super().activate(game_state, action_group)
        self.owner.dominance = self.suit
        self.owner.hand.remove(self)


class CommandWarrenCard(Card):
    def __init__(self):
        super().__init__(Suits.RABBIT, "Command Warren", True,
                         "At the start of daylight, may initiate a battle")
        self.make_craftable(rabbit_count=2)
        self.make_action_adder(
            CallbackTimes.DAYLIGHT_START, BattleAction(max_uses=1))

    def activate(self, game_state: GameState, action_group):
        assert self.owner
        self.action = BattleAction(max_uses=1)
        self.owner.actions[self.callback_time][0].actions.append(
            self.action)


class CobblerCard(Card):
    def __init__(self):
        super().__init__(Suits.RABBIT, "Cobbler", True,
                         "At the start of Evening, may take a move")
        self.make_craftable(rabbit_count=2)
        self.make_action_adder(
            CallbackTimes.EVENING_START, MoveAction(max_uses=1))

    def activate(self, game_state, action_group):
        if self.owner.faction_id == Factions.VAGABOND.value:
            from src.actions.vagabond.vagabond_move_action import VagabondMoveAction
            self.action = VagabondMoveAction(cobbler_move=True, max_uses=1)
        else:
            self.action = MoveAction(max_uses=1)
        return super().activate(game_state)


class SappersCard(Card):
    def __init__(self):
        super().__init__(Suits.BIRD, "Sappers", True,
                         "In battle as defender, may discard to deal an extra hit")
        self.make_craftable(mouse_count=1)
        self.make_battle_modifier(BattleCallbackTimes.IN_BATTLE_DEFENDER)

    def _callback(self, game_state: GameState, action_group, battle_modifier: BattleModifiers):

        if not self.owner:
            return
            yield

        if battle_modifier.clearing.get_faction_warrior_count(self.owner.faction_id) == 0:
            self.logger.debug(
                f" - Cannot use {self} in a defenseless clearing")
            return
            yield

        game_state.active_player = self.owner
        response = yield BattleUseCardMessage(game_state, action_group, self)
        use_card: bool = response.use_card
        game_state.active_player = game_state.current_player
        if use_card:
            battle_modifier.attacker_damage_modifier += 1
            self.logger.debug(f"Active cards: {self.owner.active_cards}")
            self.logger.info(
                f" - {self.owner} played {self.name} to deal an extra hit")
            self.owner.active_cards.remove(self)
            self.owner.discard_card(self)
            self.owner.battle_callbacks[self.callback_time].remove(
                self._callback)


class BrutalTacticsCard(Card):
    def __init__(self):
        super().__init__(Suits.BIRD, "Brutal Tactics", True,
                         "In battle as attacker, may deal an extra hit but the opponent scores one point")
        self.make_craftable(mouse_count=1)
        self.make_battle_modifier(BattleCallbackTimes.IN_BATTLE_ATTACKER)

    def _callback(self, game_state: GameState, action_group, battle_modifier: BattleModifiers):

        if not self.owner:
            return
            yield

        if battle_modifier.clearing.get_faction_warrior_count(self.owner.faction_id) == 0:
            self.logger.debug(
                f" - Cannot use {self} in a defenseless clearing")
            return
            yield

        game_state.active_player = self.owner
        response = yield BattleUseCardMessage(game_state, action_group, self)
        use_card: bool = response.use_card
        game_state.active_player = game_state.current_player

        if use_card:
            battle_modifier.defender_damage_modifier += 1
            battle_modifier.attacker.add_vp(1)
            self.logger.info(
                f" - {self.owner} played {self.name} to deal an extra hit, {battle_modifier.attacker} gained 1 VP")


class ArmorersCard(Card):
    def __init__(self):
        super().__init__(Suits.BIRD, "Armorers", True,
                         "In battle, may discard this to ignore all rolled hits")
        self.make_craftable(fox_count=1)
        self.make_battle_modifier(BattleCallbackTimes.IN_BATTLE)

    def _callback(self, game_state, action_group, battle_modifier: BattleModifiers):

        if not self.owner:
            return
            yield

        if battle_modifier.clearing.get_faction_warrior_count(self.owner.faction_id) == 0:
            self.logger.debug(
                f" - Cannot use {self} in a defenseless clearing")
            return
            yield

        game_state.active_player = self.owner
        response = yield BattleUseCardMessage(game_state, action_group, self)
        use_card: bool = response.use_card
        game_state.active_player = game_state.current_player

        if use_card:
            if self.owner.faction_id == battle_modifier.attacker.faction_id:
                battle_modifier.defender_damage_modifier = -999
            elif self.owner.faction_id == battle_modifier.defender.faction_id:
                battle_modifier.attacker_damage_modifier = -999
            self.owner.active_cards.remove(self)
            self.owner.discard_card(self)
            self.owner.battle_callbacks[self.callback_time].remove(
                self._callback)
            self.logger.info(
                f" - {self.owner} played {self.name} to ignore all hits")


class AmbushCard(Card):

    def __init__(self, suit: Suits, name: str) -> None:
        description = f"At the start of battle in a {suit.name.capitalize()} clearing, defender may play to deal two immediate hits, then discard. Cancel if attacker plays matching ambush."
        super().__init__(suit, name, False, description)
        self.make_battle_modifier(BattleCallbackTimes.BATTLE_START_DEFENDER)

    def _callback(self, game_state: GameState, action_group, battle_modifier: BattleModifiers):

        if battle_modifier.clearing.get_faction_warrior_count(battle_modifier.defender.faction_id) == 0:
            self.logger.debug(
                f" - Cannot use {self} in a defenseless clearing")
            return
            yield

        from src.cards.cards import SCOUTING_PARTY, SCOUTING_PARTY_2
        if SCOUTING_PARTY in battle_modifier.attacker.active_cards or SCOUTING_PARTY_2 in battle_modifier.attacker.active_cards:
            self.logger.info(" - Scouting party blocked ambush")
            # Scouting Party blocks ambushes
            return
            yield

        self.logger.info(
            f" - {battle_modifier.defender} has chosen to Ambush {battle_modifier.attacker} on Clearing {battle_modifier.clearing.index}")
        battle_modifier.defender.discard_card(self)

        available_ambush_cards = [
            card for card in battle_modifier.attacker.hand if isinstance(card, AmbushCard) and (card.suit == battle_modifier.clearing.get_suit() or card.suit == Suits.BIRD)]

        game_state.active_player = battle_modifier.attacker
        if available_ambush_cards != []:
            ambush_response: AmbushResponse = yield AmbushMessage(game_state, action_group, battle_modifier.attacker, battle_modifier.defender, battle_modifier.clearing, True, True, available_ambush_cards)
            if ambush_response.ambush_card is not None:
                self.logger.info(
                    f" - {battle_modifier.attacker} Counter-Ambushed using '{ambush_response.ambush_card}'")
                battle_modifier.attacker.discard_card(
                    ambush_response.ambush_card)
                return

        yield from battle_modifier.clearing.damage(
            victim=battle_modifier.attacker, attacker=battle_modifier.defender, amount=2, logger=self.logger, action_group=action_group)


class FavourCard(Card):

    def __init__(self, suit: Suits, name: str) -> None:
        description = f"Remove all enemy pieces in {suit.name.lower()} clearings."
        super().__init__(suit, name, False, description)

    def activate(self, game_state: GameState, action_group):
        for clearing in game_state.board.clearings:
            if clearing.get_suit() == self.suit:
                self._kill_all_enemies(clearing, game_state, action_group)

    def _kill_all_enemies(self, clearing: Clearing, game_state: GameState, action_group):
        for faction in game_state.faction_list:
            if faction.faction_id != self.owner.faction_id and clearing.get_faction_piece_count(faction.faction_id) > 0:
                yield from clearing.damage(faction, self.owner, 999, self.logger, action_group)


class BetterBurrowBankCard(Card):
    def __init__(self):
        super().__init__(Suits.RABBIT, "Better Burrow Bank", True,
                         "At start of Birdsong, you and another play draw a card")
        self.make_craftable(rabbit_count=2)
        from src.actions.cards import BetterBurrowBankAction
        self.make_action_adder(
            CallbackTimes.BIRDSONG_START, BetterBurrowBankAction())


class StandAndDeliverCard(Card):
    def __init__(self):
        super().__init__(Suits.FOX, "Stand and Deliver", True,
                         "In Birdsong, may take a random card from another player. That player scores one point")
        self.make_craftable(mouse_count=3)
        from src.actions.cards import StandAndDeliverAction
        self.make_action_adder(CallbackTimes.IN_BIRDSONG,
                               StandAndDeliverAction())


class TaxCollectorsCard(Card):
    def __init__(self):
        super().__init__(Suits.FOX, "Tax Collector", True,
                         "Once in Daylight, may remove one of your warriors to draw a card.")
        self.make_craftable(fox_count=1, mouse_count=1, rabbit_count=1)
        from src.actions.cards import TaxCollectorAction
        self.make_action_adder(CallbackTimes.IN_DAYLIGHT, TaxCollectorAction())


class CodebreakersCard(Card):
    def __init__(self):
        super().__init__(Suits.MOUSE, "Codebreakers", True,
                         "Once in Daylight, may look at another player's hand.")
        self.make_craftable(mouse_count=1)
        from src.actions.cards import CodebreakersAction
        self.make_action_adder(CallbackTimes.IN_DAYLIGHT, CodebreakersAction())


class RoyalClaimCard(Card):
    def __init__(self):
        super().__init__(Suits.BIRD, "Royal Claim", True,
                         "In Birdsong, may discard this to score one point per clearing you rule.")
        self.make_craftable(wild_count=4)
        from src.actions.cards import RoyalClaimAction
        self.make_action_adder(CallbackTimes.IN_BIRDSONG,
                               RoyalClaimAction(self))
