"""Per-faction actor-critic networks, evaluated for all factions in one batched pass."""
from __future__ import annotations
import math

import torch
from torch import nn

MASKED_LOGIT = -1e9


class EnsembleLinear(nn.Module):
    """``members`` independent linear layers applied with one batched matmul."""

    def __init__(self, members: int, in_features: int, out_features: int, gain: float = math.sqrt(2)) -> None:
        super().__init__()
        self.weight = nn.Parameter(torch.empty(members, in_features, out_features))
        self.bias = nn.Parameter(torch.zeros(members, 1, out_features))
        for w in self.weight:
            nn.init.orthogonal_(w, gain)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (members, batch, in) -> (members, batch, out)
        return torch.baddbmm(self.bias, x, self.weight)


class EnsembleLayerNorm(nn.Module):
    def __init__(self, members: int, features: int) -> None:
        super().__init__()
        self.features = features
        self.weight = nn.Parameter(torch.ones(members, 1, features))
        self.bias = nn.Parameter(torch.zeros(members, 1, features))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return torch.nn.functional.layer_norm(x, (self.features,)) * self.weight + self.bias


class EnsembleMLP(nn.Module):
    def __init__(self, members: int, in_features: int, hidden: list[int], out_features: int, out_gain: float) -> None:
        super().__init__()
        sizes = [in_features] + hidden
        self.hidden = nn.ModuleList(EnsembleLinear(members, a, b) for a, b in zip(sizes[:-1], sizes[1:]))
        self.norms = nn.ModuleList(EnsembleLayerNorm(members, b) for b in hidden)
        self.out = EnsembleLinear(members, sizes[-1], out_features, gain=out_gain)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        for layer, norm in zip(self.hidden, self.norms):
            x = torch.relu(norm(layer(x)))
        return self.out(x)


class FactionActorCritic(nn.Module):
    """A separate actor and critic for each faction (critics see the full game state)."""

    def __init__(self, obs_dim: int, action_dim: int, factions: int = 4, hidden: list[int] = (512, 512)) -> None:
        super().__init__()
        self.factions = factions
        self.actor = EnsembleMLP(factions, obs_dim, list(hidden), action_dim, out_gain=0.01)
        self.critic = EnsembleMLP(factions, obs_dim, list(hidden), 1, out_gain=1.0)

    def _all(self, net: nn.Module, obs: torch.Tensor) -> torch.Tensor:
        return net(obs.unsqueeze(0).expand(self.factions, -1, -1))

    def values_all(self, obs: torch.Tensor) -> torch.Tensor:
        """Every faction's value estimate for each observation: (batch, factions)."""
        return self._all(self.critic, obs).squeeze(-1).transpose(0, 1)

    def forward(self, obs: torch.Tensor, agent: torch.Tensor, mask: torch.Tensor):
        """Masked logits and value of the acting faction for each row."""
        rows = torch.arange(obs.shape[0], device=obs.device)
        logits = self._all(self.actor, obs)[agent, rows]
        value = self._all(self.critic, obs)[agent, rows, 0]
        return logits.masked_fill(~mask, MASKED_LOGIT), value

    @torch.no_grad()
    def act(self, obs: torch.Tensor, agent: torch.Tensor, mask: torch.Tensor):
        logits, value = self(obs, agent, mask)
        logp_all = torch.log_softmax(logits.float(), dim=-1)
        # Gumbel-max sampling: one fused op instead of torch.distributions
        gumbel = -torch.log(-torch.log(torch.rand_like(logp_all).clamp_(1e-20, 1.0)))
        action = torch.argmax(logp_all + gumbel, dim=-1)
        return action, logp_all.gather(1, action[:, None])[:, 0], value.float()


def masked_logp_entropy(logits: torch.Tensor, mask: torch.Tensor, actions: torch.Tensor):
    logp_all = torch.log_softmax(logits.float(), dim=-1)
    probs = logp_all.exp()
    entropy = -(probs * logp_all).masked_fill(~mask, 0.0).sum(-1)
    return logp_all.gather(1, actions[:, None])[:, 0], entropy
