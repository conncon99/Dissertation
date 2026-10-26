"""Multi-agent PPO self-play for Root with action masking (run it with ``python -m rl.train_ppo``).

Each faction has its own actor and critic (critics see the full game state, as in MAPPO).
Games run in parallel worker processes (rl.vec_env); whichever games are waiting for a
decision are batched onto the GPU together. Every finished game is written to
runs/<run>/games/worker_XXX.jsonl and can be recreated with ``python -m rl.replay``.
"""
from __future__ import annotations
import argparse
import csv
import dataclasses
import json
import os
import time
from dataclasses import dataclass, field

import numpy as np
import torch
from torch.utils.tensorboard import SummaryWriter

from rl.model import FactionActorCritic, masked_logp_entropy
from rl.root_game import ACTION_DIM, FACTION_NAMES, NUM_FACTIONS, OBS_DIM
from rl.vec_env import AsyncRootVecEnv


@dataclass
class Config:
    run_name: str = field(default_factory=lambda: time.strftime("ppo_%Y%m%d_%H%M%S"))
    runs_dir: str = "runs"
    seed: int = 1
    # Several games per core keep the CPU busy while games wait for GPU inference
    num_envs: int = 6 * (os.cpu_count() or 4)
    total_decisions: int = 100_000_000
    rollout_decisions: int = 65_536
    epochs: int = 4
    minibatch: int = 4_096
    lr: float = 2.5e-4
    anneal_lr: bool = True
    gamma: float = 0.995
    gae_lambda: float = 0.95
    clip: float = 0.2
    ent_coef: float = 0.01
    vf_coef: float = 0.5
    max_grad_norm: float = 0.5
    target_kl: float = 0.03
    hidden: list = field(default_factory=lambda: [512, 512])
    normalize_rewards: bool = True
    turn_limit: int = 30
    settle_terminal_rewards: bool = True
    record_games: bool = True
    bf16: bool = True
    save_every: int = 10
    resume: str = ""


class RunningMeanStd:
    """Per-faction running variance of the discounted return, used to scale rewards."""

    def __init__(self, shape) -> None:
        self.mean = np.zeros(shape)
        self.var = np.ones(shape)
        self.count = 1e-4

    def update_faction(self, faction: np.ndarray, x: np.ndarray) -> None:
        for f in np.unique(faction):
            xs = x[faction == f]
            batch_mean, batch_var, n = xs.mean(), xs.var(), len(xs)
            delta = batch_mean - self.mean[f]
            total = self.count + n
            self.mean[f] += delta * n / total
            self.var[f] = (self.var[f] * self.count + batch_var * n + delta ** 2 * self.count * n / total) / total
        self.count += len(x) / NUM_FACTIONS

    def state_dict(self):
        return {"mean": self.mean, "var": self.var, "count": self.count}

    def load_state_dict(self, d):
        self.mean, self.var, self.count = d["mean"], d["var"], d["count"]


class Rollout:
    """Transitions in arrival order. Each faction's transitions in a game form a linked chain
    (``next_idx``) because factions act in an irregular order."""

    def __init__(self, capacity: int, num_envs: int) -> None:
        self.capacity = capacity
        self.obs = torch.zeros((capacity, OBS_DIM), dtype=torch.float32).pin_memory()
        self.mask = torch.zeros((capacity, ACTION_DIM), dtype=torch.bool).pin_memory()
        self.obs_np = self.obs.numpy()
        self.mask_np = self.mask.numpy()
        self.agent = np.zeros(capacity, np.int64)
        self.action = np.zeros(capacity, np.int64)
        self.logp = np.zeros(capacity, np.float32)
        self.value = np.zeros(capacity, np.float32)
        self.reward = np.zeros(capacity, np.float64)
        self.done = np.zeros(capacity, np.bool_)
        self.next_idx = np.full(capacity, -1, np.int64)
        self.boot_value = np.zeros(capacity, np.float32)
        # Latest transition of each faction in each game (-1: none yet)
        self.last = np.full((num_envs, NUM_FACTIONS), -1, np.int64)
        self.ptr = 0

    def reset(self) -> None:
        self.reward[:] = 0.0
        self.done[:] = False
        self.next_idx[:] = -1
        self.boot_value[:] = 0.0
        self.last[:] = -1
        self.ptr = 0

    def advantages(self, gamma: float, lam: float):
        n = self.ptr
        nxt, done = self.next_idx[:n], self.done[:n]
        value = self.value[:n].astype(np.float64)
        next_value = np.where(nxt >= 0, value[np.maximum(nxt, 0)], self.boot_value[:n])
        next_value[done] = 0.0
        delta = self.reward[:n] + gamma * next_value - value
        adv = np.zeros(n, np.float64)
        for t in range(n - 1, -1, -1):
            j = nxt[t]
            adv[t] = delta[t] + (gamma * lam * adv[j] if j >= 0 and not done[t] else 0.0)
        return adv, adv + value


