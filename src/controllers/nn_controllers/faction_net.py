import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from deap import base, creator, tools, algorithms

# Define Neural Network


class FactionNet(nn.Module):
    def __init__(self, input_size=663, output_size=54, hidden_size=128):
        super(FactionNet, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.sigmoid(self.fc3(x))  # Ensure output is between 0 and 1
        return x
