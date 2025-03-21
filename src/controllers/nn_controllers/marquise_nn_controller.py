from __future__ import annotations
from controllers.base_controllers.marquise_controller import MarquiseController
from controllers.nn_controllers.observation_space_encoder import ObservationSpace
from controllers.messages.game_messages import *
from controllers.messages.controller_messages import *
from controllers.nn_controllers.action_space_decoder import *
from controllers.messages.game_messages import GameMessage
import numpy as np
from utils.root_types import Suits
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from controllers.nn_controllers.faction_net import DQNAgent
    from utils.game_state import GameState
import torch
import copy


class MarquiseNNController(MarquiseController):

    def __init__(self, model: DQNAgent):
        self.model = model
        self.prev_state = None
        self.prev_action = None
        self.prev_mask = None
        self.prev_marquise = None
        self.masks = Masker(self.model.action_size)

    def model_predict(self, msg: GameMessage, mask: List[bool]):
        observation = ObservationSpace.encode_game_state(
            msg.game_state, msg.type, msg.action_group)

        # Query PPO to get a 54-length vector in range [0,1]
        observation_tensor = torch.tensor(
            # Add batch dimension
            observation, dtype=torch.float32).unsqueeze(0)
        with torch.no_grad():
            action = self.model.act(
                observation_tensor, mask)
        if self.prev_state is not None:
            self.model.remember(self.prev_state, self.prev_action,
                                self.calculate_reward(msg.game_state), observation, self.prev_mask, False)
        self.prev_state = observation
        self.prev_action = action
        self.prev_mask = mask
        self.prev_marquise = copy.copy(msg.game_state.marquise)
        return action

    def calculate_reward(self, state: GameState):
        # Gets difference in vp and provides a penalty for taking a turn
        TURN_PENALTY = 0.1
        if state.marquise.dominance is None:
            delta_points = state.marquise.victory_points - self.prev_marquise.victory_points
            return delta_points - TURN_PENALTY
        return -100

    def _handle_battle_card_message(self, msg: BattleUseCardMessage) -> BattleUseCardResponse:
        return BattleUseCardResponse(decode_binary_choice(self.model_predict(msg, self.masks.binary_mask())))

    def _handle_ambushes(self, msg: AmbushMessage) -> AmbushResponse:
        return AmbushResponse(decode_card_output(self.model_predict(msg, self.masks.card_mask(msg.available_ambush_cards, allow_none=True))))

    def _handle_tax_collector(self, msg: TaxCollectorMessage) -> TaxCollectorResponse:
        return TaxCollectorResponse(decode_warrior_output(self.model_predict(msg, self.masks.warrior_mask(msg.available_units))))

    def _handle_stand_and_deliver(self, msg: StandAndDeliverMessage) -> StandAndDeliverResponse:
        return StandAndDeliverResponse(decode_faction_output(self.model_predict(msg, self.masks.faction_mask(msg.available_players, msg.game_state)), msg.game_state))

    def _handle_claim_dominance_suit(self, msg: ClaimDominanceSuitMessage) -> ClaimDominanceSuitResponse:
        return ClaimDominanceSuitResponse(decode_card_output(self.model_predict(msg, self.masks.card_mask(msg.available_dominance_cards))))

    def _handle_claim_dominance_card(self, msg: ClaimDominanceCardMessage) -> ClaimDominanceCardResponse:
        return ClaimDominanceCardResponse(decode_card_output(self.model_predict(msg, self.masks.card_mask(msg.available_discard_cards))))

    def _handle_codebreakers(self, msg: CodebreakersMessage) -> CodebreakersResponse:
        return CodebreakersResponse(decode_faction_output(self.model_predict(msg, self.masks.faction_mask(msg.available_players, msg.game_state)), msg.game_state))

    def _handle_battle_end(self, msg):
        raise NotImplementedError

    def _handle_piece_targeting(self, msg: PieceTargetingMessage) -> PieceTargetingResponse:
        return PieceTargetingResponse(decode_piece_output(self.model_predict(msg, self.masks.piece_mask(msg.targets)), msg.game_state))

    def _handle_better_burrow_bank(self, msg: BetterBurrowBankMessage) -> BetterBurrowBankResponse:
        return BetterBurrowBankResponse(decode_faction_output(self.model_predict(msg, self.masks.faction_mask(msg.available_players, msg.game_state)), msg.game_state))

    def _handle_movement(self, msg: MoveMessage) -> MoveResponse:

        from_clearings = [move[0] for move in msg.available_moves]

        from_clearing = decode_clearing_output(self.model_predict(
            msg, self.masks.clearing_mask(from_clearings, msg.game_state)), msg.game_state)

        to_clearings = [move[1]
                        for move in msg.available_moves if move[0] == from_clearing]

        to_clearing = decode_clearing_output(self.model_predict(
            msg, self.masks.clearing_mask(to_clearings, msg.game_state)), msg.game_state)

        for movement in msg.available_moves:
            if movement[0] == from_clearing and movement[1] == to_clearing:
                all_units = movement[2]
                break

        if len(all_units) == 1:
            units = all_units
        else:
            msg.type = GameMessages.MOVE_UNITS_MESSAGE
            units = all_units[:1 + decode_numerical_selection(
                self.model_predict(msg, len(all_units)))]
        return MoveResponse(from_clearing, to_clearing, units)

    def _handle_crafting(self, msg: CraftMessage) -> CraftResponse:
        return CraftResponse(decode_card_output(self.model_predict(msg, self.masks.card_mask(msg.crafting_options))))

    def _handle_dominance_choice(self, msg: ChooseDominanceMessage) -> ChooseDominanceResponse:
        return ChooseDominanceResponse(decode_card_output(self.model_predict(msg, self.masks.card_mask(msg.available_cards))))

    def _handle_action_choice(self, msg: ActionChoiceMessage) -> ActionChoiceResponse:
        return ActionChoiceResponse(decode_action_output(self.model_predict(msg, self.masks.action_mask(msg.available_actions)), self.model.action_size, msg.action_group))

    def _handle_battle_clearing_choice(self, msg: BattleClearingChoiceMessage) -> BattleClearingChoiceResponse:
        return BattleClearingChoiceResponse(decode_clearing_output(self.model_predict(msg, self.masks.clearing_mask(msg.available_clearings, msg.game_state)), msg.game_state))

    def _handle_battle_target_choice(self, msg: BattleTargetChoiceMessage) -> BattleTargetResponse:
        return BattleTargetResponse(decode_faction_output(self.model_predict(msg, self.masks.faction_mask(msg.battle_target_list, msg.game_state)), msg.game_state))

    def _handle_discard_choice(self, msg: DiscardChoiceMessage) -> DiscardChoiceResponse:
        return DiscardChoiceResponse(decode_card_output(self.model_predict(msg, self.masks.card_mask(msg.discard_options))))

    def _handle_triggerer_outrage_message(self, msg: TriggererOutrageMessage) -> TriggererOutrageResponse:
        return TriggererOutrageResponse(decode_card_output(self.model_predict(msg, self.masks.card_mask(msg.valid_cards))))

    def _handle_keep_clearing_choice(self, msg: KeepClearingMessage) -> KeepClearingResponse:
        return KeepClearingResponse(decode_clearing_output(self.model_predict(msg, self.masks.clearing_mask(msg.available_clearings, msg.game_state)), msg.game_state))

    def _handle_march_1_choice(self, msg: March1Message) -> March1Response:
        from_clearings = [move[0] for move in msg.available_moves]

        from_clearing = decode_clearing_output(self.model_predict(
            msg, self.masks.clearing_mask(from_clearings, msg.game_state)), msg.game_state)

        to_clearings = [move[1]
                        for move in msg.available_moves if move[0] == from_clearing]

        to_clearing = decode_clearing_output(self.model_predict(
            msg, self.masks.clearing_mask(to_clearings, msg.game_state)), msg.game_state)

        for movement in msg.available_moves:
            if movement[0] == from_clearing and movement[1] == to_clearing:
                all_units = movement[2]
                break
        if len(all_units) == 1:
            units = all_units
        else:
            msg.type = GameMessages.MARCH_1_UNITS_MESSAGE
            units = all_units[:1 + decode_numerical_selection(
                self.model_predict(msg, len(all_units)))]
        return March1Response(from_clearing, to_clearing, units)

    def _handle_march_2_choice(self, msg: March2Message) -> March2Response:

        msg.type = GameMessages.MARCH_2_CHOICE_MESSAGE
        if decode_binary_choice(self.model_predict(msg, 2)):
            print(" - Not performing second march movement")
            return March2Response(None, None, None)
        msg.type = GameMessages.MARCH_2_MESSAGE

        from_clearings = [move[0] for move in msg.available_moves]

        from_clearing = decode_clearing_output(self.model_predict(
            msg, self.masks.clearing_mask(from_clearings, msg.game_state)), msg.game_state)

        to_clearings = [move[1]
                        for move in msg.available_moves if move[0] == from_clearing]

        to_clearing = decode_clearing_output(self.model_predict(
            msg, self.masks.clearing_mask(to_clearings, msg.game_state)), msg.game_state)

        for movement in msg.available_moves:
            if movement[0] == from_clearing and movement[1] == to_clearing:
                all_units = movement[2]
                break

        if len(all_units) == 1:
            units = all_units
        else:
            msg.type = GameMessages.MARCH_2_UNITS_MESSAGE
            units = all_units[: 1 + decode_numerical_selection(
                self.model_predict(msg, len(all_units)))]
        return March2Response(from_clearing, to_clearing, units)

    def _handle_overwork_choice(self, msg: OverworkMessage) -> OverworkResponse:
        chosen_clearing = decode_clearing_output(
            self.model_predict(msg, self.masks.clearing_mask(msg.available_clearings, msg.game_state)), msg.game_state)
        msg.type = GameMessages.OVERWORK_DISCARD_MESSAGE
        card_list = [card for card in msg.hand if card.suit ==
                     Suits.BIRD or card.suit == chosen_clearing.get_suit()]
        chosen_discard = decode_card_output(
            self.model_predict(msg, self.masks.card_mask(card_list)))
        return OverworkResponse(chosen_discard, chosen_clearing)

    def _handle_marquise_building_choice(self, msg: MarquiseBuildingMessage) -> MarquiseBuildingResponse:
        clearing = decode_clearing_output(
            self.model_predict(msg, self.masks.clearing_mask(list(msg.clearing_building_options), msg.game_state)), msg.game_state)
        msg.type = GameMessages.MARQUISE_BUILDING_TYPE_MESSAGE

        building_type = decode_marquise_building_types(
            self.model_predict(msg, self.masks.marquise_building_type_mask(msg.clearing_building_options[clearing])))
        return MarquiseBuildingResponse(clearing, building_type)

    def _handle_wood_removal_choice(self, msg: WoodRemovalMessage) -> WoodRemovalResponse:
        return WoodRemovalResponse(decode_wood_output(self.model_predict(msg, self.masks.wood_mask(msg.wood_list)), msg.game_state))

    def _handle_marquise_building_setup_choice(self, msg: MarquiseBuildingSetupMessage) -> MarquiseBuildingSetupResponse:
        available_clearings = msg.available_clearings
        clearings_to_slots = {
            clearing: sum(1 for slot in clearing.slots if slot is None) for clearing in msg.available_clearings
        }
        building_clearings = []  # Sawmill, Recruiter, Workshop
        for message in [GameMessages.MARQUISE_SETUP_SAWMILL_MESSAGE, GameMessages.MARQUISE_SETUP_RECRUITER_MESSAGE, GameMessages.MARQUISE_SETUP_WORKSHOP_MESSAGE]:
            msg.type = message
            building_clearing = decode_clearing_output(
                self.model_predict(msg, self.masks.clearing_mask(msg.available_clearings, msg.game_state)), msg.game_state)
            clearings_to_slots[building_clearing] -= 1
            if clearings_to_slots[building_clearing] <= 0:
                available_clearings.remove(building_clearing)
            building_clearings.append(building_clearing)
        return MarquiseBuildingSetupResponse(sawmill_clearing=building_clearings[0], recruiter_clearing=building_clearings[1], workshop_clearing=building_clearings[2])

    def _handle_marquise_spend_bird_card_choice(self, msg: MarquiseSpendBirdCardMessage) -> MarquiseSpendBirdCardResponse:
        return MarquiseSpendBirdCardResponse(decode_card_output(self.model_predict(msg, self.masks.card_mask(msg.bird_cards))))

    def _handle_field_hospital_choice(self, msg: FieldHospitalMessage) -> FieldHospitalResponse:
        return FieldHospitalResponse(decode_card_output(self.model_predict(msg, self.masks.card_mask(msg.available_cards, allow_none=True))))
