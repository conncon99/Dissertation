from __future__ import annotations
from controllers.messages.game_messages import AmbushMessage
from utils.root_types import Suits, Items, Factions, EyrieLeaders
from typing import Dict, TYPE_CHECKING, Optional, Union
from utils.callback_handler import CallbackTimes, BattleCallbackTimes
import random
from utils.game_settings import CRAFTABLE_ITEMS
from actions.cards.dominance_action import DominanceAction
from actions.factionless.battle_action import BattleAction, BattleModifier
from actions.factionless.move_action import MoveAction
from actions.cards.better_burrow_bank_action import BetterBurrowBankAction
from controllers.messages.game_messages import BattleUseCardMessage
from controllers.messages.controller_messages import AmbushResponse
from actions.cards.stand_and_deliver_action import StandAndDeliverAction
from actions.cards.tax_collector_action import TaxCollectorAction
from actions.cards.codebreakers_action import CodebreakersAction
from actions.cards.royal_claim_action import RoyalClaimAction

if TYPE_CHECKING:
    from factions.faction import Faction
    from board.clearing import Clearing
    from utils.game_state import GameState
    from actions.action_handler import Action


class Card:
    """A base class for a playable card"""

    def __init__(self, suit: Suits, name: str, is_persistent: bool, description: str) -> None:
        self.suit = suit
        self.name = name
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

    def activate(self, game_state: GameState):
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

    def _callback(self) -> None:
        print("default callback called")


class ItemCard(Card):

    def __init__(self, suit: Suits, name: str, vp_bonus: int, item_bonus: Items) -> None:
        super().__init__(suit, name, False,
                         f"When crafted, grants the owner +{vp_bonus} victory points and a {item_bonus.name.lower()} item. Then this card is discarded.")
        self.vp_bonus = vp_bonus
        self.item_bonus = item_bonus

    def activate(self, game_state: GameState):
        super().activate(game_state)
        if not self.owner.dominance:
            # Disdain for Trade
            if self.owner.faction_id == Factions.EYRIE_DYNASTY.value and self.owner.eyrie_leader != EyrieLeaders.Builder:
                self.owner.add_vp(1)
            else:
                self.owner.add_vp(self.vp_bonus)
        self.owner.items.append(self.item_bonus)
        CRAFTABLE_ITEMS.remove(self.item_bonus)


class DominanceCard(Card):

    def __init__(self, suit: Suits, name: str) -> None:
        if suit == Suits.BIRD:
            description = "You win the game if you rule two opposite clearings at the start of your birdsong."
        else:
            description = f"You win the game if you rule three {suit.name.lower()} clearings at the start of your birdsong."
        super().__init__(suit, name, False, description)
        self.make_action_adder(CallbackTimes.DOMINANCE_TIME, DominanceAction())

    def activate(self, game_state: GameState):
        super().activate(game_state)
        self.owner.dominance = self.suit
        self.owner.hand.remove(self)


class CommandWarrenCard(Card):
    def __init__(self):
        super().__init__(Suits.RABBIT, "Command Warren", True,
                         "At the start of daylight, may initiate a battle")
        self.make_craftable(rabbit_count=2)
        self.make_action_adder(
            CallbackTimes.DAYLIGHT_START, BattleAction(max_uses=1))

    def activate(self, game_state: GameState):
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


class SappersCard(Card):
    def __init__(self):
        super().__init__(Suits.BIRD, "Sappers", True,
                         "In battle as defender, may discard to deal an extra hit")
        self.make_craftable(mouse_count=1)
        self.make_battle_modifier(BattleCallbackTimes.IN_BATTLE_DEFENDER)

    def _callback(self, battle_modifier: BattleModifier):

        use_card: bool = self.owner.controller.send_game_message(
            BattleUseCardMessage(self)).use_card

        if use_card:
            battle_modifier.defender_damage_modifier += 1
            print(f"Active cards: {self.owner.active_cards}")
            print(f" - {self.owner} played {self.name} to deal an extra hit")
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

    def _callback(self, battle_modifier: BattleModifier):

        use_card: bool = self.owner.controller.send_game_message(
            BattleUseCardMessage(self)).use_card

        if use_card:
            battle_modifier.defender_damage_modifier += 1
            battle_modifier.defender.add_vp(1)
            print(
                f" - {self.owner} played {self.name} to deal an extra hit, {battle_modifier.attacker} gained 1 VP")


