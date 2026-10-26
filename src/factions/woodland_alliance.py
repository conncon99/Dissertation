from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict, Optional
from src.factions.faction import Faction
from src.pieces.woodland_alliance.alliance_tokens import Sympathy
from src.utils.root_types import Suits
from src.actions.action_handler import ActionGroup
from src.pieces.woodland_alliance.alliance_buildings import AllianceBase
from src.actions.factionless.draw_and_discard_action import DrawAndDiscardAction
from src.actions.factionless.craft_action import CraftAction
from src.actions.woodland_alliance.mobilize_action import MobilizeAction
from src.actions.woodland_alliance.train_action import TrainAction
from src.actions.woodland_alliance.revolt_action import RevoltAction
from src.actions.factionless.play_dominance_action import PlayDominanceAction
from src.actions.woodland_alliance.spread_sympathy_action import SpreadSympathyAction
from src.actions.woodland_alliance.modify_evening_action_count import ModifyEveningActionCount
from src.actions.woodland_alliance.organize_action import OrganizeAction
from src.actions.factionless.move_action import MoveAction
from src.actions.factionless.battle_action import BattleAction
from src.actions.woodland_alliance.alliance_recruit_action import AllianceRecruitAction
from src.controllers.messages.game_messages import TriggererOutrageMessage, AllianceOutrageMessage
from src.utils.callback_handler import CallbackTimes
from src.cards.card import Card
from src.utils.colour_utils import set_print_colour

if TYPE_CHECKING:
    from src.board.map import Map
    from src.cards.deck import Deck
    from src.board.clearing import Clearing
    from src.utils.game_state import GameState


class WoodlandAlliance(Faction):
    def __init__(self, controller) -> None:
        super().__init__(faction_id=3, reach_value=3, setup_order=2,
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
        self.logger.info(f"Setting up {self}")
        self.deck = deck
        self.game_state = game_state
        self.supporters.extend(self.deck.draw(3))
        self.logger.info(f"- Added 3 Supporters")
        self.logger.info(f"- Finished {self} Set Up\n")
        return
        yield

    def get_crafting_resources(self):
        crafting_resources = {suit: 0 for suit in Suits}
        for sympathy in self.sympathy:
            crafting_resources[sympathy.get_suit()] += 1
        return crafting_resources

    def get_bonus_card_draws(self):
        return len([base for base in self.bases.values() if base is not None])

    def get_base_count(self) -> int:
        return sum(base is not None for base in self.bases.values())

    def trigger_outrage(self, triggerer: Faction, clearing: Clearing, action_group, game_state: GameState):
        set_print_colour(self.print_colour)
        self.logger.info(
            f" - OUTRAGE TRIGGERED by {triggerer} in clearing {clearing.index}")
        chosen_card = None
        # 1. If player has cards matching the suit of the clearing or bird, they can choose which to give to the woodland alliance
        if any(card.suit == Suits.BIRD or card.suit == clearing.get_suit() for card in triggerer.hand):
            valid_cards = [card for card in triggerer.hand if card.suit ==
                           Suits.BIRD or card.suit == clearing.get_suit()]
            game_state.active_player = triggerer
            response = yield TriggererOutrageMessage(self.game_state, action_group, valid_cards)
            chosen_card = response.chosen_card
            game_state.active_player = game_state.current_player
            triggerer.hand.remove(chosen_card)
            self.logger.info(
                f" - {triggerer} has given matching card '{chosen_card}' to The {self}")
        # 2. If the player does not have a matching card, they must show the alliance their hand, and the alliance chooses which card to take
        elif len(triggerer.hand) > 0:
            game_state.active_player = self
            response = yield AllianceOutrageMessage(self.game_state, action_group, triggerer.hand)
            chosen_card = response.chosen_card
            triggerer.hand.remove(chosen_card)
            self.logger.info(
                f" - The {self} has taken non-matching card '{chosen_card}' from {triggerer}")
            game_state.active_player = triggerer
        # 3. If the player has no cards, the alliance draws a card from the deck
        else:
            chosen_card = self.deck.draw(1)
            if chosen_card != []:
                chosen_card = chosen_card[0]
                self.logger.info(
                    f" - {triggerer} has no cards, drew '{chosen_card}' from the deck")
            else:
                set_print_colour(triggerer.print_colour)
                return
                yield

        # 4. Wherever this card comes from, it gets added to the alliance's supporter deck
        self.add_supporter(chosen_card)
        set_print_colour(triggerer.print_colour)
        return
        yield

    def add_supporter(self, card: Card):
        if self.get_base_count() > 0 or len(self.supporters) < 5:
            self.supporters.append(card)
        else:
            self.logger.info(
                f" - Reached Supporter Limit, unable to add '{card}'")
            self.discard_card(card)

    def get_potential_vp(self, game_state):
        potential_vp = 0
        potentially_placed = 0

        # NOTE: Innacurate as it does not take into account the clearings where we place potential sympathy

        available_clearings = []
        for token in self.sympathy:
            available_clearings.extend(token.space.adjacent_clearings)

        if available_clearings == []:
            return 1 + super().get_potential_vp(game_state)

        available_clearings = list(set(available_clearings))

        remaining_supporters = self.supporters[:]
        for clearing in available_clearings:
            # Can't place any more sympathy
            if len(clearing.tokens[self.faction_id]) > 0 or len(self.sympathy) + potentially_placed >= self.max_sympathy:
                continue

            cost = self.sympathy_track[len(
                self.sympathy) + potentially_placed][0]
            for faction in game_state.faction_list:
                if faction.faction_id == self.faction_id:
                    continue
                if clearing.get_faction_warrior_count(faction.faction_id) > 3:
                    cost += 1
                    break
            total = 0
            used_cards = []
            for card in remaining_supporters:
                if card.suit == Suits.BIRD or card.suit == clearing.get_suit():
                    total += 1
                    used_cards.append(card)
                if total == cost:
                    potential_vp += self.sympathy_track[len(
                        self.sympathy) + potentially_placed][1]
                    potentially_placed += 1
                    break
            for card in used_cards:
                remaining_supporters.remove(card)

        return potential_vp + super().get_potential_vp(game_state)
