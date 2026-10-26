from __future__ import annotations
from src.controllers.base_controllers.eyrie_dynasties_controller import EyrieDynastiesController
from src.controllers.messages.game_messages import *
from src.controllers.messages.controller_messages import *
from src.utils.root_types import Suits

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from src.board.clearing import Clearing


class EyriePlayerController(EyrieDynastiesController):

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
        self.logger.info("Choose card to give the Woodland Alliance:")
        response_mapping = self.setup_mapping(msg.valid_cards)
        return TriggererOutrageResponse(response_mapping[self._get_response(response_mapping)])

# Eyrie Controller

    def _handle_roostless_message(self, msg: RoostlessMessage) -> RoostlessResponse:
        self.logger.info("Choose Clearing to place Roost:")
        response_mapping = self.setup_mapping(msg.available_clearings)
        return RoostlessResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_roost_setup_message(self, msg: RoostSetupMessage) -> RoostSetupResponse:
        self.logger.info("Choose Clearing to place Roost:")
        response_mapping = self.setup_mapping(msg.available_clearings)
        return RoostSetupResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_leader_setup_message(self, msg: LeaderSetupMessage) -> LeaderSetupResponse:
        self.logger.info("Choose Starting Eyrie Leader:")
        response_mapping = self.setup_mapping(msg.leader_choices)
        return LeaderSetupResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_decree_recruit_message(self, msg: DecreeRecruitClearingMessage) -> DecreeRecruitClearingResponse:
        self.logger.info("Choose Clearing to Recruit In:")
        response_mapping = self.setup_mapping(msg.available_clearings)
        return DecreeRecruitClearingResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_extend_decree_card_1(self, msg: ExtendDecreeCardMessage1) -> ExtendDecreeCardResponse1:
        self.logger.info("Choose Card to add to Decree:")
        card_response_mapping = self.setup_mapping(msg.available_cards)
        return ExtendDecreeCardResponse1(card_response_mapping[self._get_response(
            card_response_mapping)])

    def _handle_extend_decree_action_1(self, msg: ExtendDecreeActionMessage1) -> ExtendDecreeActionResponse1:
        self.logger.info("Choose Decree Type to Extend:")
        decree_response_mapping = self.setup_mapping(
            ["Recruit", "Move", "Battle", "Build"])
        return ExtendDecreeActionResponse1(int(self._get_response(decree_response_mapping)) + 1)

    def _handle_extend_decree_card_2(self, msg: ExtendDecreeCardMessage2) -> ExtendDecreeCardResponse2:
        self.logger.info("Choose Card to add to Decree:")
        card_response_mapping = self.setup_mapping(msg.available_cards)
        ExtendDecreeCardResponse2(
            card_response_mapping[self._get_response(card_response_mapping)])

    def _handle_extend_decree_action_2(self, msg: ExtendDecreeActionMessage2) -> ExtendDecreeActionResponse2:
        self.logger.info("Choose Decree Type to Extend:")
        decree_response_mapping = self.setup_mapping(
            ["Recruit", "Move", "Battle", "Build", None])
        decoder = {'0': 1, '1': 2, '2': 3, '3': 4, '4': None}
        return ExtendDecreeActionResponse2(decoder[self._get_response(decree_response_mapping)])

    def _handle_decree_build_message(self, msg: DecreeBuildMessage) -> DecreeBuildResponse:
        self.logger.info("Choose Clearing to Build Roost In:")
        response_mapping = self.setup_mapping(msg.available_clearings)
        return DecreeBuildResponse(response_mapping[self._get_response(response_mapping)])

    def _handle_turmoil_leader_message(self, msg: TurmoilLeaderMessage) -> TurmoilLeaderResponse:
        self.logger.info("Choose new Eyrie Leader:")
        response_mapping = self.setup_mapping(msg.available_leaders)
        return TurmoilLeaderResponse(response_mapping[self._get_response(response_mapping)])
