import torch
import torch.nn as nn
import torch.optim as optim
import random
import numpy as np
from collections import deque
import torch
import torch.nn as nn
import torch.optim as optim
import random
import numpy as np
from collections import deque
from utils.colour_utils import original_print


class DQN(nn.Module):
    def __init__(self, state_size=747, action_size=56):  # 56 pawns
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(state_size, 2048)
        self.fc2 = nn.Linear(2048, 2048)
        self.fc3 = nn.Linear(2048, 2048)
        self.fc4 = nn.Linear(2048, 2048)
        self.fc5 = nn.Linear(2048, action_size)

        self.criterion = nn.MSELoss()
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
        self.memory = deque(maxlen=100_000)
        self.gamma = 0.95  # Discount factor
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.95
        self.batch_size = 256
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")

        self.model = DQN(state_size, action_size).to(self.device)

    def remember(self, state, action, reward, next_state, mask, done):
        self.memory.append((state, action, reward, next_state, mask, done))

    def act(self, state, mask=None):
        mask = np.array(mask, dtype=bool)
        if np.random.rand() <= self.epsilon:
            random_arr = np.random.rand(self.action_size)
            random_arr[~mask] = -np.inf
            return np.argmax(random_arr)

        state = torch.FloatTensor(state).to(self.device)
        with torch.no_grad():
            q_values = self.model(state)

        q_values = q_values.cpu().numpy().flatten()

        if mask is not None:
            # Mask out bad actions by setting them to -inf
            q_values[~mask] = -np.inf

        return np.argmax(q_values)  # Return the best valid action

    def learn(self):
        if len(self.memory) < self.batch_size:
            return
        self.model.optimizer.zero_grad()
        batch = random.sample(self.memory, self.batch_size)

        for state, action, reward, next_state, mask, done in batch:
            state = torch.FloatTensor(state).to(self.device)
            next_state = torch.FloatTensor(next_state).to(self.device)
            reward = torch.FloatTensor([reward]).to(self.device)

            q_eval = self.model.forward(state)[action].unsqueeze(0)
            if not done:
                q_next = self.model.forward(next_state)
            else:
                q_next = torch.FloatTensor([0.0])

            q_target = reward + self.gamma * torch.max(q_next).unsqueeze(0)

            loss = self.model.criterion(q_target, q_eval).to(self.device)
            loss.backward()
            self.model.optimizer.step()

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    # def replay(self, batch_size):
    #     if len(self.memory) < batch_size:
    #         return
    #     minibatch = random.sample(self.memory, batch_size)

    #     for state, action, reward, next_state, mask, done in minibatch:
    #         mask = np.array(mask, dtype=bool)
    #         state = torch.FloatTensor(state).to(self.device)
    #         next_state = torch.FloatTensor(next_state).to(self.device)
    #         reward = torch.FloatTensor([reward]).to(self.device)

    #         target = reward.clone()
    #         if not done:
    #             with torch.no_grad():
    #                 next_q_values = self.model(next_state)
    #                 # TODO: Check if this is right
    #                 next_q_values[~mask] = -np.inf
    #                 target += self.gamma * \
    #                     torch.max(next_q_values).detach()

    #         q_values = self.model(state)
    #         target_f = q_values.clone()
    #         target_f[action] = target

    #         self.optimizer.zero_grad()
    #         loss = self.criterion(q_values, target_f)
    #         loss.backward()
    #         self.optimizer.step()

    #     if self.epsilon > self.epsilon_min:
    #         self.epsilon *= self.epsilon_decay
