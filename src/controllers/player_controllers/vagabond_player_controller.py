from __future__ import annotations
from controllers.base_controllers.vagabond_controller import VagabondController
from controllers.messages.game_messages import *
from controllers.messages.controller_messages import *
from utils.root_types import Items

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from board.clearing import Clearing


class VagabondPlayerController(VagabondController):

    def _get_response(self, response_mapping) -> str:
        response = input(
            f"Enter option from {list(response_mapping.items())}: ").upper()
        while response not in response_mapping.keys():
            response = input(
                f"Enter option from {list(response_mapping.items())}: ").upper()
        return response

    def setup_mapping(self, options):
        def get_sort_key(item):
            # Try to get a valid numeric id
            item_id = getattr(item, 'id', None)
            if isinstance(item_id, (int, float)):
                return item_id

            # If no valid id, try to get a valid numeric index
            item_index = getattr(item, 'index', None)
            if isinstance(item_index, (int, float)):
                return item_index

            # If neither is valid, return None to indicate no sorting
            return None

        # Check if all items have a valid sort key (either id or index)
        all_keys_valid = all(get_sort_key(
            item) is not None for item in options)

        # Sort if all items have a valid key, otherwise keep the original order
        if all_keys_valid:
            options = sorted(options, key=get_sort_key)

        return {str(i): item for i, item in enumerate(options)}

    def _handle_ambushes(self, msg: AmbushMessage) -> AmbushResponse:
        print("Choose Ambush Card:")
        msg.available_ambush_cards.append(None)
        response_mapping = self.setup_mapping(msg.available_ambush_cards)
        return AmbushResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_battle_end(self, msg: BattleEndMessage):
        raise NotImplementedError

    def _handle_piece_targeting(self, msg: PieceTargetingMessage) -> PieceTargetingResponse:
        print("Choose Piece to Destroy:")
        response_mapping = self.setup_mapping(msg.targets)
        return PieceTargetingResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_movement(self, msg: MoveMessage) -> MoveResponse:

        print("Choose Move From Clearing:")
        from_clearings = set([move[0] for move in msg.available_moves])
        from_response_mapping = self.setup_mapping(from_clearings)
        from_clearing = from_response_mapping[self._get_response(
            from_response_mapping)]

        print("Choose Move To Clearing:")
        to_clearings = set([move[1]
                            for move in msg.available_moves if move[0] == from_clearing])
        to_response_mapping = self.setup_mapping(to_clearings)
        to_clearing = to_response_mapping[self._get_response(
            to_response_mapping)]

        for movement in msg.available_moves:
            if movement[0] == from_clearing and movement[1] == to_clearing:
                all_units = movement[2]
                break

        if len(all_units) == 1:
            units = all_units
        else:
            response = int(
                input(f"Enter Number of Units To Move (Max: {len(all_units)})"))
            while response < 0 or response > len(all_units):
                response = int(
                    input(f"Enter Number of Units To Move (Max: {len(all_units)})"))
            units = all_units[:response]
        return MoveResponse(from_clearing, to_clearing, units)

    def _handle_crafting(self, msg: CraftMessage) -> CraftResponse:
        print("Choose Card to Craft:")
        response_mapping = self.setup_mapping(msg.crafting_options)
        return CraftResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_action_choice(self, msg: ActionChoiceMessage) -> ActionChoiceResponse:
        print("Choose Action to Take:")
        response_mapping = self.setup_mapping(msg.available_actions)
        return ActionChoiceResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_stand_and_deliver(self, msg: StandAndDeliverMessage) -> StandAndDeliverResponse:
        print("Choose Faction to Target:")
        response_mapping = self.setup_mapping(msg.available_players)
        return StandAndDeliverResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_tax_collector(self, msg: TaxCollectorMessage) -> TaxCollectorResponse:
        print("Choose Unit to Remove:")
        response_mapping = self.setup_mapping(msg.available_units)
        return TaxCollectorResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_codebreakers(self, msg: CodebreakersMessage) -> CodebreakersResponse:
        print("Choose Faction to Target:")
        response_mapping = self.setup_mapping(msg.available_players)
        return CodebreakersResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_claim_dominance_card(self, msg: ClaimDominanceCardMessage) -> ClaimDominanceCardResponse:
        print("Choose Card to Discard In exchange for Dominance:")
        response_mapping = self.setup_mapping(msg.available_discard_cards)
        return ClaimDominanceCardResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_claim_dominance_suit(self, msg: ClaimDominanceSuitMessage) -> ClaimDominanceSuitResponse:
        print("Choose Dominance card to claim:")
        response_mapping = self.setup_mapping(msg.available_dominance_cards)
        return ClaimDominanceSuitResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_battle_clearing_choice(self, msg: BattleClearingChoiceMessage) -> BattleClearingChoiceResponse:
        print("Choose Clearing to Battle On:")
        response_mapping = self.setup_mapping(msg.available_clearings)
        return BattleClearingChoiceResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_battle_card_message(self, msg: BattleUseCardMessage) -> BattleUseCardResponse:
        print("Choose whether to use a card in battle:")
        response_mapping = self.setup_mapping([True, False])
        return BattleUseCardResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_better_burrow_bank(self, msg: BetterBurrowBankMessage) -> BetterBurrowBankResponse:
        print("Choose other player to also draw card:")
        response_mapping = self.setup_mapping(msg.available_players)
        return BetterBurrowBankResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_dominance_choice(self, msg: ChooseDominanceMessage) -> ChooseDominanceResponse:
        print("Choose dominance to play:")
        response_mapping = self.setup_mapping(msg.available_cards)
        return ChooseDominanceResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_battle_target_choice(self, msg: BattleTargetChoiceMessage) -> BattleTargetResponse:
        print("Choose target to battle:")
        response_mapping = self.setup_mapping(msg.battle_target_list)
        return BattleTargetResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_discard_choice(self, msg: DiscardChoiceMessage) -> DiscardChoiceResponse:
        print("Choose card to discard:")
        response_mapping = self.setup_mapping(msg.discard_options)
        return DiscardChoiceResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_triggerer_outrage_message(self, msg: TriggererOutrageMessage) -> TriggererOutrageResponse:
        print("Choose card to give the Woodland Alliance:")
        response_mapping = self.setup_mapping(msg.valid_cards)
        return TriggererOutrageResponse(response_mapping[self._get_response(response_mapping)])

    # Vagabond Controller

    def _handle_choose_character(self, msg: ChooseCharacterMessage) -> ChooseCharacterResponse:
        print("Choose Vagabond Character:")
        response_mapping = self.setup_mapping(msg.available_characters)
        return ChooseCharacterResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_vagabond_placement(self, msg: VagabondPlacementMessage) -> VagabondPlacementResponse:
        print("Choose Vagabond Starting Forest:")
        response_mapping = self.setup_mapping(msg.available_forests)
        return VagabondPlacementResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_ranger_repair(self, msg: RangerRepairMessage) -> RangerRepairResponse:
        if msg.available_damaged and msg.exhausted_damaged:
            print("Choose Whether to Repair an Exhausted Item or Not:")
            exhausted_mapping = self.setup_mapping([True, False])
            is_exhausted = exhausted_mapping[self._get_response(
                exhausted_mapping)]
        else:
            is_exhausted = msg.exhausted_damaged != []

        print("Choose Item to Repair:")
        item_choice_mapping = self.setup_mapping(
            msg.exhausted_damaged if is_exhausted else msg.available_damaged)
        chosen_item = item_choice_mapping[self._get_response(
            item_choice_mapping)]
        return RangerRepairResponse(chosen_item, is_exhausted)

    def _handle_tinker_card(self, msg: TinkerCardMessage) -> TinkerCardResponse:
        print("Choose Card to Take from the Discard:")
        response_mapping = self.setup_mapping(msg.available_cards)
        return TinkerCardResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_thief_steal(self, msg: ThiefStealMessage) -> ThiefStealResponse:
        print("Choose Target to steal from:")
        response_mapping = self.setup_mapping(msg.available_players)
        return ThiefStealResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_slip_space(self, msg: SlipMessage) -> SlipResponse:
        print("Choose Space to Slip to:")
        response_mapping = self.setup_mapping(msg.available_spaces)
        return SlipResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_refresh_item(self, msg: RefreshItemMessage) -> RefreshItemResponse:
        if msg.damaged_items and msg.undamaged_items:
            print(f"Damaged Items: {msg.damaged_items}")
            print(f"Undamaged Items: {msg.undamaged_items}")
            print("Choose Whether you wish to refresh a damaged item:")
            damaged_response_mapping = self.setup_mapping([True, False])
            is_damaged = damaged_response_mapping[self._get_response(
                damaged_response_mapping)]
        else:
            is_damaged = msg.damaged_items != []

        print(
            f"Available Items: {msg.damaged_items if is_damaged else msg.undamaged_items}")
        print("Choose Item to Refresh:")
        item_mapping = self.setup_mapping(
            msg.damaged_items if is_damaged else msg.undamaged_items)
        chosen_item = item_mapping[self._get_response(item_mapping)]
        return RefreshItemResponse(is_damaged, chosen_item)

    def _handle_vagabond_move(self, msg: VagabondMoveMessage) -> VagabondMoveResponse:
        print("Choose Clearing to Move to:")
        clearing_list = list(msg.clearing_dict.keys())
        response_mapping = self.setup_mapping(clearing_list)
        return VagabondMoveResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_choose_quest(self, msg: ChooseQuestMessage) -> ChooseQuestResponse:
        print("Choose Quest to Complete:")
        response_mapping = self.setup_mapping(msg.available_quests)
        return ChooseQuestResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_quest_use_item_track(self, msg: QuestUseItemTrackMessage) -> QuestUseItemTrackResponse:
        if msg.available_count > 0 and msg.track_count > 0:
            response_mapping = self.setup_mapping([True, False])
            use_item_track = response_mapping[self._get_response(
                response_mapping)]
        else:
            use_item_track = msg.available_count <= 0
        return QuestUseItemTrackResponse(use_item_track)

    def _handle_choose_quest_reward(self, msg: ChooseQuestRewardMessage) -> ChooseQuestRewardResponse:
        print("Choose Quest Reward:")
        response_mapping = self.setup_mapping([True, False])
        return ChooseQuestRewardResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_repair_item(self, msg: RepairItemMessage) -> RepairItemResponse:
        if msg.available_damaged and msg.exhausted_damaged:
            print("Choose Whether an Exhausted Item should be Repaired:")
            exhausted_mapping = self.setup_mapping([True, False])
            is_exhausted = exhausted_mapping[self._get_response(
                exhausted_mapping)]
        else:
            is_exhausted = msg.exhausted_damaged != []

        print("Choose Item to Repair:")
        item_choice_mapping = self.setup_mapping(
            msg.exhausted_damaged if is_exhausted else msg.available_damaged)
        chosen_item = item_choice_mapping[self._get_response(
            item_choice_mapping)]
        return RepairItemResponse(is_exhausted, chosen_item)

    def _handle_empty_satchel(self, msg: EmptySatchelMessage) -> EmptySatchelResponse:
        print(f"ed: {len(msg.exhausted_damaged_items)} , e: {len(msg.exhausted_items)}, ad: {len(msg.available_damaged_items)}, a: {len(msg.available_items)}")

        has_exhausted = bool(
            msg.exhausted_items or msg.exhausted_damaged_items)
        has_available = bool(
            msg.available_items or msg.available_damaged_items)

        has_damaged_exhausted = bool(msg.exhausted_damaged_items)
        has_damaged_available = bool(msg.available_damaged_items)

        if has_exhausted and has_available:
            print("Choose Whether to Remove an Exhausted Item or not:")
            exhausted_mapping = self.setup_mapping([True, False])
            is_exhausted = exhausted_mapping[self._get_response(
                exhausted_mapping)]
        elif has_exhausted:
            is_exhausted = True
        else:
            is_exhausted = False

        if has_damaged_exhausted or has_damaged_available:
            print("Choose Whether to Remove a Damaged Item or not:")
            damaged_mapping = self.setup_mapping([True, False])
            is_damaged = damaged_mapping[self._get_response(
                damaged_mapping)]
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

        print("Choose Item to Remove:")
        chosen_item_mapping = self.setup_mapping(candidates)
        chosen_item = chosen_item_mapping[self._get_response(
            chosen_item_mapping)]
        return EmptySatchelResponse(chosen_item, is_damaged, is_exhausted)

    def _handle_strike_faction_choice(self, msg: StrikeFactionChoiceMessage) -> StrikeFactionChoiceResponse:
        print("Chose Faction to Strike:")
        response_mapping = self.setup_mapping(msg.available_factions)
        return StrikeFactionChoiceResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_strike_piece_targeting(self, msg: StrikePieceTargetingMessage) -> StrikePieceTargetingResponse:
        print("Choose Piece to Target:")
        response_mapping = self.setup_mapping(msg.available_pieces)
        return StrikePieceTargetingResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_aid_faction_choice(self, msg: AidFactionChoiceMessage) -> AidFactionChoiceResponse:
        print("Choose Faction to Aid:")
        response_mapping = self.setup_mapping(msg.available_factions)
        return AidFactionChoiceResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_aid_card_choice(self, msg: AidCardChoiceMessage) -> AidCardChoiceResponse:
        print("Choose Card to Give:")
        response_mapping = self.setup_mapping(msg.available_cards)
        return AidCardChoiceResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_aid_exhaust_item_choice(self, msg: AidExhaustItemChoiceMessage) -> AidExhaustItemChoiceResponse:
        if (msg.bag_track > 0 or msg.tea_track > 0 or msg.coin_track > 0) and msg.available_items != []:
            print("Choose Whether to use an Item from the item track:")
            item_track_mapping = self.setup_mapping([True, False])
            use_item_track = item_track_mapping[self._get_response(
                item_track_mapping)]
        elif msg.available_items == []:
            use_item_track = True
        else:
            use_item_track = False

        track_items = []
        if use_item_track:
            track_items.extend([Items.BAG] * msg.bag_track)
            track_items.extend([Items.COINS] * msg.coin_track)
            track_items.extend([Items.TEA] * msg.tea_track)
        item_choice_mapping = self.setup_mapping(
            track_items if use_item_track else msg.available_items)
        chosen_item = item_choice_mapping[self._get_response(
            item_choice_mapping)]
        return AidExhaustItemChoiceResponse(chosen_item, use_item_track)

    def _handle_aid_take_item_choice(self, msg: AidTakeItemChoiceMessage) -> AidTakeItemChoiceResponse:
        print("Choose Item to Take:")
        response_mapping = self.setup_mapping(msg.available_items)
        return AidTakeItemChoiceResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_battle_damage_item(self, msg: BattleDamageItemMessage) -> BattleDamageItemResponse:
        if msg.available_items == [] and msg.exhausted_items == []:
            use_item_track = True
            is_exhausted = False
            track_items = []
            track_items.extend([Items.BAG] * msg.active_bag_count)
            track_items.extend([Items.COINS] * msg.active_coin_count)
            track_items.extend([Items.TEA] * msg.active_tea_count)
            print("Choose Item from Track to Damage:")
            item_mappings = self.setup_mapping(track_items)
            chosen_item = item_mappings[self._get_response(item_mappings)]
            print(
                f" - chosen_item: {chosen_item}, is_exhausted: {is_exhausted}, use_item_track: {use_item_track}")
            return BattleDamageItemResponse(chosen_item, is_exhausted, use_item_track)

        print("Choose Whether to Use an Exhausted Item or Not:")
        exhausted_mapping = self.setup_mapping(
            [msg.exhausted_items != [], msg.available_items == []])
        is_exhausted = exhausted_mapping[self._get_response(exhausted_mapping)]

        if is_exhausted:
            use_item_track = False
            print("Choose Item to Damage from Exhausted Items:")
            item_mappings = self.setup_mapping(msg.exhausted_items)
            chosen_item = item_mappings[self._get_response(item_mappings)]
        elif msg.active_bag_count == 0 and msg.active_coin_count == 0 and msg.active_tea_count == 0:
            use_item_track = False
            print("Choose Item to Damage from Available Items:")
            item_mappings = self.setup_mapping(msg.available_items)
            chosen_item = item_mappings[self._get_response(item_mappings)]
        else:
            all_available_items = []
            all_available_items.extend(msg.available_items)
            all_available_items.extend([Items.BAG] * msg.active_bag_count)
            all_available_items.extend([Items.COINS] * msg.active_coin_count)
            all_available_items.extend([Items.TEA] * msg.active_tea_count)
            print("Choose Item to Damage from Battle:")
            item_mappings = self.setup_mapping(all_available_items)
            chosen_item = item_mappings[self._get_response(item_mappings)]

            if (chosen_item == Items.BAG and msg.active_bag_count > 0) or (chosen_item == Items.COINS and msg.active_coin_count > 0) or (chosen_item == Items.TEA and msg.active_tea_count > 0):
                if chosen_item in msg.available_items:
                    print("Choose Whether to Use Item on Item Track:")
                    item_track_mapping = self.setup_mapping([True, False])
                    use_item_track = item_track_mapping[self._get_response(
                        item_track_mapping)]
                else:
                    use_item_track = True
            else:
                use_item_track = False

        print(
            f" - chosen_item: {chosen_item}, is_exhausted: {is_exhausted}, use_item_track: {use_item_track}")

        return BattleDamageItemResponse(chosen_item, is_exhausted, use_item_track)

    def _handle_coalition_choice(self, msg: CoalitionChoiceMessage) -> CoalitionChoiceResponse:
        print("Choose Coalition Target:")
        response_mapping = self.setup_mapping(msg.available_factions)
        return CoalitionChoiceResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_ally_movement(self, msg: AllyMovementMessage) -> AllyMovementResponse:
        print("Choose Ally to Move with You:")
        ally_response_mapping = self.setup_mapping(msg.available_allies)
        chosen_ally = ally_response_mapping[self._get_response(
            ally_response_mapping)]

        if chosen_ally is None:
            chosen_units = []
        else:
            if len(msg.from_clearing.units[chosen_ally.faction_id]) > 1:
                response = input(
                    f"Choose Number of Allied Units to Move between 1 and {len(msg.from_clearing.units[chosen_ally.faction_id]) - 1}: ")
                while not response.isnumeric() or response.isnumeric() and (int(response) <= 0 or int(response) >= len(msg.from_clearing.units[chosen_ally.faction_id])):
                    response = input(
                        f"Choose Number of Allied Units to Move between 1 and {len(msg.from_clearing.units[chosen_ally.faction_id]) - 1}: ")
                chosen_units = msg.from_clearing.units[:int(response)]
            else:
                chosen_units = msg.from_clearing.units[chosen_ally.faction_id]
        return AllyMovementResponse(chosen_ally, chosen_units)

    def _handle_choose_ally(self, msg: ChooseAllyMessage) -> ChooseAllyResponse:
        print("Choose Battle Ally:")
        response_mapping = self.setup_mapping(msg.available_allies)
        return ChooseAllyResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_ally_damage_split(self, msg: AllyDamageSplitMessage) -> AllyDamageSplitResponse:
        print("Choose Amount Damage that Ally should Take:")
        response = input(
            f"Enter Option From: {[i for i in range(msg.max_damage + 1)]}")
        while not response.isnumeric() or response.isnumeric() and (int(response) < 0 or int(response) > msg.max_damage):
            response = input(
                f"Enter Option From: {[i for i in range(msg.max_damage + 1)]}")
        return AllyDamageSplitResponse(int(response))
