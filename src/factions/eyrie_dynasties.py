from __future__ import annotations
from factions.faction import Faction
from typing import Dict, List, TYPE_CHECKING
from pieces.eyrie_dynasties.eyrie_buildings import Roost
from utils.root_types import Suits, RECRUIT, MOVE, BATTLE, BUILD, EyrieLeaders
from utils.callback_handler import CallbackTimes
from actions.action_handler import ActionGroup
from actions.factionless.craft_action import CraftAction
from actions.factionless.draw_and_discard_action import DrawAndDiscardAction
from actions.eyrie_dynasties.score_vp_action import ScoreVpAction
from actions.eyrie_dynasties.replenish_hand_action import ReplenishHandAction
from actions.eyrie_dynasties.extend_decree_action import ExtendDecreeAction
from actions.eyrie_dynasties.roostless_action import RoostlessAction
from actions.eyrie_dynasties.decree_recruit_action import DecreeRecruitAction
from actions.eyrie_dynasties.decree_battle_action import DecreeBattleAction
from actions.eyrie_dynasties.decree_move_action import DecreeMoveAction
from actions.eyrie_dynasties.decree_build_action import DecreeBuildAction
from actions.factionless.play_dominance_action import PlayDominanceAction
from controllers.messages.game_messages import RoostSetupMessage, LeaderSetupMessage, TurmoilLeaderMessage
from board.map import Map
from pieces.pawn import Pawn
from enum import Enum
from cards.cards import ROYAL_VIZIER_1, ROYAL_VIZIER_2

if TYPE_CHECKING:
    from cards.card import Card
    from cards.deck import Deck
    from actions.action_handler import Action
    from utils.game_state import GameState


