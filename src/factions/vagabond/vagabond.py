from __future__ import annotations
from factions.faction import Faction
from typing import List, TYPE_CHECKING, Dict, Optional
from utils.root_types import Items, Suits
from factions.vagabond.satchel import Satchel
from factions.vagabond.quests import QuestCard, QuestDeck
from pieces.vagabond.vagabond_pawn import VagabondPawn
from factions.vagabond.vagabond_characters import Characters
from board.clearing import Clearing
from controllers.messages.game_messages import ChooseCharacterMessage, VagabondPlacementMessage
from factions.vagabond.relationship_track import RelationshipTrack, ALLIED
from utils.callback_handler import CallbackTimes
from actions.action_handler import ActionGroup
from actions.vagabond.slip_action import SlipAction
from actions.vagabond.refresh_action import RefreshAction
from actions.vagabond.vagabond_move_action import VagabondMoveAction
from actions.vagabond.explore_action import ExploreAction
from actions.vagabond.special_action import SpecialAction
from actions.vagabond.quest_action import QuestAction
from actions.vagabond.repair_action import RepairAction
from actions.vagabond.vagabond_craft import VagabondCraft
from actions.factionless.draw_and_discard_action import DrawAndDiscardAction
from actions.vagabond.evenings_rest_action import EveningRestAction
from actions.vagabond.empty_satchel_action import EmptySatchelAction
from actions.vagabond.strike_action import StrikeAction
from actions.vagabond.vagabond_battle_action import VagabondBattleAction
from actions.vagabond.aid_action import AidAction
from actions.factionless.play_dominance_action import PlayDominanceAction

if TYPE_CHECKING:
    from board.map import Map
    from cards.deck import Deck
    from factions.vagabond.vagabond_characters import VagabondCharacter


class Vagabond(Faction):
    def __init__(self, controller):
        super().__init__(faction_id=4, reach_value=5, max_warriors=0,
                         controller=controller, print_colour="\033[38;5;250m")

        self.satchel = Satchel(self)
        self.quest_deck = QuestDeck()
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

    def setup_faction(self, map: Map, deck: Deck):
        print(f"Setting up {self}")
        self.deck = deck

        # 1. Choose Character
        self.character: VagabondCharacter = self.controller.send_game_message(
            ChooseCharacterMessage([character for character in Characters])).chosen_character.value
        print(f" - Chosen {self.character} as Character")

        # 2. Place Pawn in forest
        VagabondPawn(self.controller.send_game_message(
            VagabondPlacementMessage(map.forests)).chosen_forest, self)

        print(
            f" - Placed Vagabond Pawn in Forest {self.vagabond_pawn.space.index}")

        # 3. Get 3 quests
        self.quest_cards.extend(self.quest_deck.draw(3))
        print(f" - Drew quest cards: {self.quest_cards}")

        # 4. Take starting items
        for item in self.character.starting_items:
            self.satchel.add_item(item)
        print(f" - Starting Items: {self.character.starting_items}")

        print(f"- Finished {self} Set Up\n")
        return super().setup_faction(map, deck)

    def get_allied_warriors_in_clearing(self, clearing: Clearing) -> List[Faction]:
        available_allies = []
        for faction in clearing.settings.faction_list:
            if faction.faction_id == self.faction_id or len(clearing.units[faction.faction_id]) == 0:
                continue
            if self.relationship_track.relationship_level[faction.faction_id] == ALLIED:
                available_allies.append(faction)
        return available_allies
