import torch
import torch.nn as nn
import numpy as np


class ICM(nn.Module):
    def __init__(self, state_size, action_size, hidden_size=256):
        super(ICM, self).__init__()
        # Inverse model: Predicts the action from current and next state
        self.inverse_net = nn.Sequential(
            nn.Linear(state_size * 2, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, action_size)
        )
        # Forward model: Predicts the next state from current state and action
        self.forward_net = nn.Sequential(
            nn.Linear(state_size + action_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, state_size)
        )
        self.mse_loss = nn.MSELoss()
        self.ce_loss = nn.CrossEntropyLoss()

    def forward(self, state, next_state, action):
        # Predict action from states
        inverse_input = torch.cat([state, next_state], dim=1)
        predicted_action = self.inverse_net(inverse_input)

        # Predict next state from state and action
        if isinstance(action, np.ndarray):
            action = torch.tensor(action, dtype=torch.long).to(state.device)
        if len(action.shape) == 1:
            action = action.unsqueeze(1)
        action_onehot = torch.zeros((action.size(0), 56)).to(action.device)
        action_onehot.scatter_(1, action, 1.0)
        forward_input = torch.cat([state, action_onehot], dim=1)
        predicted_next_state = self.forward_net(forward_input)

        return predicted_action, predicted_next_state

    def compute_loss(self, state, next_state, action):
        if isinstance(action, np.ndarray):
            action = torch.tensor(action, dtype=torch.long).to(state.device)
        if len(action.shape) == 1:
            action = action.unsqueeze(1)
        predicted_action, predicted_next_state = self.forward(
            state, next_state, action)
        inverse_loss = self.ce_loss(predicted_action, action.squeeze())
        forward_loss = self.mse_loss(predicted_next_state, next_state)
        return inverse_loss, forward_loss
