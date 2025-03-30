from __future__ import annotations
from controllers.base_controllers.woodland_alliance_controller import AllianceController
from controllers.messages.game_messages import *
from controllers.messages.controller_messages import *
from utils.root_types import Suits

from typing import TYPE_CHECKING, List

import random

if TYPE_CHECKING:
    from board.clearing import Clearing


class AlliancePlayerController(AllianceController):

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
        raise NotImplementedError

    # Woodland Alliance Controller

    def _handle_no_bases_message(self, msg: AllianceNoBaseMessage) -> AllianceNoBaseResponse:
        print("Choose Supporter to Discard:")
        response_mapping = self.setup_mapping(msg.supporters)
        return AllianceNoBaseResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_mobilize_message(self, msg: MobilizeMessage) -> MobilizeResponse:
        print("Choose Card to Add to Supporters:")
        response_mapping = self.setup_mapping(msg.available_cards)
        return MobilizeResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_train_message(self, msg: TrainMessage) -> TrainResponse:
        print("Choose Card to Discard to create an Officer:")
        response_mapping = self.setup_mapping(msg.available_cards)
        return TrainResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_revolt_clearing_message(self, msg: RevoltClearingMessage) -> RevoltClearingResponse:
        print("Choose Clearing to Revolt In:")
        response_mapping = self.setup_mapping(msg.available_clearings)
        return RevoltClearingResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_revolt_discard_message(self, msg: RevoltDiscardMessage) -> RevoltDiscardResponse:
        print("Choose Supporter to Discard:")
        response_mapping = self.setup_mapping(msg.valid_supporters)
        return RevoltDiscardResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_spread_sympathy_clearing_message(self, msg: SpreadSympathyClearingMessage) -> SpreadSympathyClearingResponse:
        print("Choose Clearing to Spread Sympathy To:")
        response_mapping = self.setup_mapping(msg.available_clearings)
        return SpreadSympathyClearingResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_spread_sympathy_discard_message(self, msg: SpreadSympathyDiscardMessage) -> SpreadSympathyDiscardResponse:
        print("Choose Supporter to Discard:")
        response_mapping = self.setup_mapping(msg.available_supporters)
        return SpreadSympathyDiscardResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_alliance_recruit_message(self, msg: AllianceRecruitMessage) -> AllianceRecruitResponse:
        print("Choose Clearing to Recruit Warrior In:")
        response_mapping = self.setup_mapping(msg.available_clearings)
        return AllianceRecruitResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_organize_message(self, msg: OrganizeMessage) -> OrganizeResponse:
        print("Choose Warrior to Replace with Sympathy:")
        response_mapping = self.setup_mapping(msg.available_units)
        return OrganizeResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_alliance_outrage_message(self, msg: AllianceOutrageMessage) -> AllianceOutrageResponse:
        print("Choose Card to take from opponents hand: ")
        response_mapping = self.setup_mapping(msg.triggerer_hand)
        return AllianceOutrageResponse(response_mapping[self._get_response(response_mapping)])
