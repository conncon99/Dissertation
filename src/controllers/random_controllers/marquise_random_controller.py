from __future__ import annotations
from controllers.base_controllers.marquise_controller import MarquiseController
from controllers.messages.game_messages import *
from controllers.messages.controller_messages import *
from utils.root_types import Suits

from typing import TYPE_CHECKING, List

import random

if TYPE_CHECKING:
    from board.clearing import Clearing


class MarquiseRandomController(MarquiseController):

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

    def _handle_stand_and_deliver(self, msg: StandAndDeliverMessage) -> StandAndDeliverResponse:
        return StandAndDeliverResponse(random.choice(msg.available_players))

    def _handle_tax_collector(self, msg: TaxCollectorMessage) -> TaxCollectorResponse:
        return TaxCollectorResponse(random.choice(msg.available_units))

    def _handle_codebreakers(self, msg: CodebreakersMessage) -> CodebreakersResponse:
        return CodebreakersResponse(random.choice(msg.available_players))

    def _handle_claim_dominance_card(self, msg: ClaimDominanceCardMessage) -> ClaimDominanceCardResponse:
        return ClaimDominanceCardResponse(random.choice(msg.available_discard_cards))

    def _handle_claim_dominance_suit(self, msg: ClaimDominanceSuitMessage) -> ClaimDominanceSuitResponse:
        return ClaimDominanceSuitResponse(random.choice(msg.available_dominance_cards))

    def _handle_battle_clearing_choice(self, msg: BattleClearingChoiceMessage) -> BattleClearingResponse:
        return BattleClearingResponse(random.choice(msg.available_clearings))

    def _handle_battle_card_message(self, msg: BattleUseCardMessage) -> BattleUseCardResponse:
        return BattleUseCardResponse(random.choice([True, False]))

    def _handle_better_burrow_bank(self, msg: BetterBurrowBankMessage) -> BetterBurrowBankResponse:
        return BetterBurrowBankResponse(random.choice(msg.available_players))

    def _handle_dominance_choice(self, msg: ChooseDominanceMessage) -> ChooseDominanceResponse:
        return ChooseDominanceResponse(random.choice(msg.available_cards))

    def _handle_battle_target_choice(self, msg: BattleTargetChoiceMessage) -> BattleTargetResponse:
        return BattleTargetResponse(random.choice(msg.battle_target_list))

    def _handle_discard_choice(self, msg: DiscardChoiceMessage) -> DiscardChoiceResponse:
        return DiscardChoiceResponse(random.sample(msg.discard_options, msg.num_to_discard))

    def _handle_triggerer_outrage_message(self, msg: TriggererOutrageMessage) -> TriggererOutrageResponse:
        return TriggererOutrageResponse(random.choice(msg.valid_cards))

    # Marquise controller
    def _handle_keep_clearing_choice(self, msg: KeepClearingMessage) -> KeepClearingResponse:
        return KeepClearingResponse(random.choice(msg.available_clearings))

    def _handle_march_1_choice(self, msg: March1Message) -> March1Response:
        move_choice_idx = random.randint(0, len(msg.available_moves) - 1)
        from_clearing, to_clearing, all_units = msg.available_moves[move_choice_idx]
        if len(all_units) == 1:
            units = all_units
        else:
            units = random.sample(
                all_units, random.randint(1, len(all_units)))
        return March1Response(from_clearing, to_clearing, units)

    def _handle_march_2_choice(self, msg: March2Message) -> March2Response:
        move_choice_idx = random.randint(0, len(msg.available_moves) - 1)
        from_clearing, to_clearing, all_units = msg.available_moves[move_choice_idx]
        if len(all_units) == 1:
            units = all_units
        else:
            units = random.sample(
                all_units, random.randint(1, len(all_units)))
        if random.randint(0, 2) == 1:
            print(" - Not performing second march movement")
            return March2Response(None, None, None)
        return March2Response(from_clearing, to_clearing, units)

    def _handle_overwork_choice(self, msg: OverworkMessage) -> OverworkResponse:
        chosen_clearing = random.choice(msg.available_clearings)
        chosen_discard = random.choice(
            [card for card in msg.hand if card.suit == Suits.BIRD or card.suit == chosen_clearing.get_suit()])
        return OverworkResponse(chosen_discard, chosen_clearing)

    def _handle_marquise_building_choice(self, msg: MarquiseBuildingMessage) -> MarquiseBuildingResponse:
        clearing = random.choice(list(msg.clearing_building_options))
        building_type = random.choice(msg.clearing_building_options[clearing])
        return MarquiseBuildingResponse(clearing, building_type)

    def _handle_wood_removal_choice(self, msg: WoodRemovalMessage) -> WoodRemovalResponse:
        return WoodRemovalResponse(random.sample(msg.wood_list, msg.cost))

    def _handle_marquise_building_setup_choice(self, msg: MarquiseBuildingSetupMessage) -> MarquiseBuildingSetupResponse:
        available_clearings: List[Clearing] = msg.available_clearings
        clearings_to_slots = {
            clearing: sum(1 for slot in clearing.slots if slot is None) for clearing in available_clearings}
        building_clearings = []  # Sawmill, Recruiter, Workshop
        for i in range(3):
            building_clearing: Clearing = random.choice(available_clearings)
            clearings_to_slots[building_clearing] -= 1
            if clearings_to_slots[building_clearing] <= 0:
                available_clearings.remove(building_clearing)
            building_clearings.append(building_clearing)
        return MarquiseBuildingSetupResponse(sawmill_clearing=building_clearings[0], recruiter_clearing=building_clearings[1], workshop_clearing=building_clearings[2])

    def _handle_marquise_spend_bird_card_choice(self, msg: MarquiseSpendBirdCardMessage):
        return MarquiseSpendBirdCardResponse(random.choice(msg.bird_cards))

    def _handle_field_hospital_choice(self, msg: FieldHospitalMessage) -> FieldHospitalResponse:
        return FieldHospitalResponse(random.choice(msg.available_cards))
