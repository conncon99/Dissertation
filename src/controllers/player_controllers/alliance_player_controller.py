from __future__ import annotations
from src.controllers.base_controllers.woodland_alliance_controller import AllianceController
from src.controllers.messages.game_messages import *
from src.controllers.messages.controller_messages import *
from src.utils.root_types import Suits

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from src.board.clearing import Clearing


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
        self.logger.info("Choose Ambush Card:")
        msg.available_ambush_cards.append(None)
        response_mapping = self.setup_mapping(msg.available_ambush_cards)
        return AmbushResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_piece_targeting(self, msg: PieceTargetingMessage) -> PieceTargetingResponse:
        self.logger.info("Choose Piece to Destroy:")
        response_mapping = self.setup_mapping(msg.targets)
        return PieceTargetingResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_move_from(self, msg: MoveFromMessage) -> MoveFromResponse:
        self.logger.info("Choose Move From Clearing:")
        from_response_mapping = self.setup_mapping(
            msg.available_from_clearings)
        return MoveFromResponse(from_response_mapping[self._get_response(from_response_mapping)])

    def _handle_move_to(self, msg: MoveToMessage) -> MoveToResponse:
        self.logger.info("Choose Move To Clearing:")
        to_response_mapping = self.setup_mapping(
            msg.available_to_clearings)
        return MoveToResponse(to_response_mapping[self._get_response(to_response_mapping)])

    def _handle_move_units(self, msg: MoveUnitsMessage) -> MoveUnitsResponse:
        if len(msg.available_units) == 1:
            return MoveUnitsResponse(1)
        response = int(
            input(f"Enter Number of Units To Move (Max: {len(msg.available_units)})"))
        while response < 0 or response > len(msg.available_units):
            response = int(
                input(f"Enter Number of Units To Move (Max: {len(msg.available_units)})"))
        return MoveUnitsResponse(response)

    def _handle_crafting(self, msg: CraftMessage) -> CraftResponse:
        self.logger.info("Choose Card to Craft:")
        response_mapping = self.setup_mapping(msg.crafting_options)
        return CraftResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_action_choice(self, msg: ActionChoiceMessage) -> ActionChoiceResponse:
        self.logger.info("Choose Action to Take:")
        response_mapping = self.setup_mapping(msg.available_actions)
        return ActionChoiceResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_stand_and_deliver(self, msg: StandAndDeliverMessage) -> StandAndDeliverResponse:
        self.logger.info("Choose Faction to Target:")
        response_mapping = self.setup_mapping(msg.available_players)
        return StandAndDeliverResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_tax_collector(self, msg: TaxCollectorMessage) -> TaxCollectorResponse:
        self.logger.info("Choose Unit to Remove:")
        response_mapping = self.setup_mapping(msg.available_units)
        return TaxCollectorResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_codebreakers(self, msg: CodebreakersMessage) -> CodebreakersResponse:
        self.logger.info("Choose Faction to Target:")
        response_mapping = self.setup_mapping(msg.available_players)
        return CodebreakersResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_claim_dominance_card(self, msg: ClaimDominanceCardMessage) -> ClaimDominanceCardResponse:
        self.logger.info("Choose Card to Discard In exchange for Dominance:")
        response_mapping = self.setup_mapping(msg.available_discard_cards)
        return ClaimDominanceCardResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_claim_dominance_suit(self, msg: ClaimDominanceSuitMessage) -> ClaimDominanceSuitResponse:
        self.logger.info("Choose Dominance card to claim:")
        response_mapping = self.setup_mapping(msg.available_dominance_cards)
        return ClaimDominanceSuitResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_battle_clearing_choice(self, msg: BattleClearingChoiceMessage) -> BattleClearingChoiceResponse:
        self.logger.info("Choose Clearing to Battle On:")
        response_mapping = self.setup_mapping(msg.available_clearings)
        return BattleClearingChoiceResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_battle_card_message(self, msg: BattleUseCardMessage) -> BattleUseCardResponse:
        self.logger.info("Choose whether to use a card in battle:")
        response_mapping = self.setup_mapping([True, False])
        return BattleUseCardResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_better_burrow_bank(self, msg: BetterBurrowBankMessage) -> BetterBurrowBankResponse:
        self.logger.info("Choose other player to also draw card:")
        response_mapping = self.setup_mapping(msg.available_players)
        return BetterBurrowBankResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_dominance_choice(self, msg: ChooseDominanceMessage) -> ChooseDominanceResponse:
        self.logger.info("Choose dominance to play:")
        response_mapping = self.setup_mapping(msg.available_cards)
        return ChooseDominanceResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_battle_target_choice(self, msg: BattleTargetChoiceMessage) -> BattleTargetResponse:
        self.logger.info("Choose target to battle:")
        response_mapping = self.setup_mapping(msg.battle_target_list)
        return BattleTargetResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_discard_choice(self, msg: DiscardChoiceMessage) -> DiscardChoiceResponse:
        self.logger.info("Choose card to discard:")
        response_mapping = self.setup_mapping(msg.discard_options)
        return DiscardChoiceResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_triggerer_outrage_message(self, msg: TriggererOutrageMessage) -> TriggererOutrageResponse:
        raise NotImplementedError

    # Woodland Alliance Controller

    def _handle_no_bases_message(self, msg: AllianceNoBaseMessage) -> AllianceNoBaseResponse:
        self.logger.info("Choose Supporter to Discard:")
        response_mapping = self.setup_mapping(msg.supporters)
        return AllianceNoBaseResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_mobilize_message(self, msg: MobilizeMessage) -> MobilizeResponse:
        self.logger.info("Choose Card to Add to Supporters:")
        response_mapping = self.setup_mapping(msg.available_cards)
        return MobilizeResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_train_message(self, msg: TrainMessage) -> TrainResponse:
        self.logger.info("Choose Card to Discard to create an Officer:")
        response_mapping = self.setup_mapping(msg.available_cards)
        return TrainResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_revolt_clearing_message(self, msg: RevoltClearingMessage) -> RevoltClearingResponse:
        self.logger.info("Choose Clearing to Revolt In:")
        response_mapping = self.setup_mapping(msg.available_clearings)
        return RevoltClearingResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_revolt_discard_message(self, msg: RevoltDiscardMessage) -> RevoltDiscardResponse:
        self.logger.info("Choose Supporter to Discard:")
        response_mapping = self.setup_mapping(msg.valid_supporters)
        return RevoltDiscardResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_spread_sympathy_clearing_message(self, msg: SpreadSympathyClearingMessage) -> SpreadSympathyClearingResponse:
        self.logger.info("Choose Clearing to Spread Sympathy To:")
        response_mapping = self.setup_mapping(msg.available_clearings)
        return SpreadSympathyClearingResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_spread_sympathy_discard_message(self, msg: SpreadSympathyDiscardMessage) -> SpreadSympathyDiscardResponse:
        self.logger.info("Choose Supporter to Discard:")
        response_mapping = self.setup_mapping(msg.available_supporters)
        return SpreadSympathyDiscardResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_alliance_recruit_message(self, msg: AllianceRecruitMessage) -> AllianceRecruitResponse:
        self.logger.info("Choose Clearing to Recruit Warrior In:")
        response_mapping = self.setup_mapping(msg.available_clearings)
        return AllianceRecruitResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_organize_message(self, msg: OrganizeMessage) -> OrganizeResponse:
        self.logger.info("Choose Warrior to Replace with Sympathy:")
        response_mapping = self.setup_mapping(msg.available_units)
        return OrganizeResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_alliance_outrage_message(self, msg: AllianceOutrageMessage) -> AllianceOutrageResponse:
        self.logger.info("Choose Card to take from opponents hand: ")
        response_mapping = self.setup_mapping(msg.triggerer_hand)
        return AllianceOutrageResponse(response_mapping[self._get_response(response_mapping)])
