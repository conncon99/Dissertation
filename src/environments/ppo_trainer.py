import torch
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.utils import explained_variance
from stable_baselines3.common.policies import ActorCriticPolicy
import gym
from gym import spaces


class DummyGym(gym.Env):
    def __init__(self, obs_dim, action_dim):
        super().__init__()
        self.observation_space = spaces.Box(
            low=0, high=1, shape=(obs_dim,), dtype=np.float32)
        self.action_space = spaces.Box(
            low=0, high=1, shape=(action_dim,), dtype=np.float32)


class PPOTrainer:
    def __init__(self, obs_dim=663, action_dim=54, learning_rate=3e-4, gamma=0.99, gae_lambda=0.95):
        """
        Custom PPO training pipeline without OpenAI Gym.
        """
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")

        # Initialize PPO Model
        self.model = PPO(
            ActorCriticPolicy,
            DummyGym(obs_dim, action_dim),  # No environment
            policy_kwargs=dict(net_arch=[64, 64]),  # Two-layer MLP
            learning_rate=learning_rate,
            gamma=gamma,
            gae_lambda=gae_lambda,
            verbose=1,
            device=self.device
        )

        # Store episode data
        self.obs_buffer = []
        self.action_buffer = []
        self.log_prob_buffer = []
        self.reward_buffer = []

    def store_step(self, obs, action, log_prob=None):
        """
        Store a step's observation, action, and log probability.
        """
        self.obs_buffer.append(obs)
        self.action_buffer.append(action)
        self.log_prob_buffer.append(log_prob)

    def store_final_reward(self, final_reward):
        """
        Assign the final reward to all collected steps.
        """
        self.reward_buffer = [final_reward] * len(self.obs_buffer)

    def train_ppo(self):
        """
        Train PPO on the collected episode data.
        """
        if not self.obs_buffer:
            return

        # Convert lists to tensors
        obs_tensor = torch.tensor(
            self.obs_buffer, dtype=torch.float32, device=self.device)
        action_tensor = torch.tensor(
            self.action_buffer, dtype=torch.float32, device=self.device)
        log_prob_tensor = torch.tensor(
            self.log_prob_buffer, dtype=torch.float32, device=self.device)
        reward_tensor = torch.tensor(
            self.reward_buffer, dtype=torch.float32, device=self.device)

        # Compute advantages using GAE (Generalized Advantage Estimation)
        advantages, returns = self.compute_advantages(reward_tensor)

        # Train PPO model
        self.model.train()
        optimizer = self.model.policy.optimizer

        for _ in range(10):
            optimizer.zero_grad()
            distribution = self.model.policy.get_distribution(obs_tensor)
            new_log_prob = distribution.log_prob(action_tensor)

            # Compute loss (PPO Clipped Loss)
            ratio = torch.exp(new_log_prob - log_prob_tensor)
            clipped_ratio = torch.clamp(ratio, 1 - 0.2, 1 + 0.2)
            loss = -torch.min(ratio * advantages,
                              clipped_ratio * advantages).mean()

            loss.backward()
            optimizer.step()

        # Debugging info
        explained_var = explained_variance(
            reward_tensor.cpu().numpy(), returns.cpu().numpy())
        print(f"Training Loss: {loss}, Explained Variance: {explained_var}")

        # Clear buffers after training
        self.obs_buffer.clear()
        self.action_buffer.clear()
        self.log_prob_buffer.clear()
        self.reward_buffer.clear()

    def compute_advantages(self, rewards):
        """
        Compute advantages and returns for PPO.
        """
        advantages = torch.zeros_like(rewards)
        returns = torch.zeros_like(rewards)
        next_value = 0

        for t in reversed(range(len(rewards))):
            delta = rewards[t] + self.gamma * next_value - rewards[t]
            advantages[t] = delta + self.gamma * self.gae_lambda * next_value
            next_value = rewards[t]

        returns = advantages + rewards
        return advantages, returns
