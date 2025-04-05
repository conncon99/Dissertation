import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from collections import deque
from utils.colour_utils import original_print
import matplotlib.pyplot as plt
from controllers.nn_controllers.icm import ICM

loss_history = []
icm_loss_history = []
total_reward_history = []
intrinsic_reward_history = []
extrinsic_reward_history = []


class DQN(nn.Module):
    def __init__(self, state_size=773, action_size=56):  # 56 pawns
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(state_size, 2048)
        self.fc2 = nn.Linear(2048, 2048)
        self.fc3 = nn.Linear(2048, 2048)
        self.fc4 = nn.Linear(2048, 2048)
        self.fc5 = nn.Linear(2048, action_size)

        self.loss = nn.MSELoss()
        self.optimizer = optim.Adam(self.parameters())

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        x = torch.relu(self.fc4(x))
        return self.fc5(x)


class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        # self.icm = ICM(self.state_size, self.action_size).cuda()
        # self.icm_optimizer = optim.Adam(self.icm.parameters())
        # self.intrinsic_scale = 0.01
        self.mem_size = 100_000
        self.mem_cntr = 0
        self.gamma = 0.95  # Discount factor
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.batch_size = 64
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")

        self.policy_net = DQN(state_size, action_size).to(self.device)
        self.target_net = DQN(state_size, action_size).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        self.state_memory = np.zeros(
            (self.mem_size, *(state_size,)), dtype=np.float32)
        self.new_state_memory = np.zeros(
            (self.mem_size, *(state_size,)), dtype=np.float32)
        self.action_memory = np.zeros(self.mem_size, dtype=np.int32)
        self.reward_memory = np.zeros(self.mem_size, dtype=np.float32)
        self.terminal_memory = np.zeros(self.mem_size, dtype=np.bool)

    def plot_dqn_loss(self):
        plt.figure(figsize=(10, 5))
        plt.plot(loss_history)
        plt.xlabel("Episode")
        plt.ylabel("DQN Loss")
        plt.title("DQN Loss Over Time")
        plt.yscale('log')
        plt.savefig("dqn_loss.png")
        plt.close()

    # def plot_icm_loss(self):
    #     plt.figure(figsize=(10, 5))
    #     plt.plot(icm_loss_history)
    #     plt.xlabel("Episode")
    #     plt.ylabel("ICM Loss")
    #     plt.title("Intrinsic Curiosity Module Loss Over Time")
    #     plt.savefig("icm_loss.png")
    #     plt.close()

    def plot_total_reward(self):
        # plt.figure(figsize=(10, 5))
        # plt.plot(total_reward_history, label='Total Reward', color='blue')
        # plt.plot(extrinsic_reward_history,
        #          label='Extrinsic Reward', color='green')
        # plt.plot(intrinsic_reward_history,
        #          label='Intrinsic Reward', color='red')
        # plt.xlabel("Episode")
        # plt.ylabel("Reward")
        # plt.title("Total, Extrinsic, and Intrinsic Rewards Over Time")
        # plt.legend()
        # plt.savefig("total_reward_combined.png")
        # plt.close()
        plt.figure(figsize=(10, 5))
        plt.xlabel("Episode")
        plt.ylabel("Reward")
        plt.plot(extrinsic_reward_history)
        plt.savefig("total_reward_combined.png")
        plt.close()

    def save_graphs(self):
        self.plot_dqn_loss()
        # self.plot_icm_loss()
        self.plot_total_reward()
        # self.plot_icm_loss()
        # self.plot_total_reward()

    def remember(self, state, action, reward, state_, done):
        index = self.mem_cntr % self.mem_size
        self.state_memory[index] = state
        self.new_state_memory[index] = state_
        self.reward_memory[index] = reward
        self.action_memory[index] = action
        self.terminal_memory[index] = done

        self.mem_cntr += 1

    def intrinsic_reward(self, state, next_state, action):
        action = torch.tensor(action, dtype=torch.long).to(state.device)
        if len(action.shape) == 1:
            action = action.unsqueeze(1)
        _, predicted_next_state = self.icm(state, next_state, action)
        intrinsic_reward = torch.mean(
            (predicted_next_state - next_state) ** 2, dim=1)
        return intrinsic_reward

    def act(self, state, mask=None):
        if np.random.random() > self.epsilon:
            state = torch.FloatTensor(state).to(self.device)
            actions = self.policy_net.forward(
                state).cpu().detach().numpy().squeeze()
        else:
            actions = np.array([np.random.random()
                                for _ in range(self.action_size)])
        if mask is not None:
            mask = np.array(mask)
            actions[~mask] = -np.inf
        action = np.argmax(actions).item()
        return action

    def learn(self):
        if self.mem_cntr < self.batch_size:
            return

        self.policy_net.optimizer.zero_grad()
        max_mem = min(self.mem_cntr, self.mem_size)
        batch = np.random.choice(max_mem, self.batch_size, replace=False)
        batch_index = np.arange(self.batch_size, dtype=np.int32)

        state_batch = torch.tensor(self.state_memory[batch]).to(self.device)
        new_state_batch = torch.tensor(
            self.new_state_memory[batch]).to(self.device)
        reward_batch = torch.tensor(self.reward_memory[batch]).to(self.device)
        terminal_batch = torch.tensor(
            self.terminal_memory[batch]).to(self.device)

        action_batch = self.action_memory[batch]

        # Compute Intrinsic Reward

        # intrinsic_rewards = self.intrinsic_reward(
        #     state_batch, new_state_batch, action_batch).detach()
        # total_rewards = reward_batch + self.intrinsic_scale * intrinsic_rewards
        # total_rewards = total_rewards.detach()

        # # ICM Loss Calculation
        # inverse_loss, forward_loss = self.icm.compute_loss(
        #     state_batch, new_state_batch, action_batch)
        # icm_loss = inverse_loss + forward_loss

        # # Update ICM Network
        # self.icm_optimizer.zero_grad()
        # icm_loss.backward()
        # self.icm_optimizer.step()

        # Q-Learning Loss Calculation

        q_eval = self.policy_net.forward(
            state_batch)[batch_index, action_batch]
        q_next = self.policy_net.forward(new_state_batch)
        # q_next[terminal_batch] = 0.0

        with torch.no_grad():
            max_next_q_values = self.target_net(new_state_batch).max(1)[0]
            q_target = reward_batch + self.gamma * \
                max_next_q_values * \
                (1 - terminal_batch.float())  # replace with total rewards if using icm

        loss = self.policy_net.loss(q_eval, q_target).to(self.device)
        loss.backward()
        self.policy_net.optimizer.step()

        self.epsilon = self.epsilon - \
            self.epsilon_decay if self.epsilon > self.epsilon_min else self.epsilon_min

        loss_history.append(loss.item())
        # icm_loss_history.append(icm_loss.item())
        # total_reward_history.append(total_rewards.sum().item())
        extrinsic_reward_history.append(reward_batch.detach().sum().item())
        # intrinsic_reward_history.append(
        #     intrinsic_rewards.sum().item() * self.intrinsic_scale)
        # original_print(
        #     f"DQN Loss: {loss.item()}, ICM Loss: {icm_loss.item()}")
        original_print(f"DQN Loss: {loss.item()}")

        if len(loss_history) % 100 == 0:
            self.save_graphs()
