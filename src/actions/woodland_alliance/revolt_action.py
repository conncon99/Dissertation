from __future__ import annotations
from src.actions.action_handler import Action
from typing import TYPE_CHECKING, List
from src.pieces.pawn import Pawn
from src.pieces.woodland_alliance.alliance_buildings import AllianceBase
from src.controllers.messages.game_messages import RevoltClearingMessage, RevoltDiscardMessage
from src.utils.colour_utils import set_print_colour
from src.utils.root_types import Suits, Factions
from src.pieces.marquise_de_cat.marquise_tokens import Keep
from src.actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from src.factions.woodland_alliance import WoodlandAlliance
    from src.utils.game_state import GameState
    from src.board.clearing import Clearing
    from src.cards.card import Card


class RevoltAction(Action):
    def __init__(self, name="Revolt", max_uses=None, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.id = ActionIDs.REVOLT

    def can_perform(self, executor: WoodlandAlliance, game_state=None):
        return self.get_valid_clearings(executor) and super().can_perform(executor, game_state)

    def get_valid_clearings(self, executor: WoodlandAlliance):
        valid_clearings = []
        for sympathy in executor.sympathy:
            sympathetic_clearing: Clearing = sympathy.space
            if executor.bases[sympathetic_clearing.get_suit()] is not None:
                continue
            total = 0
            for card in executor.supporters:
                if sympathetic_clearing.get_suit() == card.suit or card.suit == Suits.BIRD:
                    total += 1
                if total >= 2:
                    valid_clearings.append(sympathetic_clearing)
                    break
        return valid_clearings

    def get_matching_sympathy_count(self, suit: Suits, executor: WoodlandAlliance):
        total = 0
        for sympathy in executor.sympathy:
            sympathetic_clearing: Clearing = sympathy.space
            if sympathetic_clearing.get_suit() == suit:
                total += 1
        return total

    def get_valid_supporters(self, executor: WoodlandAlliance, clearing: Clearing):
        return [supporter for supporter in executor.supporters if supporter.suit == clearing.get_suit() or supporter.suit == Suits.BIRD]

    def perform(self, game_state: GameState, executor: WoodlandAlliance):
        # 1. Choose a valid clearing and discard two matching supporters
        valid_clearings = self.get_valid_clearings(executor)
        response = yield RevoltClearingMessage(game_state, self.action_group, valid_clearings)
        clearing: Clearing = response.chosen_clearing

        self.logger.info(f" - Revolted on clearing {clearing.index}")

        for i in range(2):
            valid_supporters = self.get_valid_supporters(executor, clearing)
            response = yield RevoltDiscardMessage(game_state, self.action_group, valid_supporters)
            chosen_discard = response.chosen_discard
            executor.discard_card(chosen_discard)
            executor.supporters.remove(chosen_discard)

            # 2. Remove all enemy pieces there
        for faction in game_state.faction_list:
            if faction.faction_id == executor.faction_id:
                continue
            yield from clearing.damage(faction, executor, 999, self.logger, self.action_group)

        set_print_colour(executor.print_colour)

        # 3. Place matching base and warriors there equal to total number of matching sympathetic clearings
        AllianceBase(clearing.get_suit(), clearing, executor,
                     clearing.get_first_free_slot())
        warriors_placed = 0
        if not any(isinstance(token, Keep) for token in clearing.tokens[Factions.MARQUISE_DE_CAT.value]):
            for _ in range(self.get_matching_sympathy_count(clearing.get_suit(), executor)):
                if len(executor.units) + executor.officers < executor.max_warriors:
                    Pawn(clearing, executor)
                    warriors_placed += 1
        self.logger.info(
            f" - Placed {warriors_placed} warriors on clearing {clearing.index}")

        # 4. Place a warrior in the officers box
        if len(executor.units) + executor.officers < executor.max_warriors:
            executor.officers += 1
            self.logger.info(
                f" - Increased Officer Count to {executor.officers}")

        return super().perform(game_state, executor)
