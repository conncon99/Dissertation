from typing import Dict, Union
from ray.rllib.algorithms.dqn.torch.default_dqn_torch_rl_module import DefaultDQNRLModule, QF_LOGITS, QF_PROBS, QF_PREDS, ATOMS
from ray.rllib.utils.annotations import override
from ray.rllib.utils.framework import get_activation_fn
from ray.rllib.models.torch.modules.noisy_layer import NoisyLayer
from ray.rllib.models.torch.misc import SlimFC
from ray.rllib.core.columns import Columns
from ray.rllib.core.rl_module.rl_module import RLModule
from ray.rllib.core.rl_module.torch.torch_rl_module import TorchRLModule
import torch.nn.functional as F
from ray.rllib.utils.typing import TensorType
import torch.nn as nn
from ray.rllib.algorithms.dqn.dqn_torch_model import DQNTorchModel
import torch


from gymnasium.spaces import Box, Discrete
from ray.rllib.algorithms.dqn import DQNConfig
from ray.rllib.algorithms.dqn.dqn_torch_model import DQNTorchModel
from ray.rllib.models import ModelCatalog
from ray.rllib.models.torch.fcnet import FullyConnectedNetwork as TorchFC
from ray.rllib.utils.framework import try_import_torch
from ray.rllib.utils.torch_utils import FLOAT_MAX, FLOAT_MIN
torch, nn = try_import_torch()


class DQNActionMaskModel(DQNTorchModel):
    """PyTorch version of above ParametricActionsModel."""

    def __init__(
        self,
        obs_space: Box,
        action_space: Discrete,
        num_outputs,
        model_config,
        name,
        **kw,
    ):
        DQNTorchModel.__init__(
            self, obs_space, action_space, num_outputs, model_config, name, **kw
        )

        obs_len = obs_space.shape[0] - action_space.n

        orig_obs_space = Box(
            shape=(
                obs_len,), low=obs_space.low[:obs_len], high=obs_space.high[:obs_len]
        )
        self.action_embed_model = TorchFC(
            orig_obs_space,
            action_space,
            action_space.n,
            model_config,
            name + "_action_embed",
        )

    def forward(self, input_dict, state, seq_lens):
        action_mask = input_dict["obs"]["action_mask"]
        action_scores, _ = self.action_embed_model(
            {"obs": input_dict["obs"]["observations"]}
        )
        inf_mask = torch.clamp(torch.log(action_mask), min=FLOAT_MIN)
        return action_scores + inf_mask, state

    def value_function(self):
        return self.action_embed_model.value_function()


class MaskedDQNTorchModel(DQNTorchModel):

    def __init__(self, observation_space, action_space, num_outputs, model_config, name, *, q_hiddens=..., dueling=False, dueling_activation="relu", num_atoms=1, use_noisy=False, v_min=-10, v_max=10, sigma0=0.5, add_layer_norm=False):
        super().__init__(observation_space, action_space, num_outputs, model_config, name, q_hiddens=q_hiddens, dueling=dueling,
                         dueling_activation=dueling_activation, num_atoms=num_atoms, use_noisy=use_noisy, v_min=v_min, v_max=v_max, sigma0=sigma0, add_layer_norm=add_layer_norm)

    def forward(self, input_dict, state, seq_lens):
        self._last_obs = input_dict["obs"]
        return super().forward(input_dict, state, seq_lens)

    def get_q_value_distributions(self, model_out):
        output = super().get_q_value_distributions(model_out)
        q_values = output[0]

        if hasattr(self, "_last_obs") and "action_mask" in self._last_obs:
            mask = self._last_obs["action_mask"]
            inf_mask = torch.clamp(torch.log(mask), min=-1e8)
            q_values = q_values + inf_mask

        return (q_values,) + output[1:]


class MaskedRainbowDQNRLModule(DefaultDQNRLModule):
    def _qf_forward_helper(
        self,
        batch: Dict[str, TensorType],  # type: ignore
        encoder,
        head: Union[torch.nn.Module, Dict[str, torch.nn.Module]],
    ) -> Dict[str, TensorType]:  # type: ignore
        obs = batch[Columns.OBS]
        mask = batch.get("action_mask", None)

        # Encode observations
        features = encoder(obs)

        if self.uses_dueling:
            af = head["af"](features)
            vf = head["vf"](features)
            af = af.view(-1, self.action_space.n, self.num_atoms)
            vf = vf.view(-1, 1, self.num_atoms)
            logits = af - af.mean(dim=1, keepdim=True) + vf
        else:
            logits = head(features)
            logits = logits.view(-1, self.action_space.n, self.num_atoms)

        # Softmax to get probabilities over atoms
        if mask is not None:
            # Set logits of invalid actions to -1e10 before softmax
            inf_mask = (mask == 0).unsqueeze(-1).expand_as(logits)
            logits = logits.masked_fill(inf_mask, -1e10)

        probs = F.softmax(logits, dim=-1)

        # Support atoms
        z = torch.linspace(self.v_min, self.v_max,
                           self.num_atoms, device=logits.device)

        # Compute expected Q-values
        q_values = torch.sum(probs * z, dim=-1)

        out = {
            "qf_preds": q_values,
            "atoms": z,
            "qf_logits": logits,
            "qf_probs": probs,
        }

        return out
