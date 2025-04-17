from typing import Dict
import torch
import numpy as np
from torch import nn
from ray.rllib.models.torch.torch_modelv2 import TorchModelV2
from ray.rllib.models.torch.fcnet import FullyConnectedNetwork as TorchFC
from src.controllers.nn_controllers.mask import Mask
import logging


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
        super().__init__(obs_space, action_space, num_outputs, model_config, name, **kwargs)
        nn.Module.__init__(self)
        orig_space = getattr(obs_space, "original_space", obs_space)
        self.logger = logging.getLogger(__name__)
        self.logger.debug(orig_space)

        TorchModelV2.__init__(
            self, obs_space, action_space, num_outputs, model_config, name, **kwargs
        )
        nn.Module.__init__(self)

        self.internal_model = TorchFC(
            orig_space["observations"],
            action_space,
            num_outputs,
            model_config,
            name + "_internal",
        )

        # disable action masking --> will likely lead to invalid actions
        self.no_masking = model_config.get(
            "custom_model_config", {}).get("no_masking", False)

    def forward(self, input_dict, state, seq_lens):
        # Extract the available actions tensor from the observation.
        self.logger.debug("FORWARD CALLED")
        obs = input_dict["obs"]
        if "action_mask" in obs:
            self.logger.debug("DEBUG shape, dtype of action_mask:", obs["action_mask"].shape, obs["action_mask"].dtype,
                              " min=", obs["action_mask"].min().item(), " max=", obs["action_mask"].max().item())
        else:
            self.logger.warning("NO ACTION MASK FOUND")
        if "observations" in obs:
            self.logger.debug("DEBUG shape, dtype of observations:", obs["observations"].shape, obs["observations"].dtype,
                              " min=", obs["observations"].min().item(), " max=", obs["observations"].max().item())
        else:
            self.logger.warning("NO OBS FOUND")

        action_mask = input_dict["obs"]["action_mask"]

        # Compute the unmasked logits.
        logits, _ = self.internal_model(
            {"obs": input_dict["obs"]["observations"]}, state, seq_lens)

        # If action masking is disabled, directly return unmasked logits
        if self.no_masking:
            return logits, state

        # Convert action_mask into a [0.0 || -inf]-type mask.
        self.logger.debug(action_mask)
        masked_logits = torch.where(
            action_mask > 0.5,
            logits,
            torch.tensor(-np.inf, device=logits.device)
        )

        batch_size = action_mask.shape[0]
        for b in range(batch_size):
            if (action_mask[b] > 0.5).sum() == 0:
                # fallback for row b
                masked_logits[b] = logits[b]

        # Return masked logits.
        self.logger.debug(f"Logits: {masked_logits}")
        return masked_logits, state

    def value_function(self):
        return self.internal_model.value_function()
