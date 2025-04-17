from __future__ import annotations
from src.factions.faction import Faction
from typing import List, TYPE_CHECKING, Dict, Optional
from src.utils.root_types import Items, Suits
from src.factions.vagabond.satchel import Satchel
from src.factions.vagabond.quests import QuestCard, QuestDeck
from src.pieces.vagabond.vagabond_pawn import VagabondPawn
from src.factions.vagabond.vagabond_characters import Characters
from src.board.clearing import Clearing
from src.controllers.messages.game_messages import ChooseCharacterMessage, VagabondPlacementMessage
from src.factions.vagabond.relationship_track import RelationshipTrack, ALLIED
from src.utils.callback_handler import CallbackTimes
from src.actions.action_handler import ActionGroup
from src.actions.vagabond.slip_action import SlipAction
from src.actions.vagabond.refresh_action import RefreshAction
from src.actions.vagabond.vagabond_move_action import VagabondMoveAction
from src.actions.vagabond.explore_action import ExploreAction
from src.actions.vagabond.special_action import SpecialAction
from src.actions.vagabond.quest_action import QuestAction
from src.actions.vagabond.repair_action import RepairAction
from src.actions.vagabond.vagabond_craft import VagabondCraft
from src.actions.factionless.draw_and_discard_action import DrawAndDiscardAction
from src.actions.vagabond.evenings_rest_action import EveningRestAction
from src.actions.vagabond.empty_satchel_action import EmptySatchelAction
from src.actions.vagabond.strike_action import StrikeAction
from src.actions.vagabond.vagabond_battle_action import VagabondBattleAction
from src.actions.vagabond.aid_action import AidAction
from src.actions.factionless.play_dominance_action import PlayDominanceAction
import logging

if TYPE_CHECKING:
    from src.board.map import Map
    from src.cards.deck import Deck
    from src.factions.vagabond.vagabond_characters import VagabondCharacter
    from src.utils.game_state import GameState


class Vagabond(Faction):
    def __init__(self, controller, use_manual_card_draw=False):
        super().__init__(faction_id=4, reach_value=5, max_warriors=0, setup_order=3,
                         controller=controller, print_colour="\033[38;5;250m")

        self.satchel = Satchel(self)
        self.quest_deck = QuestDeck(use_manual_card_draw)
        self.quest_cards: List[QuestCard] = []
        self.character: VagabondCharacter = None
        self.relationship_track = RelationshipTrack(self)
        self.vagabond_pawn: VagabondPawn = None
        self.active_tea_count: int = 0
        self.active_coin_count: int = 0
        self.active_bag_count: int = 0
        self.max_track_count: int = 3
        self.battle_ally: Optional[Faction] = None

        self.completed_quests: Dict[Suits, int] = {
            suit: 0 for suit in Suits if suit != Suits.BIRD}

        self.actions[CallbackTimes.IN_BIRDSONG] = [ActionGroup('Birdsong-1', False, [RefreshAction()], 1),
                                                   ActionGroup('Birdsong-2', False, [SlipAction()], 1, can_abort=True)]

        self.actions[CallbackTimes.IN_DAYLIGHT] = [
            ActionGroup('Daylight', False, [VagabondMoveAction(), VagabondBattleAction(), ExploreAction(), AidAction(), RepairAction(), StrikeAction(), VagabondCraft(), SpecialAction(), QuestAction(), PlayDominanceAction()], None, can_abort=True)]

        self.actions[CallbackTimes.IN_EVENING] = [
            ActionGroup('Evening-1', False, [EveningRestAction()], 1),
            ActionGroup('Evening-2', False, [DrawAndDiscardAction()], 1),
            ActionGroup('Evening-3', False, [EmptySatchelAction()], 1)]

    def __repr__(self):
        return "Vagabond"

    def get_bonus_card_draws(self):
        return self.active_coin_count

    def get_crafting_resources(self):
        crafting_resources = {suit: 0 for suit in Suits}
        if isinstance(self.vagabond_pawn.space, Clearing):
            crafting_resources[self.vagabond_pawn.space.get_suit(
            )] += self.satchel.available_items[Items.HAMMER]
        return crafting_resources

    def setup_faction(self, map: Map, deck: Deck, game_state: GameState):
        self.logger.info(f"Setting up {self}")
        self.deck = deck
        self.game_state = game_state

        # 1. Choose Character
        response = yield ChooseCharacterMessage(game_state, None, [character for character in Characters])
        self.character: VagabondCharacter = response.chosen_character.value
        self.logger.info(f" - Chosen {self.character} as Character")

        # 2. Place Pawn in forest
        response = yield VagabondPlacementMessage(game_state, None, map.forests)
        VagabondPawn(response.chosen_forest, self)

        self.logger.info(
            f" - Placed Vagabond Pawn in Forest {self.vagabond_pawn.space.index}")

        # 3. Get 3 quests
        self.quest_cards.extend(self.quest_deck.draw(3))
        self.logger.info(f" - Drew quest cards: {self.quest_cards}")

        # 4. Take starting items
        for item in self.character.starting_items:
            self.satchel.add_item(item)
        self.logger.info(f" - Starting Items: {self.character.starting_items}")

        self.logger.info(f"- Finished {self} Set Up\n")

    def get_allied_warriors_in_clearing(self, clearing: Clearing) -> List[Faction]:
        available_allies = []
        for faction in clearing.game_state.faction_list:
            if faction.faction_id == self.faction_id or len(clearing.units[faction.faction_id]) == 0:
                continue
            if self.relationship_track.relationship_level[faction.faction_id] == ALLIED:
                available_allies.append(faction)
        return available_allies