class ArmorersCard(Card):
    def __init__(self):
        super().__init__(Suits.BIRD, "Armorers", True,
                         "In battle, may discard this to ignore all rolled hits")
        self.make_craftable(fox_count=1)
        self.make_battle_modifier(BattleCallbackTimes.IN_BATTLE)

    def _callback(self, battle_modifier: BattleModifier):

        use_card: bool = self.owner.controller.send_game_message(
            BattleUseCardMessage(self)).use_card

        if use_card:
            if self.owner.faction_id == battle_modifier.attacker.faction_id:
                battle_modifier.defender_damage_modifier = -999
            elif self.owner.faction_id == battle_modifier.defender.faction_id:
                battle_modifier.attacker_damage_modifier = -999
            self.owner.active_cards.remove(self)
            self.owner.discard_card(self)
            self.owner.battle_callbacks[self.callback_time].remove(
                self._callback)
            print(
                f" - {self.owner} played {self.name} to ignore all hits")


class AmbushCard(Card):

    def __init__(self, suit: Suits, name: str) -> None:
        description = f"At the start of battle in a {suit.name.capitalize()} clearing, defender may play to deal two immediate hits, then discard. Cancel if attacker plays matching ambush."
        super().__init__(suit, name, False, description)
        self.make_battle_modifier(BattleCallbackTimes.BATTLE_START_DEFENDER)

    def _callback(self, battle_modifer: BattleModifier) -> None:

        from cards.cards import SCOUTING_PARTY, SCOUTING_PARTY_2
        if SCOUTING_PARTY in battle_modifer.attacker.active_cards or SCOUTING_PARTY_2 in battle_modifer.attacker.active_cards:
            print(" - Scouting party blocked ambush")
            # Scouting Party blocks ambushes
            return

        print(f" - {battle_modifer.defender} has chosen to Ambush {battle_modifer.attacker} on Clearing {battle_modifer.clearing.index}")
        battle_modifer.defender.discard_card(self)

        available_ambush_cards = [
            card for card in battle_modifer.attacker.hand if isinstance(card, AmbushCard) and (card.suit == battle_modifer.clearing.get_suit() or card.suit == Suits.BIRD)]

        if available_ambush_cards != []:
            ambush_response: AmbushResponse = battle_modifer.attacker.controller.send_game_message(AmbushMessage(
                battle_modifer.attacker, battle_modifer.defender, battle_modifer.clearing, True, True, available_ambush_cards))
            if ambush_response.ambush_card is not None:
                print(
                    f" - {battle_modifer.attacker} Counter-Ambushed using '{ambush_response.ambush_card}'")
                battle_modifer.attacker.discard_card(
                    ambush_response.ambush_card)
                return

        battle_modifer.clearing.damage(
            victim=battle_modifer.attacker, attacker=battle_modifer.defender, amount=2)


class FavourCard(Card):

    def __init__(self, suit: Suits, name: str) -> None:
        description = f"Remove all enemy pieces in {suit.name.lower()} clearings."
        super().__init__(suit, name, False, description)

    def activate(self, game_state: GameState):
        for clearing in game_state.board.clearings:
            if clearing.get_suit() == self.suit:
                self._kill_all_enemies(clearing, game_state)

    def _kill_all_enemies(self, clearing: Clearing, game_state: GameState):
        for faction in game_state.faction_list:
            if faction.faction_id != self.owner.faction_id and clearing.get_faction_piece_count(faction.faction_id) > 0:
                clearing.damage(faction, self.owner, 999)


class BetterBurrowBankCard(Card):
    def __init__(self):
        super().__init__(Suits.RABBIT, "Better Burrow Bank", True,
                         "At start of Birdsong, you and another play draw a card")
        self.make_craftable(rabbit_count=2)
        self.make_action_adder(
            CallbackTimes.BIRDSONG_START, BetterBurrowBankAction())


class StandAndDeliverCard(Card):
    def __init__(self):
        super().__init__(Suits.FOX, "Stand and Deliver", True,
                         "In Birdsong, may take a random card from another player. That player scores one point")
        self.make_craftable(mouse_count=3)
        self.make_action_adder(CallbackTimes.IN_BIRDSONG,
                               StandAndDeliverAction())


class TaxCollectorsCard(Card):
    def __init__(self):
        super().__init__(Suits.FOX, "Tax Collector", True,
                         "Once in Daylight, may remove one of your warriors to draw a card.")
        self.make_craftable(fox_count=1, mouse_count=1, rabbit_count=1)
        self.make_action_adder(CallbackTimes.IN_DAYLIGHT, TaxCollectorAction())


class CodebreakersCard(Card):
    def __init__(self):
        super().__init__(Suits.MOUSE, "Codebreakers", True,
                         "Once in Daylight, may look at another player's hand.")
        self.make_craftable(mouse_count=1)
        self.make_action_adder(CallbackTimes.IN_DAYLIGHT, CodebreakersAction())


class RoyalClaimCard(Card):
    def __init__(self):
        super().__init__(Suits.BIRD, "Royal Claim", True,
                         "In Birdsong, may discard this to score one point per clearing you rule.")
        self.make_craftable(wild_count=4)
        self.make_action_adder(CallbackTimes.IN_BIRDSONG,
                               RoyalClaimAction(self))
