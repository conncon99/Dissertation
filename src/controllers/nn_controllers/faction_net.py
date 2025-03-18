import torch
import torch.nn as nn
from collections import deque
import random
import numpy as np
from torch import optim

# Define Neural Network


class FactionNet(nn.Module):
    def __init__(self, input_size=663, output_size=54):
        super(FactionNet, self).__init__()
        self.fc1 = nn.Linear(input_size, 1024)
        self.fc2 = nn.Linear(1024, 1024)
        self.fc3 = nn.Linear(1024, 512)
        self.fc4 = nn.Linear(512, output_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        x = torch.sigmoid(self.fc4(x))  # Ensure output is between 0 and 1
        return x


class DQNAgent:
    def __init__(self, input_size=663, output_size=54):
        self.input_size = input_size
        self.output_size = output_size
        self.model = FactionNet(input_size, output_size)
        self.memory = deque(maxlen=500)
        self.gamma = 0.95  # Discount factor
        self.epsilon = 1.0  # Explore-exploit factor
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")
        self.criterion = nn.MSELoss()
        self.optimizer = optim.Adam(self.model.parameters())

    def remember(self, state, action, reward, next_state, done):
        # This will need work to be able to handle next states
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if random.random() <= self.epsilon:
            return np.array([random.random() for _ in range(self.output_size)])
        with torch.no_grad():
            q_values = self.model(state)
        return q_values.numpy().flatten()

    def replay(self, batch_size):
        minibatch = np.array(random.sample(self.memory, batch_size))
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * \
                    np.amax(self.model(next_state)[0])
            target_f = self.model(state)
            target_f[0][action] = target
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
