from __future__ import annotations
from src.controllers.base_controllers.vagabond_controller import VagabondController
from src.controllers.messages.game_messages import *
from src.controllers.messages.controller_messages import *
from src.utils.root_types import Items

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from src.board.clearing import Clearing


class VagabondRandomController(VagabondController):

    def __init__(self) -> None:
        """A dummy controller that chooses all its options randomly"""
        super().__init__()

    def _handle_faction_messages(self, msg):
        if self.pending_action:
            self.logger.debug("- Using Pending Action")
            action = self.pending_action
            self.pending_action = None
            return action
        else:
            return super()._handle_faction_messages(msg)

    def _handle_ambushes(self, msg: AmbushMessage) -> AmbushResponse:
        msg.available_ambush_cards.append(None)
        return AmbushResponse(np.random.choice(msg.available_ambush_cards))

    def _handle_piece_targeting(self, msg: PieceTargetingMessage) -> PieceTargetingResponse:
        return PieceTargetingResponse(np.random.choice(msg.targets))

    def _handle_move_from(self, msg: MoveFromMessage) -> MoveFromResponse:
        return MoveFromResponse(np.random.choice(msg.available_from_clearings))

    def _handle_move_to(self, msg: MoveToMessage) -> MoveToResponse:
        return MoveToResponse(np.random.choice(msg.available_to_clearings))

    def _handle_move_units(self, msg: MoveUnitsMessage) -> MoveUnitsResponse:
        if len(msg.available_units) == 1:
            return MoveUnitsResponse(1)
        return MoveUnitsResponse(np.random.randint(1, len(msg.available_units) + 1))

    def _handle_crafting(self, msg: CraftMessage) -> CraftResponse:
        return CraftResponse(np.random.choice(msg.crafting_options))

    def _handle_stand_and_deliver(self, msg: StandAndDeliverMessage) -> StandAndDeliverResponse:
        return StandAndDeliverResponse(np.random.choice(msg.available_players))

    def _handle_tax_collector(self, msg: TaxCollectorMessage) -> TaxCollectorResponse:
        return TaxCollectorResponse(np.random.choice(msg.available_units))

    def _handle_codebreakers(self, msg: CodebreakersMessage) -> CodebreakersResponse:
        return CodebreakersResponse(np.random.choice(msg.available_players))

    def _handle_claim_dominance_card(self, msg: ClaimDominanceCardMessage) -> ClaimDominanceCardResponse:
        return ClaimDominanceCardResponse(np.random.choice(msg.available_discard_cards))

    def _handle_claim_dominance_suit(self, msg: ClaimDominanceSuitMessage) -> ClaimDominanceSuitResponse:
        return ClaimDominanceSuitResponse(np.random.choice(msg.available_dominance_cards))

    def _handle_action_choice(self, msg: ActionChoiceMessage) -> ActionChoiceResponse:
        return ActionChoiceResponse(np.random.choice(msg.available_actions))

    def _handle_battle_clearing_choice(self, msg: BattleClearingChoiceMessage) -> BattleClearingChoiceResponse:
        return BattleClearingChoiceResponse(np.random.choice(msg.available_clearings))

    def _handle_better_burrow_bank(self, msg: BetterBurrowBankMessage) -> BetterBurrowBankResponse:
        return BetterBurrowBankResponse(np.random.choice(msg.available_players))

    def _handle_battle_card_message(self, msg: BattleUseCardMessage) -> BattleUseCardResponse:
        return BattleUseCardResponse(np.random.choice([True, False]))

    def _handle_dominance_choice(self, msg: ChooseDominanceMessage) -> ChooseDominanceResponse:
        return ChooseDominanceResponse(np.random.choice(msg.available_cards))

    def _handle_battle_target_choice(self, msg: BattleTargetChoiceMessage) -> BattleTargetResponse:
        return BattleTargetResponse(np.random.choice(msg.battle_target_list))

    def _handle_discard_choice(self, msg: DiscardChoiceMessage) -> DiscardChoiceResponse:
        return DiscardChoiceResponse(np.random.choice(msg.discard_options))

    def _handle_triggerer_outrage_message(self, msg: TriggererOutrageMessage) -> TriggererOutrageResponse:
        return TriggererOutrageResponse(np.random.choice(msg.valid_cards))

    # Vagabond Controller

    def _handle_choose_character(self, msg: ChooseCharacterMessage) -> ChooseCharacterResponse:
        return ChooseCharacterResponse(np.random.choice(msg.available_characters))

    def _handle_vagabond_placement(self, msg: VagabondPlacementMessage) -> VagabondPlacementResponse:
        return VagabondPlacementResponse(np.random.choice(msg.available_forests))

    def _handle_ranger_repair(self, msg: RangerRepairMessage) -> RangerRepairResponse:
        if msg.available_damaged and msg.exhausted_damaged:
            is_exhausted = np.random.choice([True, False])
        else:
            is_exhausted = msg.exhausted_damaged != []

        chosen_item = np.random.choice(
            msg.exhausted_damaged) if is_exhausted else np.random.choice(msg.available_damaged)
        return RangerRepairResponse((chosen_item, is_exhausted, True))

    def _handle_tinker_card(self, msg: TinkerCardMessage) -> TinkerCardResponse:
        return TinkerCardResponse(np.random.choice(msg.available_cards))

    def _handle_thief_steal(self, msg: ThiefStealMessage) -> ThiefStealResponse:
        return ThiefStealResponse(np.random.choice(msg.available_players))

    def _handle_slip_space(self, msg: SlipMessage) -> SlipResponse:
        return SlipResponse(np.random.choice(msg.available_spaces))

    def _handle_refresh_item(self, msg: RefreshItemMessage) -> RefreshItemResponse:
        if msg.damaged_items and msg.undamaged_items:
            is_damaged = np.random.choice([True, False])
        else:
            is_damaged = msg.damaged_items != []

        chosen_item = np.random.choice(
            msg.damaged_items) if is_damaged else np.random.choice(msg.undamaged_items)
        return RefreshItemResponse((chosen_item, True, is_damaged))

    def _handle_vagabond_move(self, msg: VagabondMoveMessage) -> VagabondMoveResponse:
        clearing_list = list(msg.clearing_dict.keys())
        return VagabondMoveResponse(np.random.choice(clearing_list))

    def _handle_choose_quest(self, msg: ChooseQuestMessage) -> ChooseQuestResponse:
        return ChooseQuestResponse(np.random.choice(msg.available_quests))

    def _handle_quest_use_item_track(self, msg: QuestUseItemTrackMessage) -> QuestUseItemTrackResponse:
        if msg.available_count > 0 and msg.track_count > 0:
            use_item_track = np.random.choice([True, False])
        elif msg.available_count > 0:
            use_item_track = False
        else:
            use_item_track = True
        return QuestUseItemTrackResponse(use_item_track)

    def _handle_choose_quest_reward(self, msg: ChooseQuestRewardMessage) -> ChooseQuestRewardResponse:
        return ChooseQuestRewardResponse(np.random.choice([True, False]))

    def _handle_repair_item(self, msg: RepairItemMessage) -> RepairItemResponse:
        if msg.available_damaged and msg.exhausted_damaged:
            is_exhausted = np.random.choice([True, False])
        else:
            is_exhausted = msg.exhausted_damaged != []

        chosen_item = np.random.choice(
            msg.exhausted_damaged) if is_exhausted else np.random.choice(msg.available_damaged)
        return RepairItemResponse((chosen_item, is_exhausted, True))

    def _handle_empty_satchel(self, msg: EmptySatchelMessage) -> EmptySatchelResponse:
        self.logger.info(
            f"ed: {len(msg.exhausted_damaged_items)} , e: {len(msg.exhausted_items)}, ad: {len(msg.available_damaged_items)}, a: {len(msg.available_items)}")

        has_exhausted = bool(
            msg.exhausted_items or msg.exhausted_damaged_items)
        has_available = bool(
            msg.available_items or msg.available_damaged_items)

        has_damaged_exhausted = bool(msg.exhausted_damaged_items)
        has_damaged_available = bool(msg.available_damaged_items)

        if has_exhausted and has_available:
            is_exhausted = np.random.choice([True, False])
        elif has_exhausted:
            is_exhausted = True
        else:
            is_exhausted = False

        if has_damaged_exhausted or has_damaged_available:
            is_damaged = np.random.choice([True, False])
        else:
            is_damaged = False

        if is_exhausted:
            if is_damaged:
                candidates = msg.exhausted_damaged_items if msg.exhausted_damaged_items else msg.exhausted_items
            else:
                candidates = msg.exhausted_items if msg.exhausted_items else msg.exhausted_damaged_items
        else:
            if is_damaged:
                candidates = msg.available_damaged_items if msg.available_damaged_items else msg.available_items
            else:
                candidates = msg.available_items if msg.available_items else msg.available_damaged_items

        # If no candidates exist, you might want to raise an error or handle it gracefully.
        if not candidates:
            raise ValueError("No items available to choose from.")

        chosen_item = np.random.choice(candidates)
        return EmptySatchelResponse((chosen_item, is_exhausted, is_damaged))

    def _handle_strike_faction_choice(self, msg: StrikeFactionChoiceMessage) -> StrikeFactionChoiceResponse:
        return StrikeFactionChoiceResponse(np.random.choice(msg.available_factions))

    def _handle_strike_piece_targeting(self, msg: StrikePieceTargetingMessage) -> StrikePieceTargetingResponse:
        return StrikePieceTargetingResponse(np.random.choice(msg.available_pieces))

    def _handle_aid_faction_choice(self, msg: AidFactionChoiceMessage) -> AidFactionChoiceResponse:
        return AidFactionChoiceResponse(np.random.choice(msg.available_factions))

    def _handle_aid_card_choice(self, msg: AidCardChoiceMessage) -> AidCardChoiceResponse:
        return AidCardChoiceResponse(np.random.choice(msg.available_cards))

    def _handle_aid_exhaust_item_choice(self, msg: AidExhaustItemChoiceMessage) -> AidExhaustItemChoiceResponse:
        if (msg.bag_track > 0 or msg.tea_track > 0 or msg.coin_track > 0) and msg.available_items != []:
            use_item_track = np.random.choice([True, False])
        elif msg.available_items == []:
            use_item_track = True
        else:
            use_item_track = False

        if use_item_track:
            track_items = []
            track_items.extend([Items.BAG] * msg.bag_track)
            track_items.extend([Items.COINS] * msg.coin_track)
            track_items.extend([Items.TEA] * msg.tea_track)
            chosen_item = np.random.choice(track_items)
        else:
            chosen_item = np.random.choice(msg.available_items)
        return AidExhaustItemChoiceResponse((chosen_item, use_item_track))

    def _handle_aid_take_item_choice(self, msg: AidTakeItemChoiceMessage) -> AidTakeItemChoiceResponse:
        return AidTakeItemChoiceResponse(np.random.choice(msg.available_items))

    def _handle_battle_damage_item(self, msg: BattleDamageItemMessage) -> BattleDamageItemResponse:
        if msg.available_items == [] and msg.exhausted_items == []:
            use_item_track = True
            is_exhausted = False
            track_items = []
            track_items.extend([Items.BAG] * msg.active_bag_count)
            track_items.extend([Items.COINS] * msg.active_coin_count)
            track_items.extend([Items.TEA] * msg.active_tea_count)
            chosen_item = np.random.choice(track_items)
            self.logger.info(
                f" - chosen_item: {chosen_item}, is_exhausted: {is_exhausted}, use_item_track: {use_item_track}")
            return BattleDamageItemResponse((chosen_item, is_exhausted, use_item_track))

        is_exhausted = np.random.choice(
            [msg.exhausted_items != [], msg.available_items == []])

        if is_exhausted:
            use_item_track = False
            chosen_item = np.random.choice(msg.exhausted_items)
        elif msg.active_bag_count == 0 and msg.active_coin_count == 0 and msg.active_tea_count == 0:
            use_item_track = False
            chosen_item = np.random.choice(msg.available_items)
        else:
            all_available_items = []
            all_available_items.extend(msg.available_items)
            all_available_items.extend([Items.BAG] * msg.active_bag_count)
            all_available_items.extend([Items.COINS] * msg.active_coin_count)
            all_available_items.extend([Items.TEA] * msg.active_tea_count)
            chosen_item = np.random.choice(all_available_items)

            if (chosen_item == Items.BAG and msg.active_bag_count > 0) or (chosen_item == Items.COINS and msg.active_coin_count > 0) or (chosen_item == Items.TEA and msg.active_tea_count > 0):
                if chosen_item in msg.available_items:
                    use_item_track = np.random.choice([True, False])
                else:
                    use_item_track = True
            else:
                use_item_track = False

        self.logger.info(
            f" - chosen_item: {chosen_item}, is_exhausted: {is_exhausted}, use_item_track: {use_item_track}")

        return BattleDamageItemResponse((chosen_item, is_exhausted, use_item_track))

    def _handle_coalition_choice(self, msg: CoalitionChoiceMessage) -> CoalitionChoiceResponse:
        return CoalitionChoiceResponse(np.random.choice(msg.available_factions))

    def _handle_choose_ally(self, msg: ChooseAllyMessage) -> ChooseAllyResponse:
        return ChooseAllyResponse(np.random.choice(msg.available_allies))

    def _handle_ally_damage_split(self, msg: AllyDamageSplitMessage) -> AllyDamageSplitResponse:
        return AllyDamageSplitResponse(np.random.randint(0, msg.max_damage + 1))

    def _handle_ally_movement_faction(self, msg: AllyMovementFactionMessage) -> AllyMovementFactionResponse:
        return AllyMovementFactionResponse(np.random.choice(msg.available_allies))

    def _handle_ally_movement_units_choice(self, msg: AllyMovementUnitMessage) -> AllyMovementUnitResponse:
        return AllyMovementUnitResponse(np.random.randint(1, len(msg.from_clearing.units[msg.chosen_ally.faction_id]) + 1))
