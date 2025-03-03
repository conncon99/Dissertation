from __future__ import annotations
from controllers.base_controllers.vagabond_controller import VagabondController
from controllers.messages.game_messages import *
from controllers.messages.controller_messages import *
from utils.root_types import Items

from typing import TYPE_CHECKING

import random

if TYPE_CHECKING:
    from board.clearing import Clearing


class VagabondRandomController(VagabondController):

    def __init__(self) -> None:
        """A dummy controller that chooses all its options randomly"""
        super().__init__()

    def _handle_ambushes(self, msg: AmbushMessage) -> AmbushResponse:
        msg.available_ambush_cards.append(None)
        return AmbushResponse(random.choice(msg.available_ambush_cards))

    def _handle_battle_end(self, msg: BattleEndMessage):
        return super()._handle_battle_end(msg)

    def _handle_piece_targeting(self, msg: PieceTargetingMessage) -> PieceTargetingResponse:
        return PieceTargetingResponse(random.sample(msg.targets, msg.remaining_dmg))

    def _handle_movement(self, msg: MoveMessage) -> MoveResponse:
        move_choice_idx = random.randint(0, len(msg.available_moves) - 1)
        from_clearing, to_clearing, all_units = msg.available_moves[move_choice_idx]
        if len(all_units) == 1:
            units = all_units
        else:
            units = random.sample(
                all_units, random.randint(1, len(all_units)))
        return MoveResponse(from_clearing, to_clearing, units)

    def _handle_crafting(self, msg: CraftMessage) -> CraftResponse:
        return CraftResponse(random.choice(msg.crafting_options))

    def _handle_action_choice(self, msg: ActionChoiceMessage) -> ActionChoiceResponse:
        return ActionChoiceResponse(random.choice(msg.available_actions))

    def _handle_battle_clearing_choice(self, msg: BattleClearingChoiceMessage) -> BattleClearingResponse:
        return BattleClearingResponse(random.choice(msg.available_clearings))

    def _handle_better_burrow_bank(self, msg: BetterBurrowBankMessage) -> BetterBurrowBankResponse:
        return BetterBurrowBankResponse(random.choice(msg.available_players))

    def _handle_battle_card_message(self, msg: BattleUseCardMessage) -> BattleUseCardResponse:
        return BattleUseCardResponse(random.choice([True, False]))

    def _handle_dominance_choice(self, msg: ChooseDominanceMessage) -> ChooseDominanceResponse:
        return ChooseDominanceResponse(random.choice(msg.available_cards))

    def _handle_battle_target_choice(self, msg: BattleTargetChoiceMessage) -> BattleTargetResponse:
        return BattleTargetResponse(random.choice(msg.battle_target_list))

    def _handle_discard_choice(self, msg: DiscardChoiceMessage) -> DiscardChoiceResponse:
        return DiscardChoiceResponse(random.sample(msg.discard_options, msg.num_to_discard))

    def _handle_triggerer_outrage_message(self, msg: TriggererOutrageMessage) -> TriggererOutrageResponse:
        return TriggererOutrageResponse(random.choice(msg.valid_cards))

    # Vagabond Controller

    def _handle_choose_character(self, msg: ChooseCharacterMessage) -> ChooseCharacterResponse:
        return ChooseCharacterResponse(random.choice(msg.available_characters))

    def _handle_vagabond_placement(self, msg: VagabondPlacementMessage) -> VagabondPlacementResponse:
        return VagabondPlacementResponse(random.choice(msg.available_forests))

    def _handle_ranger_repair(self, msg: RangerRepairMessage) -> RangerRepairResponse:
        if msg.available_damaged and msg.exhausted_damaged:
            is_exhausted = random.choice([True, False])
        else:
            is_exhausted = msg.exhausted_damaged != []

        chosen_item = random.choice(
            msg.exhausted_damaged) if is_exhausted else random.choice(msg.available_damaged)
        return RangerRepairResponse(chosen_item, is_exhausted)

    def _handle_tinker_card(self, msg: TinkerCardMessage) -> TinkerCardResponse:
        return TinkerCardResponse(random.choice(msg.available_cards))

    def _handle_thief_steal(self, msg: ThiefStealMessage) -> ThiefStealResponse:
        return ThiefStealResponse(random.choice(msg.available_players))

    def _handle_slip_space(self, msg: SlipMessage) -> SlipResponse:
        return SlipResponse(random.choice(msg.available_spaces))

    def _handle_refresh_item(self, msg: RefreshItemMessage) -> RefreshItemResponse:
        if msg.damaged_items and msg.undamaged_items:
            is_damaged = random.choice([True, False])
        else:
            is_damaged = msg.damaged_items != []

        chosen_item = random.choice(
            msg.damaged_items) if is_damaged else random.choice(msg.undamaged_items)
        return RefreshItemResponse(is_damaged, chosen_item)

    def _handle_vagabond_move(self, msg: VagabondMoveMessage) -> VagabondMoveResponse:
        clearing_list = list(msg.clearing_dict.keys())
        return VagabondMoveResponse(random.choice(clearing_list))

    def _handle_choose_quest(self, msg: ChooseQuestMessage) -> ChooseQuestResponse:
        return ChooseQuestResponse(random.choice(msg.available_quests))

    def _handle_choose_quest_reward(self, msg: ChooseQuestRewardMessage) -> ChooseQuestRewardResponse:
        return ChooseQuestRewardResponse(random.choice([True, False]))

    def _handle_repair_item(self, msg: RepairItemMessage) -> RepairItemResponse:
        if msg.available_damaged and msg.exhausted_damaged:
            is_exhausted = random.choice([True, False])
        else:
            is_exhausted = msg.exhausted_damaged != []

        chosen_item = random.choice(
            msg.exhausted_damaged) if is_exhausted else random.choice(msg.available_damaged)
        return RepairItemResponse(is_exhausted, chosen_item)

    def _handle_empty_satchel(self, msg: EmptySatchelMessage) -> EmptySatchelResponse:
        print(f"ed: {len(msg.exhausted_damaged_items)} , e: {len(msg.exhausted_items)}, ad: {len(msg.available_damaged_items)}, a: {len(msg.available_items)}")

        exhausted_options = [msg.exhausted_items != []
                             or msg.exhausted_damaged_items != [], not (msg.available_items != [] or msg.available_damaged_items != [])]
        damaged_options = [msg.available_damaged_items !=
                           [] or msg.exhausted_damaged_items != [], not (msg.available_items != [] or msg.exhausted_items != [])]

        can_be_both = msg.exhausted_damaged_items != []
        can_be_neither = msg.available_items != []

        is_exhausted = random.choice(exhausted_options)
        if not can_be_both and is_exhausted:
            is_damaged = False
        elif not can_be_neither and not is_exhausted:
            is_damaged = True
        else:
            is_damaged = random.choice(damaged_options)

        if is_exhausted and is_damaged:
            chosen_item = random.choice(msg.exhausted_damaged_items)
        elif is_exhausted:
            chosen_item = random.choice(msg.exhausted_items)
        elif is_damaged:
            chosen_item = random.choice(msg.available_damaged_items)
        else:
            chosen_item = random.choice(msg.available_items)

        return EmptySatchelResponse(chosen_item, is_damaged, is_exhausted)

    def _handle_strike_faction_choice(self, msg: StrikeFactionChoiceMessage) -> StrikeFactionChoiceResponse:
        return StrikeFactionChoiceResponse(random.choice(msg.available_factions))

    def _handle_strike_piece_targeting(self, msg: StrikePieceTargetingMessage) -> StrikePieceTargetingResponse:
        return StrikePieceTargetingResponse(random.choice(msg.available_pieces))

    def _handle_aid_faction_choice(self, msg: AidFactionChoiceMessage) -> AidFactionChoiceResponse:
        return AidFactionChoiceResponse(random.choice(msg.available_factions))

    def _handle_aid_card_choice(self, msg: AidCardChoiceMessage) -> AidCardChoiceResponse:
        return AidCardChoiceResponse(random.choice(msg.available_cards))

    def _handle_aid_exhaust_item_choice(self, msg: AidExhaustItemChoiceMessage) -> AidExhaustItemChoiceResponse:
        return AidExhaustItemChoiceResponse(random.choice(msg.available_items))

    def _handle_aid_take_item_choice(self, msg: AidTakeItemChoiceMessage) -> AidTakeItemChoiceResponse:
        return AidTakeItemChoiceResponse(random.choice(msg.available_items))

    def _handle_battle_damage_item(self, msg: BattleDamageItemMessage) -> BattleDamageItemResponse:
        if msg.available_items == [] and msg.exhausted_items == []:
            use_item_track = True
            is_exhausted = False
            track_items = []
            track_items.extend([Items.BAG] * msg.active_bag_count)
            track_items.extend([Items.COINS] * msg.active_coint_count)
            track_items.extend([Items.TEA] * msg.active_tea_count)
            chosen_item = random.choice(track_items)
            print(
                f" - chosen_item: {chosen_item}, is_exhausted: {is_exhausted}, use_item_track: {use_item_track}")
            return BattleDamageItemResponse(chosen_item, is_exhausted, use_item_track)

        is_exhausted = random.choice(
            [msg.exhausted_items != [], msg.available_items == []])

        if is_exhausted:
            use_item_track = False
            chosen_item = random.choice(msg.exhausted_items)
        elif msg.active_bag_count == 0 and msg.active_coint_count == 0 and msg.active_tea_count == 0:
            use_item_track = False
            chosen_item = random.choice(msg.available_items)
        else:
            all_available_items = []
            all_available_items.extend(msg.available_items)
            all_available_items.extend([Items.BAG] * msg.active_bag_count)
            all_available_items.extend([Items.COINS] * msg.active_coint_count)
            all_available_items.extend([Items.TEA] * msg.active_tea_count)
            chosen_item = random.choice(all_available_items)

            if (chosen_item == Items.BAG and msg.active_bag_count > 0) or (chosen_item == Items.COINS and msg.active_coint_count > 0) or (chosen_item == Items.TEA and msg.active_tea_count > 0):
                if chosen_item in msg.available_items:
                    use_item_track = random.choice([True, False])
                else:
                    use_item_track = True
            else:
                use_item_track = False

        print(
            f" - chosen_item: {chosen_item}, is_exhausted: {is_exhausted}, use_item_track: {use_item_track}")

        return BattleDamageItemResponse(chosen_item, is_exhausted, use_item_track)
