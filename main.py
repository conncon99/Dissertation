import os
import matplotlib
from src.pettingzoo_env import RootEnv
import matplotlib.pyplot as plt
from tqdm import tqdm
from typing import Optional, Tuple
import logging
import torch
from pathlib import Path
import numpy as np
import gymnasium as gym
from tianshou.env import PettingZooEnv, DummyVectorEnv, SubprocVectorEnv
from tianshou.policy import MultiAgentPolicyManager, RainbowPolicy, BasePolicy, DQNPolicy, ICMPolicy
from tianshou.trainer import OffpolicyTrainer
from tianshou.utils.net.common import Net
from tianshou.utils.net.discrete import IntrinsicCuriosityModule
from tianshou.data import Collector, VectorReplayBuffer, PrioritizedVectorReplayBuffer
from torch.utils.tensorboard import SummaryWriter
from tianshou.utils import TensorboardLogger
from tianshou.data import Batch


# make sure we patch only once
if not hasattr(MultiAgentPolicyManager, "_prio_patched"):
    _old_process_fn = MultiAgentPolicyManager.process_fn

    def _patched_process_fn(self, batch, buffer, indices):
        # 1. let the original method do all the real work
        processed = _old_process_fn(self, batch, buffer, indices)

        # 2. wherever the priority fields existed in the original batch,
        #    copy them into every agent sub-batch that lost them
        def _repair(sub):
            for k in ("weight", "index"):
                if k in batch and k not in sub:
                    sub[k] = batch[k]

        if isinstance(processed, dict):          # new-ish Ti­anshou
            for sb in processed.values():
                _repair(sb)
        elif isinstance(processed, (list, tuple)):
            for sb in processed:
                _repair(sb)
        else:                                    # single-agent fallback
            _repair(processed)

        # 3. also keep the keys in the returned (re-stacked) batch
        for k in ("weight", "index"):
            if k in batch and k not in processed:
                processed[k] = batch[k]

        return processed

    MultiAgentPolicyManager.process_fn = _patched_process_fn
    MultiAgentPolicyManager._prio_patched = True

BATCH_SIZE = 64
TRAINING_NUM = 10

faction_color_map = {
    'marquise': 'orange',
    'eyrie': 'blue',
    'woodland_alliance': 'green',
    'vagabond': 'gray'
}

agent_names = ['marquise', 'eyrie', 'woodland_alliance', 'vagabond']
LOG_DIR = Path("logs/root")


def _get_env():
    return PettingZooEnv(RootEnv())


def plot_metric(data_dict, title, ylabel, filename, plot_dir, colors=None, log_scale=False):
    fig, ax = plt.subplots()
    for i, (agent_name, values) in enumerate(data_dict.items()):
        color = colors[i] if colors and i < len(colors) else None
        ax.plot(values, label=agent_name.capitalize(), color=color)
    if log_scale:
        plt.yscale('log')
    ax.set_title(title)
    ax.set_xlabel("Episode")
    ax.set_ylabel(ylabel)
    ax.legend()
    ax.grid(True)
    plt.tight_layout()
    os.makedirs(plot_dir, exist_ok=True)
    plt.savefig(os.path.join(plot_dir, filename))
    plt.close()


def _get_agents():
    env = _get_env()

    obs_shape = env.observation_space["observation"].shape
    act_shape = env.action_space.n
    device = "cuda" if torch.cuda.is_available() else "cpu"

    agents = []

    for i in range(4):

        net = Net(state_shape=obs_shape,
                  action_shape=act_shape,
                  hidden_sizes=[1024, 1024, 512],
                  device=device,
                  softmax=True,
                  num_atoms=340,
                  ).to(device)

        optim = torch.optim.Adam(net.parameters(), lr=1e-4)

        base_policy = RainbowPolicy(model=net, optim=optim,
                                    action_space=env.action_space, estimation_step=3, target_update_freq=320, num_atoms=340, v_max=25, v_min=-10).to(device)
        # Feature extractor for ICM
        feature_net = Net(state_shape=obs_shape,
                          hidden_sizes=[256, 256], device=device)
        feature_dim = feature_net.output_dim

        # icm_module = IntrinsicCuriosityModule(
        #     feature_net=feature_net,
        #     feature_dim=feature_dim,
        #     action_dim=act_shape,
        #     hidden_sizes=[256, 256],
        #     device=device
        # )

        # icm_policy = ICMPolicy(
        #     policy=base_policy,
        #     model=icm_module,
        #     optim=torch.optim.Adam(
        #         list(net.parameters()) + list(icm_module.parameters()), lr=1e-4
        #     ),
        #     lr_scale=1.0,
        #     reward_scale=0.1,
        #     forward_loss_weight=0.2,
        #     action_space=env.action_space,
        # ).to(device)

        agents.append(base_policy)

    return MultiAgentPolicyManager(policies=agents, env=env)


