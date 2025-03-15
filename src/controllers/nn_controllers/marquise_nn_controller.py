from __future__ import annotations
from controllers.base_controllers.marquise_controller import MarquiseController
from controllers.nn_controllers.observation_space_encoder import ObservationSpace
from controllers.messages.game_messages import *
from controllers.messages.controller_messages import *
from controllers.nn_controllers.action_space_decoder import *
from controllers.messages.game_messages import GameMessage
import numpy as np
from utils.root_types import Suits
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controllers.nn_controllers.faction_net import FactionNet
import torch


class MarquiseNNController(MarquiseController):

    def __init__(self, model: FactionNet):
        self.model = model

    def model_predict(self, msg: GameMessage):
        observation = ObservationSpace.encode_game_state(
            msg.game_state, msg.type, msg.action_group)

        # Query PPO to get a 54-length vector in range [0,1]
        observation_tensor = torch.tensor(
            observation, dtype=torch.float32).unsqueeze(0)  # Add batch dimension
        with torch.no_grad():
            action_probs = self.model(observation_tensor).numpy().flatten()
        return action_probs

    def _handle_battle_card_message(self, msg: BattleUseCardMessage) -> BattleUseCardResponse:
        return BattleUseCardResponse(decode_binary_choice(self.model_predict(msg)))

    def _handle_ambushes(self, msg: AmbushMessage) -> AmbushResponse:
        return AmbushResponse(decode_single_selection(self.model_predict(msg), msg.available_ambush_cards))

    def _handle_tax_collector(self, msg: TaxCollectorMessage) -> TaxCollectorResponse:
        return TaxCollectorResponse(decode_single_selection(self.model_predict(msg), msg.available_units))

    def _handle_stand_and_deliver(self, msg: StandAndDeliverMessage) -> StandAndDeliverResponse:
        return StandAndDeliverResponse(decode_single_selection(self.model_predict(msg), msg.available_players))

    def _handle_claim_dominance_suit(self, msg: ClaimDominanceSuitMessage) -> ClaimDominanceSuitResponse:
        return ClaimDominanceSuitResponse(decode_single_selection(self.model_predict(msg), msg.available_dominance_cards))

    def _handle_claim_dominance_card(self, msg: ClaimDominanceCardMessage) -> ClaimDominanceCardResponse:
        return ClaimDominanceCardResponse(decode_single_selection(self.model_predict(msg), msg.available_discard_cards))

    def _handle_codebreakers(self, msg: CodebreakersMessage) -> CodebreakersResponse:
        return CodebreakersResponse(decode_single_selection(self.model_predict(msg), msg.available_players))

    def _handle_battle_end(self, msg):
        raise NotImplementedError

    def _handle_piece_targeting(self, msg: PieceTargetingMessage) -> PieceTargetingResponse:
        return PieceTargetingResponse(decode_multiple_selection(self.model_predict(msg), msg.targets, msg.remaining_dmg))

    def _handle_better_burrow_bank(self, msg: BetterBurrowBankMessage) -> BetterBurrowBankResponse:
        return BetterBurrowBankResponse(decode_single_selection(self.model_predict(msg), msg.available_players))

    def _handle_movement(self, msg: MoveMessage) -> MoveResponse:
        move_choice_idx = decode_numerical_selection(
            self.model_predict(msg), 0, len(msg.available_moves) - 1)
        from_clearing, to_clearing, all_units = msg.available_moves[move_choice_idx]
        if len(all_units) == 1:
            units = all_units
        else:
            msg.type = GameMessages.MOVE_UNITS_MESSAGE
            units = all_units[:decode_numerical_selection(
                self.model_predict(msg), 1, len(all_units))]
        return MoveResponse(from_clearing, to_clearing, units)

    def _handle_crafting(self, msg: CraftMessage) -> CraftResponse:
        return CraftResponse(decode_single_selection(self.model_predict(msg), msg.crafting_options))

    def _handle_dominance_choice(self, msg: ChooseDominanceMessage) -> ChooseDominanceResponse:
        return ChooseDominanceResponse(decode_single_selection(self.model_predict(msg), msg.available_cards))

    def _handle_action_choice(self, msg: ActionChoiceMessage) -> ActionChoiceResponse:
        return ActionChoiceResponse(decode_single_selection(self.model_predict(msg), msg.available_actions))

    def _handle_battle_clearing_choice(self, msg: BattleClearingChoiceMessage) -> BattleClearingChoiceResponse:
        return BattleClearingChoiceResponse(decode_single_selection(self.model_predict(msg), msg.available_clearings))

    def _handle_battle_target_choice(self, msg: BattleTargetChoiceMessage) -> BattleTargetResponse:
        return BattleTargetResponse(decode_single_selection(self.model_predict(msg), msg.battle_target_list))

    def _handle_discard_choice(self, msg: DiscardChoiceMessage) -> DiscardChoiceResponse:
        return DiscardChoiceResponse(decode_multiple_selection(self.model_predict(msg), msg.discard_options, msg.num_to_discard))

    def _handle_triggerer_outrage_message(self, msg: TriggererOutrageMessage) -> TriggererOutrageResponse:
        return TriggererOutrageResponse(decode_single_selection(self.model_predict(msg), msg.valid_cards))

    def _handle_keep_clearing_choice(self, msg: KeepClearingMessage) -> KeepClearingResponse:
        return KeepClearingResponse(decode_single_selection(self.model_predict(msg), msg.available_clearings))

    def _handle_march_1_choice(self, msg: March1Message) -> March1Response:
        move_choice_idx = decode_numerical_selection(
            self.model_predict(msg), 0, len(msg.available_moves) - 1)
        from_clearing, to_clearing, all_units = msg.available_moves[move_choice_idx]
        if len(all_units) == 1:
            units = all_units
        else:
            msg.type = GameMessages.MARCH_1_UNITS_MESSAGE
            units = all_units[:decode_numerical_selection(
                self.model_predict(msg), 1, len(all_units))]
        return March1Response(from_clearing, to_clearing, units)

    def _handle_march_2_choice(self, msg: March2Message) -> March2Response:

        msg.type = GameMessages.MARCH_2_CHOICE_MESSAGE
        if decode_binary_choice(self.model_predict(msg)):
            print(" - Not performing second march movement")
            return March2Response(None, None, None)
        msg.type = GameMessages.MARCH_2_MESSAGE
        move_choice_idx = decode_numerical_selection(
            self.model_predict(msg), 0, len(msg.available_moves) - 1)
        from_clearing, to_clearing, all_units = msg.available_moves[move_choice_idx]
        if len(all_units) == 1:
            units = all_units
        else:
            msg.type = GameMessages.MARCH_2_UNITS_MESSAGE
            units = all_units[:decode_numerical_selection(
                self.model_predict(msg), 1, len(all_units))]
        return March2Response(from_clearing, to_clearing, units)

    def _handle_overwork_choice(self, msg: OverworkMessage) -> OverworkResponse:
        chosen_clearing = decode_single_selection(
            self.model_predict(msg), msg.available_clearings)
        msg.type = GameMessages.OVERWORK_DISCARD_MESSAGE
        chosen_discard = decode_single_selection(self.model_predict(msg), [
                                                 card for card in msg.hand if card.suit == Suits.BIRD or card.suit == chosen_clearing.get_suit()])
        return OverworkResponse(chosen_discard, chosen_clearing)

    def _handle_marquise_building_choice(self, msg: MarquiseBuildingMessage) -> MarquiseBuildingResponse:
        clearing = decode_single_selection(
            self.model_predict(msg), list(msg.clearing_building_options))
        msg.type = GameMessages.MARQUISE_BUILDING_TYPE_MESSAGE
        building_type = decode_single_selection(
            self.model_predict(msg), msg.clearing_building_options[clearing])
        return MarquiseBuildingResponse(clearing, building_type)

    def _handle_wood_removal_choice(self, msg: WoodRemovalMessage) -> WoodRemovalResponse:
        return WoodRemovalResponse(decode_multiple_selection(self.model_predict(msg), msg.wood_list, msg.cost))

    def _handle_marquise_building_setup_choice(self, msg: MarquiseBuildingSetupMessage) -> MarquiseBuildingSetupResponse:
        available_clearings = msg.available_clearings
        clearings_to_slots = {
            clearing: sum(1 for slot in clearing.slots if slot is None) for clearing in msg.available_clearings
        }
        building_clearings = []  # Sawmill, Recruiter, Workshop
        for message in [GameMessages.MARQUISE_SETUP_SAWMILL_MESSAGE, GameMessages.MARQUISE_SETUP_RECRUITER_MESSAGE, GameMessages.MARQUISE_SETUP_WORKSHOP_MESSAGE]:
            msg.type = message
            building_clearing = decode_single_selection(
                self.model_predict(msg), available_clearings)
            clearings_to_slots[building_clearing] -= 1
            if clearings_to_slots[building_clearing] <= 0:
                available_clearings.remove(building_clearing)
            building_clearings.append(building_clearing)
        return MarquiseBuildingSetupResponse(sawmill_clearing=building_clearings[0], recruiter_clearing=building_clearings[1], workshop_clearing=building_clearings[2])

    def _handle_marquise_spend_bird_card_choice(self, msg: MarquiseSpendBirdCardMessage) -> MarquiseSpendBirdCardResponse:
        return MarquiseSpendBirdCardResponse(decode_single_selection(self.model_predict(msg), msg.bird_cards))

    def _handle_field_hospital_choice(self, msg: FieldHospitalMessage) -> FieldHospitalResponse:
        return FieldHospitalResponse(decode_single_selection(self.model_predict(msg), msg.available_cards))
