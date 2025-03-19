import math
import os
import numpy as np
import torch
from utils.game_settings import GameSettings
from utils.game_manager import GameManager
from factions import *
from controllers.random_controllers import *
from controllers.nn_controllers.marquise_nn_controller import MarquiseNNController
from controllers.nn_controllers.faction_net import DQNAgent
import gc
import builtins
from utils.colour_utils import colored_print, original_print, set_log

builtins.print = colored_print

### **TRAINING SETTINGS** ###
TURN_LIMIT = 100
RUN_COUNT = 10_000
SAVE_EVERY = 500  # Save every 500 runs
BATCH_SIZE = 32
CHECKPOINT_FILE = "saved_models/marquise_nn.pth"

# Create directory for saved models if it doesn't exist
os.makedirs("saved_models", exist_ok=True)

### **Initialize Marquise NN (DQNAgent)** ###
marquise_net = DQNAgent(663, 54)

### **Load Checkpoint if Exists** ###
if os.path.exists(CHECKPOINT_FILE):
    marquise_net.model.load_state_dict(torch.load(CHECKPOINT_FILE))
    marquise_net.model.train()
    original_print(f"✅ Loaded model from {CHECKPOINT_FILE}")
else:
    original_print("⚠ No saved model found, starting fresh.")

### **Track Wins** ###
winners = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

if __name__ == "__main__":
    for i in range(RUN_COUNT):
        original_print(f"RUN: {i+1}")

        # Initialize factions
        marquise = Marquise(MarquiseNNController(marquise_net))
        eyrie = EyrieDynasties(EyrieRandomController())
        woodland_alliance = WoodlandAlliance(AllianceRandomController())
        vagabond = Vagabond(VagabondRandomController())

        # Set up game
        settings = GameSettings([marquise, eyrie, woodland_alliance, vagabond])
        manager = GameManager(settings, TURN_LIMIT)

        # Run game and track winner
        winner = manager.run_game()
        winners[winner] += 1

        # Train Marquise NN
        for _ in range(math.ceil(len(marquise_net.memory) / (BATCH_SIZE * 2))):
            marquise_net.replay(min(BATCH_SIZE, len(marquise_net.memory)))
        marquise_net.memory.clear()

        # Save Model Every 500 Runs
        if (i + 1) % SAVE_EVERY == 0:
            torch.save(marquise_net.model.state_dict(), CHECKPOINT_FILE)
            original_print(f"💾 Model checkpoint saved at {i+1} runs.")

    ### **Final Stats** ###
    original_print(f"🏆 Marquise Wins: {winners[1]}")
    original_print(f"🦅 Eyrie Dynasties Wins: {winners[2]}")
    original_print(f"🌲 Woodland Alliance Wins: {winners[3]}")
    original_print(f"🎒 Vagabond Wins: {winners[4]}")
    original_print(f"⏳ Timeouts: {winners[5]}")

    ### **Final Test Run With Logging Enabled** ###
    set_log(True)
    marquise = Marquise(MarquiseNNController(marquise_net))
    eyrie = EyrieDynasties(EyrieRandomController())
    woodland_alliance = WoodlandAlliance(AllianceRandomController())
    vagabond = Vagabond(VagabondRandomController())
    settings = GameSettings([marquise, eyrie, woodland_alliance, vagabond])
    manager = GameManager(settings, TURN_LIMIT)
    manager.run_game()
