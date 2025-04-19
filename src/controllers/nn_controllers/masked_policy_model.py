from typing import Dict
import torch
import numpy as np
from torch import nn
from ray.rllib.models.torch.torch_modelv2 import TorchModelV2
import logging
from ray.rllib.utils.annotations import override
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence


class TorchActionMaskModel(TorchModelV2, nn.Module):
    """PyTorch version of above ActionMaskingModel."""

    def __init__(
        self,
        obs_space,
        action_space,
        num_outputs,
        model_config,
        name,
        **kwargs,
    ):
        TorchModelV2.__init__(self, obs_space, action_space,
                              num_outputs, model_config, name)
        nn.Module.__init__(self)
        self.logger = logging.getLogger()
        orig_space = getattr(obs_space, "original_space", obs_space)
        self.obs_size = orig_space["observations"].shape[0]
        self.num_outputs = num_outputs
        self.lstm_size = model_config["custom_model_config"].get(
            "lstm_hidden_size", 256)
        fc_layer_sizes = model_config["custom_model_config"].get(
            "fc_layer_sizes", [512, 256])
        self.no_masking = model_config["custom_model_config"].get(
            "no_masking", False)

        # LSTM Layer
        self.lstm = nn.LSTM(self.obs_size, self.lstm_size, batch_first=True)

        # Fully Connected Layers
        fc_layers = []
        input_dim = self.lstm_size

        for size in fc_layer_sizes:
            fc_layers.append(nn.Linear(input_dim, size))
            fc_layers.append(nn.ReLU())
            input_dim = size
        fc_layers.append(nn.Linear(input_dim, num_outputs)
                         )  # final layer = action logits
        self.policy_net = nn.Sequential(*fc_layers)

        self.value_net = nn.Sequential(
            nn.Linear(self.lstm_size, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )

        self._value_out = None

    @override(TorchModelV2)
    def forward(self, input_dict, state, seq_lens):

        obs_flat = input_dict["obs"]["observations"]
        action_mask = input_dict["obs"].get("action_mask", None)

        if action_mask is None:
            self.logger.warning("No Action Mask Found, May lead to errors")

        B = len(seq_lens)
        T = obs_flat.size(0) // B
        obs_time = obs_flat.view(B, T, self.obs_size)

        # Build packed sequence so LSTM skips padding efficiently.
        packed = pack_padded_sequence(
            obs_time,
            lengths=torch.as_tensor(seq_lens, device=obs_flat.device),
            batch_first=True,
            enforce_sorted=False,
        )

        # Prepare previous hidden state: RLlib supplies [B, hidden]; need [1, B, hidden]
        hx = state[0].unsqueeze(0)
        cx = state[1].unsqueeze(0)

        packed_out, (h_n, c_n) = self.lstm(packed, (hx, cx))
        unpacked, _ = pad_packed_sequence(
            packed_out, batch_first=True)  # [B, T, hidden]
        # Flatten back to [T*B, hidden]
        lstm_out_flat = unpacked.reshape(-1, self.lstm_size)

        # Policy logits and value predictions (also flattened)
        logits_flat = self.policy_net(lstm_out_flat)
        value_flat = self.value_net(lstm_out_flat).squeeze(1)

        self._value_out = value_flat  # store for value_function()

        # Apply action mask if provided
        if not self.no_masking and action_mask is not None:
            logits_flat = torch.where(
                action_mask > 0.5,
                logits_flat,
                torch.tensor(-float("inf"), device=logits_flat.device),
            )
            # Fallback: if a row has no legal actions, use unmasked logits
            invalid_rows = (action_mask > 0.5).sum(dim=1) == 0
            logits_flat[invalid_rows] = self.policy_net(lstm_out_flat)[
                invalid_rows]

        # Return logits and the *next* state (last hidden for each sequence)
        return logits_flat, [h_n.squeeze(0), c_n.squeeze(0)]

    @override(TorchModelV2)
    def value_function(self):
        return self._value_out

    @override(TorchModelV2)
    def get_initial_state(self):
        return [
            torch.zeros(self.lstm_size, dtype=torch.float32),
            torch.zeros(self.lstm_size, dtype=torch.float32),
        ]
