from __future__ import annotations
from src.actions.action_handler import Action
from src.utils.root_types import Items, Factions
from typing import TYPE_CHECKING
from src.board.clearing import Clearing
from src.controllers.messages.game_messages import StrikeFactionChoiceMessage, StrikePieceTargetingMessage
from src.pieces.woodland_alliance.alliance_buildings import AllianceBase
from src.pieces.woodland_alliance.alliance_tokens import Sympathy
from src.utils.colour_utils import set_print_colour
from src.actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from src.factions.vagabond.vagabond import Vagabond


class StrikeAction(Action):
    def __init__(self, name='Strike', max_uses=None, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.id = ActionIDs.STRIKE

    def can_perform(self, executor: Vagabond, game_state=None):
        return executor.satchel.available_items[Items.CROSSBOW] > 0 and isinstance(executor.vagabond_pawn.space, Clearing) and \
            any(executor.vagabond_pawn.space.get_faction_piece_count(faction.faction_id) !=
                0 and faction.faction_id != executor.faction_id for faction in game_state.faction_list)

    def perform(self, game_state, executor: Vagabond):
        assert isinstance(executor.vagabond_pawn.space, Clearing)
        available_factions = [faction for faction in game_state.faction_list if faction.faction_id !=
                              executor.faction_id and executor.vagabond_pawn.space.get_faction_piece_count(faction.faction_id) > 0]
        # Choose Faction to target
        response = yield StrikeFactionChoiceMessage(game_state, self.action_group, available_factions)
        chosen_faction = response.chosen_faction
        game_state.selected_faction = chosen_faction
        self.logger.info(
            f" - Targeting {chosen_faction} with strike on Clearing {executor.vagabond_pawn.space.index}")

        # If there are no warriors, choose piece to target
        if executor.vagabond_pawn.space.get_faction_warrior_count(chosen_faction.faction_id) == 0:
            available_targets = []
            for slot in executor.vagabond_pawn.space.slots:
                if slot is not None and slot.faction and slot.faction.faction_id == chosen_faction.faction_id:
                    available_targets.append(slot)

            for token in executor.vagabond_pawn.space.tokens[chosen_faction.faction_id]:
                available_targets.append(token)

            response = yield StrikePieceTargetingMessage(game_state, self.action_group, available_targets, chosen_faction)
            chosen_piece = response.chosen_piece
            self.logger.info(
                f" - Destroying Token/Building on Clearing {executor.vagabond_pawn.space.index}")
            if isinstance(chosen_piece, Sympathy) or isinstance(chosen_piece, AllianceBase):
                yield from chosen_piece.destroy(executor, self.action_group)
            else:
                chosen_piece.destroy(executor, self.action_group)
        else:
            self.logger.info(
                f" - Destroying warrior on Clearing {executor.vagabond_pawn.space.index}")
            executor.vagabond_pawn.space.units[chosen_faction.faction_id][0].destroy(
                executor, self.action_group)

            if chosen_faction.faction_id == Factions.MARQUISE_DE_CAT.value and chosen_faction.keep is not None:
                set_print_colour(chosen_faction.print_colour)
                yield from chosen_faction.use_field_hospital(
                    executor.vagabond_pawn.space, 1, self.action_group)
                set_print_colour(executor.print_colour)

        # Exhaust crossbow
        executor.satchel.exhaust_item(Items.CROSSBOW)
        game_state.selected_faction = None
        return super().perform(game_state, executor)
        yield
