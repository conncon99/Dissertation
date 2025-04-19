from __future__ import annotations
from src.controllers.base_controllers.controller import Controller
from src.controllers.base_controllers.action_decoder import Decoder
from src.controllers.nn_controllers.masked_policy_model import TorchActionMaskModel
from src.controllers.nn_controllers.observation_space_encoder import ObservationSpace
from gymnasium import spaces
from src.controllers.nn_controllers.mask import Mask
import numpy as np

import torch
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.controllers.messages.game_messages import GameMessage


class NN_Controller(Controller):

    def __init__(self, faction_name):
        super().__init__()
        model_path = f"training/checkpoints/policies/{faction_name}/model/model.pt"
        self.mask = Mask()
        self.model: TorchActionMaskModel = torch.load(
            model_path, weights_only=False)
        self.model.eval()
        B = 1
        self.h = torch.zeros(B, self.model.lstm_size)
        self.c = torch.zeros(B, self.model.lstm_size)

        self.state = [self.h, self.c]

    def reset_state(self):
        self.state = [torch.zeros_like(self.h), torch.zeros_like(self.c)]

    def send_game_message(self, msg: GameMessage):
        obs = ObservationSpace.encode_game_state(
            msg.game_state, msg.type, msg.action_group).clip(0, 1).astype(np.float32)
        action_mask = np.array(self.mask.create_mask(
            msg), dtype=np.float32).clip(0, 1)

        obs_dict = {
            "observations": obs,
            "action_mask":  action_mask,
        }

        inputs = {"obs": {
            k: torch.from_numpy(v).unsqueeze(0) for k, v in obs_dict.items()
        }}

        seq_lens = torch.tensor([1])

        with torch.no_grad():
            logits, next_state = self.model(
                inputs, self.state, seq_lens)

        self.state = next_state

        action_id = torch.argmax(logits, dim=1).item()

        return Decoder.decode(action_id, msg)

    # region Unimplemented Handlers

    def _handle_faction_messages(self, msg):
        raise NotImplementedError

    def _handle_battle_card_message(self, msg):
        raise NotImplementedError

    def _handle_ambushes(self, msg):
        raise NotImplementedError

    def _handle_tax_collector(self, msg):
        raise NotImplementedError

    def _handle_stand_and_deliver(self, msg):
        raise NotImplementedError

    def _handle_claim_dominance_suit(self, msg):
        raise NotImplementedError

    def _handle_claim_dominance_card(self, msg):
        raise NotImplementedError

    def _handle_codebreakers(self, msg):
        raise NotImplementedError

    def _handle_piece_targeting(self, msg):
        raise NotImplementedError

    def _handle_better_burrow_bank(self, msg):
        raise NotImplementedError

    def _handle_move_from(self, msg):
        raise NotImplementedError

    def _handle_move_to(self, msg):
        raise NotImplementedError

    def _handle_move_units(self, msg):
        raise NotImplementedError

    def _handle_crafting(self, msg):
        raise NotImplementedError

    def _handle_dominance_choice(self, msg):
        raise NotImplementedError

    def _handle_action_choice(self, msg):
        raise NotImplementedError

    def _handle_battle_clearing_choice(self, msg):
        raise NotImplementedError

    def _handle_battle_target_choice(self, msg):
        raise NotImplementedError

    def _handle_discard_choice(self, msg):
        raise NotImplementedError

    def _handle_triggerer_outrage_message(self, msg):
        raise NotImplementedError

    # endregion


Marquise_NN_Controller = NN_Controller("marquise")
Eyrie_NN_Controller = NN_Controller("eyrie")
Alliance_NN_Controller = NN_Controller("woodland_alliance")
Vagabond_NN_Controller = NN_Controller("vagabond")
