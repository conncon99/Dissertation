from __future__ import annotations
from src.controllers.base_controllers.marquise_controller import MarquiseController
from src.controllers.messages.game_messages import *
from src.controllers.messages.controller_messages import *
from src.utils.root_types import Suits

from typing import TYPE_CHECKING, List

import numpy as np

if TYPE_CHECKING:
    from src.board.clearing import Clearing


class MarquiseRandomController(MarquiseController):

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

    def _handle_move_from(self, msg: MoveFromMessage) -> MoveFromResponse:
        return MoveFromResponse(np.random.choice(msg.available_from_clearings))

    def _handle_move_to(self, msg: MoveToMessage) -> MoveToResponse:
        return MoveToResponse(np.random.choice(msg.available_to_clearings))

    def _handle_move_units(self, msg: MoveUnitsMessage) -> MoveUnitsResponse:
        if len(msg.available_units) == 1:
            return MoveUnitsResponse(1)
        return MoveUnitsResponse(np.random.randint(1, len(msg.available_units) + 1))

    def _handle_ambushes(self, msg: AmbushMessage) -> AmbushResponse:
        msg.available_ambush_cards.append(None)
        return AmbushResponse(np.random.choice(msg.available_ambush_cards))

    def _handle_piece_targeting(self, msg: PieceTargetingMessage) -> PieceTargetingResponse:
        return PieceTargetingResponse(np.random.choice(msg.targets))

    def _handle_crafting(self, msg: CraftMessage) -> CraftResponse:
        return CraftResponse(np.random.choice(msg.crafting_options))

    def _handle_action_choice(self, msg: ActionChoiceMessage) -> ActionChoiceResponse:
        return ActionChoiceResponse(np.random.choice(msg.available_actions))

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

    def _handle_battle_clearing_choice(self, msg: BattleClearingChoiceMessage) -> BattleClearingChoiceResponse:
        return BattleClearingChoiceResponse(np.random.choice(msg.available_clearings))

    def _handle_battle_card_message(self, msg: BattleUseCardMessage) -> BattleUseCardResponse:
        return BattleUseCardResponse(np.random.choice([True, False]))

    def _handle_better_burrow_bank(self, msg: BetterBurrowBankMessage) -> BetterBurrowBankResponse:
        return BetterBurrowBankResponse(np.random.choice(msg.available_players))

    def _handle_dominance_choice(self, msg: ChooseDominanceMessage) -> ChooseDominanceResponse:
        return ChooseDominanceResponse(np.random.choice(msg.available_cards))

    def _handle_battle_target_choice(self, msg: BattleTargetChoiceMessage) -> BattleTargetResponse:
        return BattleTargetResponse(np.random.choice(msg.battle_target_list))

    def _handle_discard_choice(self, msg: DiscardChoiceMessage) -> DiscardChoiceResponse:
        return DiscardChoiceResponse(np.random.choice(msg.discard_options))

    def _handle_triggerer_outrage_message(self, msg: TriggererOutrageMessage) -> TriggererOutrageResponse:
        return TriggererOutrageResponse(np.random.choice(msg.valid_cards))

    # Marquise controller
    def _handle_keep_clearing_choice(self, msg: KeepClearingMessage) -> KeepClearingResponse:
        return KeepClearingResponse(np.random.choice(msg.available_clearings))

    def _handle_wood_removal_choice(self, msg: WoodRemovalMessage) -> WoodRemovalResponse:
        return WoodRemovalResponse(np.random.choice(msg.wood_list))

    def _handle_marquise_spend_bird_card_choice(self, msg: MarquiseSpendBirdCardMessage):
        return MarquiseSpendBirdCardResponse(np.random.choice(msg.bird_cards))

    def _handle_field_hospital_choice(self, msg: FieldHospitalMessage) -> FieldHospitalResponse:
        return FieldHospitalResponse(np.random.choice(msg.available_cards))

    def _handle_march_again(self, msg: MarchAgainMessage) -> MarchAgainResponse:
        return MarchAgainResponse(np.random.choice([True, False]))

    def _handle_overwork_clearing(self, msg: OverworkClearingMessage) -> OverworkClearingResponse:
        return OverworkClearingResponse(np.random.choice(msg.available_clearings))

    def _handle_overwork_discard(self, msg: OverworkDiscardMessage) -> OverworkDiscardResponse:
        return OverworkDiscardResponse(np.random.choice(msg.available_cards))

    def _handle_marquise_building_type_choice(self, msg: MarquiseBuildingTypeMessage) -> MarquiseBuildingTypeResponse:
        return MarquiseBuildingTypeResponse(np.random.choice(msg.clearing_building_options))

    def _handle_marquise_building_clearing_choice(self, msg: MarquiseBuildingClearingMessage) -> MarquiseBuildingClearingResponse:
        return MarquiseBuildingClearingResponse(np.random.choice(list(msg.clearing_building_options)))

    def _handle_marquise_setup_workshop(self, msg: MarquiseWorkshopSetupMessage) -> MarquiseWorkshopSetupResponse:
        return MarquiseWorkshopSetupResponse(np.random.choice(msg.available_clearings))

    def _handle_marquise_setup_recruiter(self, msg: MarquiseRecruiterSetupMessage) -> MarquiseRecruiterSetupResponse:
        return MarquiseRecruiterSetupResponse(np.random.choice(msg.available_clearings))

    def _handle_marquise_setup_sawmill(self, msg: MarquiseSawmillSetupMessage) -> MarquiseSawmillSetupResponse:
        return MarquiseSawmillSetupResponse(np.random.choice(msg.available_clearings))