class EyrieDynasties(Faction):

    def __init__(self, controller):
        super().__init__(faction_id=2, reach_value=7,
                         max_warriors=20, controller=controller, print_colour="\033[38;5;19m")
        self.max_roosts: int = 7
        # Number of roosts, VP reward
        self.roost_track: Dict[int, int] = {
            0: 0, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 4, 7: 5}
        self.decree_cards: Dict[int, List[Card]] = {
            RECRUIT: [], MOVE: [], BATTLE: [], BUILD: []}
        self.roosts: List[Roost] = []
        self.eyrie_leader: EyrieLeaders = None
        self.gained_despot_bonus = False
        self.remaining_leaders: List[EyrieLeaders] = [
            leader for leader in EyrieLeaders]
        self.actions[CallbackTimes.IN_DAYLIGHT] = [
            ActionGroup("Daylight-Craft",
                        actions=[CraftAction(), PlayDominanceAction()], can_abort=True),
            ActionGroup("Daylight-Decree-Recruit", ordered=True, actions=[]),
            ActionGroup("Daylight-Decree-Move", ordered=True, actions=[]),
            ActionGroup("Daylight-Decree-Battle", ordered=True, actions=[]),
            ActionGroup("Daylight-Decree-Build", ordered=True, actions=[]),
            ActionGroup("Daylight-End", False, [PlayDominanceAction()], 1, can_abort=True)]
        self.actions[CallbackTimes.IN_BIRDSONG] = [ActionGroup(
            "Birdsong", ordered=True, actions=[ReplenishHandAction(), ExtendDecreeAction(), RoostlessAction()])]
        self.actions[CallbackTimes.IN_EVENING] = [
            ActionGroup("Evening", actions=[ScoreVpAction(), DrawAndDiscardAction()], ordered=True)]

    def __repr__(self):
        return "Eyrie Dynasties"

    def setup_faction(self, map: Map, deck: Deck, game_state: GameState):
        print(f"Setting up {self}")
        self.deck = deck
        self.game_state = game_state

        # 1. Place 1 Roost and 6 warriors in a corner clearing that is not occupied by another player, and if possible, is diagonally opposite from a starting corner

        free_corner_clearings = [
            clearing for clearing in map.corner_clearings if all(slot is None or slot.faction.faction_id == self.faction_id for slot in clearing.slots) and all(token_list == [] for token_list in clearing.tokens.values())]

        preferred_corner_clearings = [clearing for clearing in free_corner_clearings if map.get_opposite_corner(
            clearing) not in free_corner_clearings]

        start_clearing_options = preferred_corner_clearings if preferred_corner_clearings else free_corner_clearings

        start_clearing = self.controller.send_game_message(
            RoostSetupMessage(game_state, None, start_clearing_options)).chosen_clearing

        roost = Roost(start_clearing, self,
                      start_clearing.get_first_free_slot())
        for _ in range(6):
            Pawn(start_clearing, self)

        print(
            f"- Placed a {roost} and 6 warriors in clearing {start_clearing.index}")

        # 2. Choose leader

        self.eyrie_leader = self.controller.send_game_message(
            LeaderSetupMessage(game_state, None, self.remaining_leaders)).chosen_leader
        self.remaining_leaders.remove(self.eyrie_leader)
        print(
            f"- Selected {self.eyrie_leader.name} as leader of the Eyrie Dynasties")

        # 3. Tuck Viziers
        print("- Assigning Viziers")
        self.assign_leader_viziers()

        print(f"- Finished {self} Set Up\n")

    def get_crafting_resources(self):
        crafting_resources = {suit: 0 for suit in Suits}
        for roost in self.roosts:
            crafting_resources[roost.get_suit()] += 1
        return crafting_resources

    def get_bonus_card_draws(self):
        if len(self.roosts) == 3:
            return 1
        elif len(self.roosts) == 6:
            return 2
        return 0

    def add_card_to_decree(self, card: Card, decree_type: int):
        self.decree_cards[decree_type].append(card)

        decree_action_dict: Dict[int, Action] = {
            RECRUIT: DecreeRecruitAction, MOVE: DecreeMoveAction, BATTLE: DecreeBattleAction, BUILD: DecreeBuildAction}
        self.actions[CallbackTimes.IN_DAYLIGHT][decree_type].actions.append(
            decree_action_dict[decree_type](card.suit))
        if card in self.hand:
            self.hand.remove(card)
        decree_name_dict = {MOVE: "Move", RECRUIT: "Recruit",
                            BATTLE: "Battle", BUILD: "Build"}
        print(
            f" - {card} with suit {card.suit.name.capitalize()} added to {decree_name_dict[decree_type]} decree")

    def assign_leader_viziers(self):
        self.add_card_to_decree(ROYAL_VIZIER_1, self.eyrie_leader.vizier_1)
        self.add_card_to_decree(ROYAL_VIZIER_2, self.eyrie_leader.vizier_2)

    def trigger_turmoil(self, action_group):
        # 1. Humiliate - Lose 1 VP per bird card on Decree
        # 2. Purge - Discard Decree
        victory_points_removed = 0
        for action_type, cards in self.decree_cards.items():
            for card in cards:
                if card.suit == Suits.BIRD:
                    victory_points_removed += 1
                if card != ROYAL_VIZIER_1 and card != ROYAL_VIZIER_2:
                    self.discard_card(card)
        self.decree_cards: Dict[int, List[Card]] = {
            RECRUIT: [], MOVE: [], BATTLE: [], BUILD: []}
        self.subtract_vp(victory_points_removed)
        if self.victory_points < 0:
            self.victory_points = 0
        print(
            f" - Discarded decree and lost {victory_points_removed} victory points")

        # 3. Depose - Choose a new leader and re-assign viziers - if there are no available leaders, they all become available
        if not self.remaining_leaders:
            self.remaining_leaders = [leader for leader in EyrieLeaders]

        self.eyrie_leader: EyrieLeaders = self.controller.send_game_message(
            TurmoilLeaderMessage(self.game_state, action_group, self.remaining_leaders)).chosen_leader
        print(
            f" - Chose {self.eyrie_leader.name.capitalize()} as new eyrie leader")
        self.assign_leader_viziers()

        # 4. End Daylight immediately and begin evening
        for action_group in self.actions[CallbackTimes.IN_DAYLIGHT][1:]:
            action_group.cancel_action_group()
