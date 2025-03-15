from __future__ import annotations
from controllers.base_controllers.marquise_controller import MarquiseController
from controllers.nn_controllers.observation_space_encoder import ObservationSpace
from controllers.messages.game_messages import *
from controllers.messages.controller_messages import *
from controllers.nn_controllers.action_space_decoder import *
from controllers.messages.game_messages import GameMessage
import numpy as np
from utils.root_types import Suits
from environments.ppo_trainer import PPOTrainer
import torch
from typing import TYPE_CHECKING


class MarquiseNNController(MarquiseController):

    def __init__(self, trainer: PPOTrainer):
        self.trainer = trainer

    def send_game_message(self, msg):
        return super().send_game_message(msg)

    def model_predict(self, msg: GameMessage):
        observation = ObservationSpace.encode_game_state(
            msg.game_state, msg.type, msg.action_group)

        obs_tensor = torch.tensor(
            observation, dtype=torch.float32, device=self.trainer.device).unsqueeze(0)

        with torch.no_grad():
            policy_output = self.trainer.model.policy(obs_tensor)

            if isinstance(policy_output, tuple):
                action_logits = policy_output[0]
            else:
                action_logits = policy_output

        return observation, action_logits.squeeze(0).cpu().numpy()

    def _handle_battle_card_message(self, msg: BattleUseCardMessage) -> BattleUseCardResponse:
        observation, action_logits = self.model_predict(msg)
        choice = decode_binary_choice(action_logits)
        self.trainer.store_step(observation, action_logits)
        return BattleUseCardResponse(choice)

    def _handle_ambushes(self, msg: AmbushMessage) -> AmbushResponse:
        observation, action_logits = self.model_predict(msg)
        choice = decode_single_selection(
            action_logits, msg.available_ambush_cards)
        self.trainer.store_step(observation, action_logits)
        return AmbushResponse(choice)

    def _handle_tax_collector(self, msg: TaxCollectorMessage) -> TaxCollectorResponse:
        observation, action_logits = self.model_predict(msg)
        choice = decode_single_selection(action_logits, msg.available_units)
        self.trainer.store_step(observation, action_logits)
        return TaxCollectorResponse(choice)

    def _handle_stand_and_deliver(self, msg: StandAndDeliverMessage) -> StandAndDeliverResponse:
        observation, action_logits = self.model_predict(msg)
        choice = decode_single_selection(action_logits, msg.available_players)
        self.trainer.store_step(observation, action_logits)
        return StandAndDeliverResponse(choice)

    def _handle_claim_dominance_suit(self, msg: ClaimDominanceSuitMessage) -> ClaimDominanceSuitResponse:
        observation, action_logits = self.model_predict(msg)
        choice = decode_single_selection(
            action_logits, msg.available_dominance_cards)
        self.trainer.store_step(observation, action_logits)
        return ClaimDominanceSuitResponse(choice)

    def _handle_claim_dominance_card(self, msg: ClaimDominanceCardMessage) -> ClaimDominanceCardResponse:
        observation, action_logits = self.model_predict(msg)
        choice = decode_single_selection(
            action_logits, msg.available_discard_cards)
        self.trainer.store_step(observation, action_logits)
        return ClaimDominanceCardResponse(choice)

    def _handle_codebreakers(self, msg: CodebreakersMessage) -> CodebreakersResponse:
        observation, action_logits = self.model_predict(msg)
        choice = decode_single_selection(action_logits, msg.available_players)
        self.trainer.store_step(observation, action_logits)
        return CodebreakersResponse(choice)

    def _handle_battle_end(self, msg):
        raise NotImplementedError

    def _handle_piece_targeting(self, msg: PieceTargetingMessage) -> PieceTargetingResponse:
        observation, action_logits = self.model_predict(msg)
        choices = decode_multiple_selection(
            action_logits, msg.targets, msg.remaining_dmg)
        self.trainer.store_step(observation, action_logits)
        return PieceTargetingResponse(choices)

    def _handle_better_burrow_bank(self, msg: BetterBurrowBankMessage) -> BetterBurrowBankResponse:
        observation, action_logits = self.model_predict(msg)
        choice = decode_single_selection(action_logits, msg.available_players)
        self.trainer.store_step(observation, action_logits)
        return BetterBurrowBankResponse(choice)

    def _handle_movement(self, msg: MoveMessage) -> MoveResponse:

        observation, action_logits = self.model_predict(msg)
        move_choice_idx = decode_numerical_selection(
            action_logits, 0, len(msg.available_moves) - 1)
        self.trainer.store_step(observation, action_logits)

        from_clearing, to_clearing, all_units = msg.available_moves[move_choice_idx]
        if len(all_units) == 1:
            units = all_units
        else:
            msg.type = GameMessages.MOVE_UNITS_MESSAGE
            observation, action_logits = self.model_predict(msg)
            unit_choice = decode_numerical_selection(
                action_logits, 1, len(all_units))
            self.trainer.store_step(observation, action_logits)
            units = all_units[:unit_choice]
        return MoveResponse(from_clearing, to_clearing, units)

    def _handle_crafting(self, msg: CraftMessage) -> CraftResponse:
        observation, action_logits = self.model_predict(msg)
        choice = decode_single_selection(action_logits, msg.crafting_options)
        self.trainer.store_step(observation, action_logits)
        return CraftResponse(choice)

    def _handle_dominance_choice(self, msg: ChooseDominanceMessage) -> ChooseDominanceResponse:
        observation, action_logits = self.model_predict(msg)
        choice = decode_single_selection(action_logits, msg.available_cards)
        self.trainer.store_step(observation, action_logits)
        return ChooseDominanceResponse(choice)

    def _handle_action_choice(self, msg: ActionChoiceMessage) -> ActionChoiceResponse:
        observation, action_logits = self.model_predict(msg)
        choice = decode_single_selection(
            action_logits, msg.available_actions)
        self.trainer.store_step(observation, action_logits)
        return ActionChoiceResponse(choice)

    def _handle_battle_clearing_choice(self, msg: BattleClearingChoiceMessage) -> BattleClearingChoiceResponse:
        observation, action_logits = self.model_predict(msg)
        choice = decode_single_selection(
            action_logits, msg.available_clearings)
        self.trainer.store_step(observation, action_logits)
        return BattleClearingChoiceResponse(choice)

    def _handle_battle_target_choice(self, msg: BattleTargetChoiceMessage) -> BattleTargetResponse:
        observation, action_logits = self.model_predict(msg)
        choice = decode_single_selection(action_logits, msg.battle_target_list)
        self.trainer.store_step(observation, action_logits)
        return BattleTargetResponse(choice)

    def _handle_discard_choice(self, msg: DiscardChoiceMessage) -> DiscardChoiceResponse:
        observation, action_logits = self.model_predict(msg)
        choices = decode_multiple_selection(
            action_logits, msg.discard_options, msg.num_to_discard)
        self.trainer.store_step(observation, action_logits)
        return DiscardChoiceResponse(choices)

    def _handle_triggerer_outrage_message(self, msg: TriggererOutrageMessage) -> TriggererOutrageResponse:
        observation, action_logits = self.model_predict(msg)
        choice = decode_single_selection(action_logits, msg.valid_cards)
        self.trainer.store_step(observation, action_logits)
        return TriggererOutrageResponse(choice)

    def _handle_keep_clearing_choice(self, msg: KeepClearingMessage) -> KeepClearingResponse:
        observation, action_logits = self.model_predict(msg)
        choice = decode_single_selection(
            action_logits, msg.available_clearings)
        self.trainer.store_step(observation, action_logits)
        return KeepClearingResponse(choice)

    def _handle_march_1_choice(self, msg: March1Message) -> March1Response:
        observation, action_logits = self.model_predict(msg)
        move_choice_idx = decode_numerical_selection(
            action_logits, 0, len(msg.available_moves) - 1)
        self.trainer.store_step(observation, action_logits)

        from_clearing, to_clearing, all_units = msg.available_moves[move_choice_idx]
        if len(all_units) == 1:
            units = all_units
        else:
            msg.type = GameMessages.MARCH_1_UNITS_MESSAGE

            observation, action_logits = self.model_predict(msg)
            unit_count = decode_numerical_selection(
                action_logits, 1, len(all_units))
            self.trainer.store_step(observation, action_logits)

            units = all_units[:unit_count]
        return March1Response(from_clearing, to_clearing, units)

    def _handle_march_2_choice(self, msg: March2Message) -> March2Response:

        msg.type = GameMessages.MARCH_2_CHOICE_MESSAGE
        observation, action_logits = self.model_predict(msg)
        self.trainer.store_step(observation, action_logits)
        if decode_binary_choice(action_logits):
            print(" - Not performing second march movement")
            return March2Response(None, None, None)
        msg.type = GameMessages.MARCH_2_MESSAGE

        observation, action_logits = self.model_predict(msg)
        move_choice_idx = decode_numerical_selection(
            action_logits, 0, len(msg.available_moves) - 1)
        self.trainer.store_step(observation, action_logits)

        from_clearing, to_clearing, all_units = msg.available_moves[move_choice_idx]

        if len(all_units) == 1:
            units = all_units
        else:
            msg.type = GameMessages.MARCH_2_UNITS_MESSAGE
            observation, action_logits = self.model_predict(msg)
            unit_count = decode_numerical_selection(
                action_logits, 1, len(all_units))
            self.trainer.store_step(observation, action_logits)
            units = all_units[:unit_count]
        return March2Response(from_clearing, to_clearing, units)

    def _handle_overwork_choice(self, msg: OverworkMessage) -> OverworkResponse:
        observation, action_logits = self.model_predict(msg)
        chosen_clearing = decode_single_selection(
            action_logits, msg.available_clearings)
        self.trainer.store_step(observation, action_logits)

        msg.type = GameMessages.OVERWORK_DISCARD_MESSAGE

        observation, action_logits = self.model_predict(msg)
        chosen_discard = decode_single_selection(action_logits, [
            card for card in msg.hand if card.suit == Suits.BIRD or card.suit == chosen_clearing.get_suit()])
        self.trainer.store_step(observation, action_logits)
        return OverworkResponse(chosen_discard, chosen_clearing)

    def _handle_marquise_building_choice(self, msg: MarquiseBuildingMessage) -> MarquiseBuildingResponse:

        observation, action_logits = self.model_predict(msg)
        clearing_choice = decode_single_selection(
            action_logits, list(msg.clearing_building_options))
        self.trainer.store_step(observation, action_logits)

        msg.type = GameMessages.MARQUISE_BUILDING_TYPE_MESSAGE

        observation, action_logits = self.model_predict(msg)
        building_type = decode_single_selection(
            action_logits, msg.clearing_building_options[clearing_choice])
        self.trainer.store_step(observation, action_logits)
        return MarquiseBuildingResponse(clearing_choice, building_type)

    def _handle_wood_removal_choice(self, msg: WoodRemovalMessage) -> WoodRemovalResponse:
        observation, action_logits = self.model_predict(msg)
        choices = decode_multiple_selection(
            action_logits, msg.wood_list, msg.cost)
        self.trainer.store_step(observation, action_logits)
        return WoodRemovalResponse(choices)

    def _handle_marquise_building_setup_choice(self, msg: MarquiseBuildingSetupMessage) -> MarquiseBuildingSetupResponse:
        available_clearings = msg.available_clearings
        clearings_to_slots = {
            clearing: sum(1 for slot in clearing.slots if slot is None) for clearing in msg.available_clearings
        }
        building_clearings = []  # Sawmill, Recruiter, Workshop
        for message in [GameMessages.MARQUISE_SETUP_SAWMILL_MESSAGE, GameMessages.MARQUISE_SETUP_RECRUITER_MESSAGE, GameMessages.MARQUISE_SETUP_WORKSHOP_MESSAGE]:
            msg.type = message
            observation, action_logits = self.model_predict(msg)
            building_clearing = decode_single_selection(
                action_logits, msg.available_clearings)
            self.trainer.store_step(observation, action_logits)
            clearings_to_slots[building_clearing] -= 1
            if clearings_to_slots[building_clearing] <= 0:
                available_clearings.remove(building_clearing)
            building_clearings.append(building_clearing)
        return MarquiseBuildingSetupResponse(sawmill_clearing=building_clearings[0], recruiter_clearing=building_clearings[1], workshop_clearing=building_clearings[2])

    def _handle_marquise_spend_bird_card_choice(self, msg: MarquiseSpendBirdCardMessage) -> MarquiseSpendBirdCardResponse:
        observation, action_logits = self.model_predict(msg)
        choice = decode_single_selection(action_logits, msg.bird_cards)
        self.trainer.store_step(observation, action_logits)
        return MarquiseSpendBirdCardResponse(choice)

    def _handle_field_hospital_choice(self, msg: FieldHospitalMessage) -> FieldHospitalResponse:
        observation, action_logits = self.model_predict(msg)
        choice = decode_single_selection(action_logits, msg.available_cards)
        self.trainer.store_step(observation, action_logits)
        return FieldHospitalResponse(choice)
