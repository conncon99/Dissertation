from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict, Optional
from factions.faction import Faction
from pieces.woodland_alliance.alliance_tokens import Sympathy
from utils.root_types import Suits
from actions.action_handler import ActionGroup
from pieces.woodland_alliance.alliance_buildings import AllianceBase
from actions.factionless.draw_and_discard_action import DrawAndDiscardAction
from actions.factionless.craft_action import CraftAction
from actions.woodland_alliance.mobilize_action import MobilizeAction
from actions.woodland_alliance.train_action import TrainAction
from actions.woodland_alliance.revolt_action import RevoltAction
from actions.factionless.play_dominance_action import PlayDominanceAction
from actions.woodland_alliance.spread_sympathy_action import SpreadSympathyAction
from actions.woodland_alliance.modify_evening_action_count import ModifyEveningActionCount
from actions.woodland_alliance.organize_action import OrganizeAction
from actions.factionless.move_action import MoveAction
from actions.factionless.battle_action import BattleAction
from actions.woodland_alliance.alliance_recruit_action import AllianceRecruitAction
from controllers.messages.game_messages import TriggererOutrageMessage, AllianceOutrageMessage
from utils.callback_handler import CallbackTimes
from cards.card import Card
from utils.colour_utils import set_print_colour

if TYPE_CHECKING:
    from board.map import Map
    from cards.deck import Deck
    from board.clearing import Clearing
    from utils.game_state import GameState


class WoodlandAlliance(Faction):
    def __init__(self, controller) -> None:
        super().__init__(faction_id=3, reach_value=3,
                         max_warriors=10, controller=controller, print_colour="\033[38;5;82m")
        self.sympathy: List[Sympathy] = []
        self.max_bases = 3
        self.max_sympathy = 10
        self.bases: Dict[Suits, Optional[AllianceBase]] = {
            Suits.FOX: None, Suits.RABBIT: None, Suits.MOUSE: None}
        self.supporters: List[Card] = []
        self.officers: int = 0
        # Number, [Cost, VP reward]
        self.sympathy_track: Dict[int, List[int]] = {
            0: [1, 0], 1: [1, 1], 2: [1, 1], 3: [2, 1], 4: [2, 2], 5: [2, 2], 6: [3, 3], 7: [3, 4], 8: [3, 4], 9: [3, 4]}
        self.actions[CallbackTimes.IN_BIRDSONG] = [
            ActionGroup('Birdsong-1', False, [RevoltAction()], None, can_abort=True), ActionGroup('Birdsong-2', False, [SpreadSympathyAction()], None, can_abort=True)]
        self.actions[CallbackTimes.IN_DAYLIGHT] = [
            ActionGroup('Daylight', False, [PlayDominanceAction(), CraftAction(), MobilizeAction(), TrainAction()], None, True)]
        self.actions[CallbackTimes.IN_EVENING] = [
            ActionGroup('Evening-Officer-Count', False,
                        [ModifyEveningActionCount()], 1),
            ActionGroup('Evening-1', False,
                        [MoveAction(), BattleAction(), AllianceRecruitAction(), OrganizeAction()], self.officers, can_abort=True),
            ActionGroup('Evening-2', False, [DrawAndDiscardAction()], 1)]

    def __repr__(self):
        return "Woodland Alliance"

    def setup_faction(self, map: Map, deck: Deck, game_state: GameState):
        print(f"Setting up {self}")
        self.deck = deck
        self.game_state = game_state
        self.supporters.extend(self.deck.draw(3))
        print(f"- Added 3 Supporters")
        print(f"- Finished {self} Set Up\n")
        yield
        return

    def get_crafting_resources(self):
        crafting_resources = {suit: 0 for suit in Suits}
        for sympathy in self.sympathy:
            crafting_resources[sympathy.get_suit()] += 1
        return crafting_resources

    def get_bonus_card_draws(self):
        return len([base for base in self.bases.values() if base is not None])

    def get_base_count(self) -> int:
        return sum(base is not None for base in self.bases.values())

    def trigger_outrage(self, triggerer: Faction, clearing: Clearing, action_group):
        set_print_colour(self.print_colour)
        print(
            f" - OUTRAGE TRIGGERED by {triggerer} in clearing {clearing.index}")
        chosen_card = None
        # 1. If player has cards matching the suit of the clearing or bird, they can choose which to give to the woodland alliance
        if any(card.suit == Suits.BIRD or card.suit == clearing.get_suit() for card in triggerer.hand):
            valid_cards = [card for card in triggerer.hand if card.suit ==
                           Suits.BIRD or card.suit == clearing.get_suit()]
            chosen_card = triggerer.controller.send_game_message(
                TriggererOutrageMessage(self.game_state, action_group, valid_cards)).chosen_card
            triggerer.hand.remove(chosen_card)
            print(
                f" - {triggerer} has given matching card '{chosen_card}' to The {self}")
        # 2. If the player does not have a matching card, they must show the alliance their hand, and the alliance chooses which card to take
        elif len(triggerer.hand) > 0:
            chosen_card = self.controller.send_game_message(
                AllianceOutrageMessage(self.game_state, action_group, triggerer.hand)).chosen_card
            triggerer.hand.remove(chosen_card)
            print(
                f" - The {self} has taken non-matching card '{chosen_card}' from {triggerer}")
        # 3. If the player has no cards, the alliance draws a card from the deck
        else:
            chosen_card = self.deck.draw(1)
            if chosen_card != []:
                chosen_card = chosen_card[0]
                print(
                    f" - {triggerer} has no cards, drew '{chosen_card}' from the deck")
            else:
                set_print_colour(triggerer.print_colour)
                return

        # 4. Wherever this card comes from, it gets added to the alliance's supporter deck
        self.add_supporter(chosen_card)
        set_print_colour(triggerer.print_colour)

    def add_supporter(self, card: Card):
        if self.get_base_count() > 0 or len(self.supporters) < 5:
            self.supporters.append(card)
        else:
            print(f" - Reached Supporter Limit, unable to add '{card}'")
            self.discard_card(card)
