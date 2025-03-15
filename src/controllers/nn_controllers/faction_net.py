import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from deap import base, creator, tools, algorithms

# Define Neural Network


class FactionNet(nn.Module):
    def __init__(self, input_size=663, output_size=54):
        super(FactionNet, self).__init__()
        self.fc1 = nn.Linear(input_size, 512)
        self.fc2 = nn.Linear(512, 1024)
        self.fc3 = nn.Linear(1024, 1024)
        self.fc4 = nn.Linear(1024, 512)
        self.fc5 = nn.Linear(512, output_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        x = torch.relu(self.fc4(x))
        x = torch.sigmoid(self.fc5(x))  # Ensure output is between 0 and 1
        return x