if __name__ == "__main__":

    print("CUDA Available:", torch.cuda.is_available())
    print("GPU Device:", torch.cuda.get_device_name(
        0) if torch.cuda.is_available() else "None")

    # Environment setup

    train_envs = SubprocVectorEnv([_get_env for _ in range(TRAINING_NUM)])
    test_envs = SubprocVectorEnv([_get_env for _ in range(TRAINING_NUM)])
    seed = 1
    np.random.seed(seed)
    torch.manual_seed(seed)
    train_envs.seed(seed)
    test_envs.seed(seed)

    # Agent Setup

    policy = _get_agents()

    # Logging

    # Prepare per-agent TensorBoard loggers

    writer = SummaryWriter(log_dir=LOG_DIR)
    tb_logger = TensorboardLogger(writer)

    # Collector Setup

    train_collector = Collector(policy, train_envs, PrioritizedVectorReplayBuffer(
        total_size=30_000,
        buffer_num=len(train_envs),
        alpha=0.6,
        beta=0.4
    ))
    test_collector = Collector(policy, test_envs, exploration_noise=True)
    # Batch Size *  training num
    # train_collector.collect(
    #     n_step=BATCH_SIZE * TRAINING_NUM, reset_before_collect=True)

    # Training Callbacks

    agent_rewards = {name: [] for name in agent_names}
    agent_losses = {name: [] for name in agent_names}
    vp_tracking = {name: [] for name in agent_names}

    agent_episodes = []

    def save_best_fn(policy):
        os.makedirs("log/root/rainbow", exist_ok=True)
        # save all agent nets
        for agent, p in zip(agent_names, policy.policies.values()):
            torch.save(p.state_dict(), f"log/root/rainbow/{agent}.pth")

    # stop when average reward across agents >= some threshold
    def stop_fn(mean_rewards):
        return False

    # set exploration schedules
    def train_fn(epoch, env_step):

        for p in policy.policies.values():
            p.set_eps(max(0.05, 1 - epoch / 50))
        beta_start = 0.4
        beta_end = 1.0
        max_epochs = 500
        frac = min(epoch / max_epochs, 1.0)
        beta = beta_start + frac * (beta_end - beta_start)
        train_collector.buffer.set_beta(beta)

    def test_fn(epoch, env_step):
        for p in policy.policies.values():
            p.set_eps(0.05)

    # reward metric: mean over all agents
    def reward_metric(rews):
        return rews.mean(axis=0)

    class CustomLogger(TensorboardLogger):
        def log_update_data(self, data, step):
            # print(data)
            for name, agent in zip(agent_names, policy.policies.values()):
                try:
                    agent_loss = data['smoothed_loss'][f"{name}/loss"]
                except:
                    print("\nError: Used Previous Agent Loss")
                    agent_loss = agent_losses[name][-1]
                # print(agent_loss)
                agent_losses[name].append(agent_loss)

        def log_test_data(self, data, step):
            for idx, name in enumerate(agent_names):
                try:
                    reward = data["returns"][idx]
                except:
                    print("\nERROR: Used Previous Agent Reward")
                    reward = agent_rewards[name][-1]

                agent_rewards[name].append(reward)

            plot_metric(agent_losses, "Agent Loss",
                        "Loss", "agent_loss.png", LOG_DIR, colors=list(faction_color_map.values()), log_scale=True)
            plot_metric(agent_rewards, "Agent Reward",
                        "Reward", "agent_reward.png", LOG_DIR, colors=list(faction_color_map.values()))
            # plot_metric(vp_tracking, "Victory Points",
            #             "Victory Points", "vp_graph.png", LOG_DIR)

    tb_logger = CustomLogger(writer)

    # Run Training
    result = OffpolicyTrainer(
        policy=policy,
        train_collector=train_collector,
        test_collector=test_collector,
        max_epoch=500,
        step_per_epoch=5000,
        step_per_collect=200,
        episode_per_test=10,
        batch_size=BATCH_SIZE,
        train_fn=train_fn,
        test_fn=test_fn,
        stop_fn=stop_fn,
        save_best_fn=save_best_fn,
        update_per_step=0.1,
        test_in_train=False,
        reward_metric=reward_metric,
        logger=tb_logger
    ).run(reset_prior_to_run=True)
    print("finished: ", result)