class Trainer:

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.run_dir = os.path.join(cfg.runs_dir, cfg.run_name)
        self.ckpt_dir = os.path.join(self.run_dir, "checkpoints")
        os.makedirs(self.ckpt_dir, exist_ok=True)
        torch.manual_seed(cfg.seed)
        np.random.seed(cfg.seed)
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.amp = cfg.bf16 and self.device.type == "cuda"

        self.model = FactionActorCritic(OBS_DIM, ACTION_DIM, NUM_FACTIONS, cfg.hidden).to(self.device)
        self.optim = torch.optim.Adam(self.model.parameters(), lr=cfg.lr, eps=1e-5)
        self.ret_rms = RunningMeanStd(NUM_FACTIONS)
        self.update = 0
        self.decisions = 0
        self.games = 0
        if cfg.resume:
            self._load(cfg.resume)

        with open(os.path.join(self.run_dir, "config.json"), "w") as f:
            json.dump(dataclasses.asdict(cfg), f, indent=2)
        self.tb = SummaryWriter(os.path.join(self.run_dir, "tb"))
        self.csv_path = os.path.join(self.run_dir, "metrics.csv")

        self.rollout = Rollout(cfg.rollout_decisions, cfg.num_envs)
        self.ret = np.zeros((cfg.num_envs, NUM_FACTIONS))
        self.pending: set[int] = set()
        self.ep_stats: list[dict] = []
        self.env = AsyncRootVecEnv(cfg.num_envs, os.path.join(self.run_dir, "games"), run_seed=cfg.seed,
                                   turn_limit=cfg.turn_limit, settle_terminal_rewards=cfg.settle_terminal_rewards,
                                   record=cfg.record_games)

    # ---------------------------------------------------------------- collection

    def _autocast(self):
        return torch.autocast("cuda", dtype=torch.bfloat16, enabled=self.amp)

    def _absorb(self, envs: np.ndarray) -> None:
        """Credit rewards reported by these games to their factions' latest transitions."""
        ro, sh = self.rollout, self.env.shared
        if self.env.restarted:
            # A crashed worker's game ended without a final reward
            lost = np.asarray(self.env.restarted)
            self.env.restarted.clear()
            closing = ro.last[lost]
            ro.done[closing[closing >= 0]] = True
            ro.last[lost] = -1
            self.ret[lost] = 0.0
        if len(envs) == 0:
            return
        raw = sh.reward[envs].astype(np.float64)
        self.ret[envs] += raw
        scale = 1.0 / np.sqrt(self.ret_rms.var + 1e-8) if self.cfg.normalize_rewards else np.ones(NUM_FACTIONS)
        rewards = np.clip(raw * scale, -10.0, 10.0)
        last = ro.last[envs]
        valid = last >= 0
        np.add.at(ro.reward, last[valid], rewards[valid])

        done = sh.done[envs]
        if done.any():
            finished = envs[done]
            closing = ro.last[finished]
            ro.done[closing[closing >= 0]] = True
            ro.last[finished] = -1
            self.ret[finished] = 0.0
            for w in finished.tolist():
                self.ep_stats.append({
                    "return": sh.ep_return[w].copy(), "vp": sh.ep_vp[w].copy(), "win": sh.ep_win[w].copy(),
                    "decisions": int(sh.ep_decisions[w]), "turns": int(sh.ep_turns[w]), "error": bool(sh.ep_error[w]),
                })
            self.games += len(finished)
        self.pending.update(envs.tolist())

    def _act(self, envs: np.ndarray) -> None:
        ro, sh = self.rollout, self.env.shared
        k = len(envs)
        t0, t1 = ro.ptr, ro.ptr + k
        idx = np.arange(t0, t1)
        ro.obs_np[t0:t1] = sh.obs[envs]
        ro.mask_np[t0:t1] = sh.mask[envs]
        agent = sh.agent[envs]
        ro.agent[t0:t1] = agent

        prev = ro.last[envs, agent]
        linked = prev >= 0
        ro.next_idx[prev[linked]] = idx[linked]
        ro.last[envs, agent] = idx

        if self.cfg.normalize_rewards:
            self.ret_rms.update_faction(agent, self.ret[envs, agent])
            self.ret[envs, agent] *= self.cfg.gamma

        obs = ro.obs[t0:t1].to(self.device, non_blocking=True)
        mask = ro.mask[t0:t1].to(self.device, non_blocking=True)
        agent_t = torch.from_numpy(agent).to(self.device, non_blocking=True)
        with self._autocast():
            action, logp, value = self.model.act(obs, agent_t, mask)
        out = torch.stack([action.float(), logp, value]).cpu().numpy()
        actions = out[0].astype(np.int64)
        ro.action[t0:t1] = actions
        ro.logp[t0:t1] = out[1]
        ro.value[t0:t1] = out[2]
        ro.ptr = t1
        self.env.send(envs, actions)

    def collect(self) -> None:
        ro = self.rollout
        ro.reset()
        while ro.ptr < ro.capacity:
            if self.pending:
                todo = np.asarray(sorted(self.pending)[:ro.capacity - ro.ptr], dtype=np.int64)
                self.pending.difference_update(todo.tolist())
                self._act(todo)
            if ro.ptr < ro.capacity:
                self._absorb(self.env.poll())
        # Let in-flight games report so their rewards land in this rollout
        self._absorb(self.env.drain())

        # Bootstrap unfinished chains with each faction's value of the current state
        open_w, open_f = np.nonzero(ro.last >= 0)
        if len(open_w):
            obs = torch.from_numpy(self.env.shared.obs.copy()).to(self.device)
            with torch.no_grad(), self._autocast():
                values = self.model.values_all(obs).float().cpu().numpy()
            ro.boot_value[ro.last[open_w, open_f]] = values[open_w, open_f]

    # ---------------------------------------------------------------- learning

    def learn(self) -> dict:
        cfg, ro = self.cfg, self.rollout
        n = ro.ptr
        adv, ret = ro.advantages(cfg.gamma, cfg.gae_lambda)
        agent_np = ro.agent[:n]
        for f in range(NUM_FACTIONS):
            sel = agent_np == f
            if sel.sum() > 1:
                adv[sel] = (adv[sel] - adv[sel].mean()) / (adv[sel].std() + 1e-8)

        dev = self.device
        obs = ro.obs[:n].to(dev, non_blocking=True)
        mask = ro.mask[:n].to(dev, non_blocking=True)
        agent = torch.from_numpy(agent_np).to(dev)
        actions = torch.from_numpy(ro.action[:n]).to(dev)
        old_logp = torch.from_numpy(ro.logp[:n]).to(dev)
        adv_t = torch.from_numpy(adv.astype(np.float32)).to(dev)
        ret_t = torch.from_numpy(ret.astype(np.float32)).to(dev)

        if cfg.anneal_lr:
            frac = max(0.0, 1.0 - self.decisions / cfg.total_decisions)
            for g in self.optim.param_groups:
                g["lr"] = cfg.lr * frac

        sums = torch.zeros((5, NUM_FACTIONS), device=dev)  # pg, vf, entropy, kl, clipfrac
        counts = torch.zeros(NUM_FACTIONS, device=dev)
        stopped_early = False
        for epoch in range(cfg.epochs):
            perm = torch.randperm(n, device=dev)
            epoch_kl = []
            for start in range(0, n, cfg.minibatch):
                mb = perm[start:start + cfg.minibatch]
                with self._autocast():
                    logits, value = self.model(obs[mb], agent[mb], mask[mb])
                logp, entropy = masked_logp_entropy(logits, mask[mb], actions[mb])
                value = value.float()
                log_ratio = logp - old_logp[mb]
                ratio = log_ratio.exp()
                a = adv_t[mb]
                pg = -torch.min(ratio * a, ratio.clamp(1 - cfg.clip, 1 + cfg.clip) * a)
                vf = 0.5 * (value - ret_t[mb]) ** 2
                loss = pg.mean() + cfg.vf_coef * vf.mean() - cfg.ent_coef * entropy.mean()

                self.optim.zero_grad(set_to_none=True)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), cfg.max_grad_norm)
                self.optim.step()

                with torch.no_grad():
                    kl = (ratio - 1) - log_ratio
                    clipped = ((ratio - 1).abs() > cfg.clip).float()
                    stats = torch.stack([pg, vf, entropy, kl, clipped])
                    sums.index_add_(1, agent[mb], stats)
                    counts.index_add_(0, agent[mb], torch.ones_like(pg))
                    epoch_kl.append(kl.mean())
            if cfg.target_kl and torch.stack(epoch_kl).mean().item() > cfg.target_kl:
                stopped_early = True
                break

        means = (sums / counts.clamp(min=1)).cpu().numpy()
        metrics = {"lr": self.optim.param_groups[0]["lr"], "epochs_run": epoch + 1, "kl_stop": float(stopped_early)}
        for f, name in enumerate(FACTION_NAMES):
            sel = agent_np == f
            y, yhat = ret[sel], ro.value[:n][sel]
            ev = 1 - np.var(y - yhat) / (np.var(y) + 1e-8) if sel.any() else 0.0
            metrics.update({
                f"{name}/policy_loss": means[0, f], f"{name}/value_loss": means[1, f],
                f"{name}/entropy": means[2, f], f"{name}/approx_kl": means[3, f],
                f"{name}/clip_frac": means[4, f], f"{name}/explained_variance": ev,
                f"{name}/decision_share": sel.mean(), f"{name}/reward_scale": 1 / np.sqrt(self.ret_rms.var[f] + 1e-8),
            })
        return metrics

    # ---------------------------------------------------------------- bookkeeping

    def _episode_metrics(self) -> dict:
        stats, self.ep_stats = self.ep_stats, []
        if not stats:
            return {}
        ok = [s for s in stats if not s["error"]]
        metrics = {"games/finished": len(stats), "games/errors": len(stats) - len(ok)}
        if ok:
            metrics["games/decisions"] = np.mean([s["decisions"] for s in ok])
            metrics["games/turns"] = np.mean([s["turns"] for s in ok])
            metrics["games/no_winner"] = np.mean([not s["win"].any() for s in ok])
            for f, name in enumerate(FACTION_NAMES):
                metrics[f"{name}/win_rate"] = np.mean([s["win"][f] for s in ok])
                metrics[f"{name}/vp"] = np.mean([s["vp"][f] for s in ok])
                metrics[f"{name}/game_return"] = np.mean([s["return"][f] for s in ok])
        return metrics

    def _log(self, metrics: dict) -> None:
        for k, v in metrics.items():
            self.tb.add_scalar(k, float(v), self.decisions)
        new = not os.path.exists(self.csv_path)
        row = {"update": self.update, "decisions": self.decisions, "games": self.games, **metrics}
        if not new:
            with open(self.csv_path, newline="") as f:
                header = next(csv.reader(f), None)
            if header != list(row):
                # Columns changed (e.g. first update with game stats): start a new file version
                self.csv_path = self.csv_path.replace(".csv", f"_{self.update}.csv")
                new = True
        with open(self.csv_path, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(row))
            if new:
                w.writeheader()
            w.writerow({k: float(v) if isinstance(v, (np.floating, np.integer)) else v for k, v in row.items()})

    def save(self, tag: str) -> str:
        path = os.path.join(self.ckpt_dir, f"{tag}.pt")
        torch.save({"model": self.model.state_dict(), "optim": self.optim.state_dict(),
                    "ret_rms": self.ret_rms.state_dict(), "update": self.update, "decisions": self.decisions,
                    "games": self.games, "config": dataclasses.asdict(self.cfg)}, path)
        return path

    def _load(self, path: str) -> None:
        ckpt = torch.load(path, map_location=self.device)
        self.model.load_state_dict(ckpt["model"])
        self.optim.load_state_dict(ckpt["optim"])
        self.ret_rms.load_state_dict(ckpt["ret_rms"])
        self.update, self.decisions, self.games = ckpt["update"], ckpt["decisions"], ckpt["games"]
        print(f"resumed from {path} at update {self.update}, {self.decisions} decisions")

    def train(self) -> None:
        cfg = self.cfg
        print(f"run dir {self.run_dir}; {cfg.num_envs} game workers; device {self.device}"
              + (f" ({torch.cuda.get_device_name(0)})" if self.device.type == "cuda" else ""))
        try:
            while self.decisions < cfg.total_decisions:
                self.env.set_update(self.update)
                t0 = time.perf_counter()
                self.collect()
                t1 = time.perf_counter()
                metrics = self.learn()
                t2 = time.perf_counter()
                self.update += 1
                self.decisions += self.rollout.ptr
                metrics.update(self._episode_metrics())
                metrics["perf/collect_decisions_per_s"] = self.rollout.ptr / (t1 - t0)
                metrics["perf/decisions_per_s"] = self.rollout.ptr / (t2 - t0)
                metrics["perf/collect_s"] = t1 - t0
                metrics["perf/learn_s"] = t2 - t1
                self._log(metrics)
                wins = " ".join(f"{n[:4]}={metrics.get(f'{n}/win_rate', float('nan')):.2f}" for n in FACTION_NAMES)
                print(f"update {self.update:5d} | {self.decisions:>11,d} decisions | {self.games:>8,d} games | "
                      f"{metrics['perf/decisions_per_s']:7.0f} dec/s (collect {metrics['perf/collect_decisions_per_s']:.0f}) | "
                      f"learn {t2 - t1:4.1f}s | win {wins}", flush=True)
                if self.update % cfg.save_every == 0:
                    self.save(f"update_{self.update:05d}")
                self.save("latest")
        except KeyboardInterrupt:
            print("interrupted; saving")
            self.save("latest")
        finally:
            self.env.close()
            self.tb.close()


def parse_args(argv=None) -> Config:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    defaults = Config()
    for f in dataclasses.fields(Config):
        name = "--" + f.name.replace("_", "-")
        default = getattr(defaults, f.name)
        if isinstance(default, bool):
            ap.add_argument(name, action=argparse.BooleanOptionalAction, default=default)
        elif isinstance(default, list):
            ap.add_argument(name, type=int, nargs="+", default=default)
        else:
            ap.add_argument(name, type=type(default), default=default)
    args = ap.parse_args(argv)
    cfg = Config(**vars(args))
    if cfg.resume:
        # Keep the original run's directory and settings unless overridden on the command line
        saved = torch.load(cfg.resume, map_location="cpu")["config"]
        given = {k for k, v in vars(args).items() if v != getattr(defaults, k)}
        cfg = Config(**{**saved, **{k: getattr(cfg, k) for k in given}})
    return cfg

