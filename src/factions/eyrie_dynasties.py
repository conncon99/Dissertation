from __future__ import annotations
from src.factions.faction import Faction
from typing import Dict, List, TYPE_CHECKING
from src.pieces.eyrie_dynasties.eyrie_buildings import Roost
from src.utils.root_types import Suits, RECRUIT, MOVE, BATTLE, BUILD, EyrieLeaders
from src.utils.callback_handler import CallbackTimes
from src.actions.action_handler import ActionGroup
from src.actions.factionless.craft_action import CraftAction
from src.actions.factionless.draw_and_discard_action import DrawAndDiscardAction
from src.actions.eyrie_dynasties.score_vp_action import ScoreVpAction
from src.actions.eyrie_dynasties.replenish_hand_action import ReplenishHandAction
from src.actions.eyrie_dynasties.extend_decree_action import ExtendDecreeAction
from src.actions.eyrie_dynasties.roostless_action import RoostlessAction
from src.actions.eyrie_dynasties.decree_recruit_action import DecreeRecruitAction
from src.actions.eyrie_dynasties.decree_battle_action import DecreeBattleAction
from src.actions.eyrie_dynasties.decree_move_action import DecreeMoveAction
from src.actions.eyrie_dynasties.decree_build_action import DecreeBuildAction
from src.actions.factionless.play_dominance_action import PlayDominanceAction
from src.controllers.messages.game_messages import RoostSetupMessage, LeaderSetupMessage, TurmoilLeaderMessage
from src.board.map import Map
from src.board.clearing import Clearing
from src.pieces.pawn import Pawn
from enum import Enum
from src.cards.cards import ROYAL_VIZIER_1, ROYAL_VIZIER_2

if TYPE_CHECKING:
    from src.cards.card import Card
    from src.cards.deck import Deck
    from src.actions.action_handler import Action
    from src.utils.game_state import GameState


class EyrieDynasties(Faction):

    def __init__(self, controller):
        super().__init__(faction_id=2, reach_value=7, setup_order=1,
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
        self.logger.info(f"Setting up {self}")
        self.deck = deck
        self.game_state = game_state

        # 1. Place 1 Roost and 6 warriors in a corner clearing that is not occupied by another player, and if possible, is diagonally opposite from a starting corner

        free_corner_clearings = [
            clearing for clearing in map.corner_clearings if all(slot is None or slot.faction.faction_id == self.faction_id for slot in clearing.slots) and all(token_list == [] for token_list in clearing.tokens.values())]

        preferred_corner_clearings = [clearing for clearing in free_corner_clearings if map.get_opposite_corner(
            clearing) not in free_corner_clearings]

        start_clearing_options = preferred_corner_clearings if preferred_corner_clearings else free_corner_clearings
        response = yield RoostSetupMessage(game_state, None, start_clearing_options)
        start_clearing = response.chosen_clearing

        roost = Roost(start_clearing, self,
                      start_clearing.get_first_free_slot())
        for _ in range(6):
            Pawn(start_clearing, self)

        self.logger.info(
            f"- Placed a {roost} and 6 warriors in clearing {start_clearing.index}")

        # 2. Choose leader
        response = yield LeaderSetupMessage(game_state, None, self.remaining_leaders)
        self.eyrie_leader = response.chosen_leader
        self.remaining_leaders.remove(self.eyrie_leader)
        self.logger.info(
            f"- Selected {self.eyrie_leader.name} as leader of the Eyrie Dynasties")

        # 3. Tuck Viziers
        self.logger.info("- Assigning Viziers")
        self.assign_leader_viziers()

        self.logger.info(f"- Finished {self} Set Up\n")
        return

    def get_crafting_resources(self):
        crafting_resources = {suit: 0 for suit in Suits}
        for roost in self.roosts:
            crafting_resources[roost.get_suit()] += 1
        return crafting_resources

    def get_bonus_card_draws(self):
        # One card per uncovered draw bonus: uncovered once 3 and 6 roosts are on the map
        return (1 if len(self.roosts) >= 3 else 0) + (1 if len(self.roosts) >= 6 else 0)

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
        self.logger.info(
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
        # The decree actions of the purged cards (and the old viziers) are removed too
        for decree_type in (RECRUIT, MOVE, BATTLE, BUILD):
            self.actions[CallbackTimes.IN_DAYLIGHT][decree_type].actions.clear()
        self.subtract_vp(victory_points_removed)
        if self.victory_points < 0:
            self.victory_points = 0
        self.logger.info(
            f" - Discarded decree and lost {victory_points_removed} victory points")

        # 3. Depose - The current leader is set aside face down, then a new leader is chosen from those face up and the
        #    viziers are re-assigned. If there are no face up leaders, they all flip face up (7.7.3)
        if not self.remaining_leaders:
            self.remaining_leaders = [leader for leader in EyrieLeaders]

        response = yield TurmoilLeaderMessage(self.game_state, action_group, self.remaining_leaders)
        self.eyrie_leader: EyrieLeaders = response.chosen_leader
        self.remaining_leaders.remove(self.eyrie_leader)
        self.logger.info(
            f" - Chose {self.eyrie_leader.name.capitalize()} as new eyrie leader")
        self.assign_leader_viziers()

        # 4. End Daylight immediately and begin evening
        for action_group in self.actions[CallbackTimes.IN_DAYLIGHT][1:]:
            action_group.cancel_action_group()

    def get_potential_vp(self, game_state):
        potential_vp = 0

        # Decree Availability Potential Rewards
        available_clearings = []
        roostless_clearings = []
        fighting_clearings = []
        for warrior in self.units:
            assert isinstance(warrior.space, Clearing)
            # Number of available clearings to move to
            available_clearings.extend(warrior.space.adjacent_clearings)
            # Number of ruled clearings without a roost
            if warrior.space.get_owner() == self.faction_id and not any(slot and slot.name == "Roost" for slot in warrior.space.slots) and warrior.space not in roostless_clearings:
                roostless_clearings.append(warrior.space)

            for faction in game_state.faction_list:
                if faction.faction_id == self.faction_id:
                    continue
                # Number of clearings occupied with other factions in them
                if warrior.space.get_faction_piece_count(faction.faction_id) > 0 and warrior.space not in fighting_clearings:
                    fighting_clearings.append(warrior.space)

        available_clearings = list(set(available_clearings))

        potential_vp += len(available_clearings) * 0.5
        potential_vp += len(roostless_clearings) * 0.5
        potential_vp += len(fighting_clearings) * 0.5

        # Suit Diversity Rewards

        def suit_diversity_bonus(clearings): return len(
            set(c.get_suit() for c in clearings))

        potential_vp += suit_diversity_bonus(available_clearings)
        potential_vp += suit_diversity_bonus(roostless_clearings)
        potential_vp += suit_diversity_bonus(fighting_clearings)

        # Decree Length Rewards

        potential_vp += len(self.decree_cards[BUILD]) + len(self.decree_cards[BATTLE]) + len(
            self.decree_cards[MOVE]) + len(self.decree_cards[RECRUIT])

        return potential_vp + super().get_potential_vp(game_state)
