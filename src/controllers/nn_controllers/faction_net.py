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


class DQN(nn.Module):
    def __init__(self, state_size=663, action_size=54):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(state_size, 1024)
        self.fc2 = nn.Linear(1024, 1024)
        self.fc3 = nn.Linear(1024, 2048)
        self.fc4 = nn.Linear(2048, 1024)
        self.fc5 = nn.Linear(1024, action_size)

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
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95  # Discount factor
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.95
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")

        self.model = DQN(state_size, action_size).to(self.device)
        self.criterion = nn.MSELoss()
        self.optimizer = optim.Adam(self.model.parameters())

    def remember(self, state, action, reward, next_state, mask, done):
        self.memory.append((state, action, reward, next_state, mask, done))

    def act(self, state, mask=None):
        if np.random.rand() <= self.epsilon:
            return np.random.randint(mask if mask is not None else self.action_size)

        state = torch.FloatTensor(state).to(self.device)
        with torch.no_grad():
            q_values = self.model(state)

        q_values = q_values.cpu().numpy().flatten()

        if mask is not None:
            q_values = q_values[:mask]  # Apply integer-based masking

        return np.argmax(q_values)  # Return the best valid action

    def replay(self, batch_size):
        if len(self.memory) < batch_size:
            return
        minibatch = random.sample(self.memory, batch_size)

        for state, action, reward, next_state, mask, done in minibatch:
            state = torch.FloatTensor(state).to(self.device)
            next_state = torch.FloatTensor(next_state).to(self.device)
            reward = torch.FloatTensor([reward]).to(self.device)

            target = reward.clone()
            if not done:
                with torch.no_grad():
                    target += self.gamma * \
                        torch.max(self.model(next_state)[:mask]).detach()

            q_values = self.model(state)
            target_f = q_values.clone()
            target_f[action] = target

            self.optimizer.zero_grad()
            loss = self.criterion(q_values, target_f)
            loss.backward()
            self.optimizer.step()

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
