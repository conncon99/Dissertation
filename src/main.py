import math
import os
import numpy as np
import torch
from utils.game_settings import GameSettings
from utils.game_manager import GameManager
from factions.marquise_de_cat import Marquise
from factions.eyrie_dynasties import EyrieDynasties
from factions.woodland_alliance import WoodlandAlliance
from factions.vagabond.vagabond import Vagabond
from controllers.random_controllers import *
from controllers.nn_controllers.marquise_nn_controller import MarquiseNNController
from controllers.nn_controllers.faction_net import DQNAgent
import gc
import builtins
from utils.colour_utils import colored_print, original_print, set_log

builtins.print = colored_print

### **TRAINING SETTINGS** ###
TURN_LIMIT = 100
RUN_COUNT = 500_000
SAVE_EVERY = 250  # Save every 500 runs
UPDATE_TARGET_EVERY = 1000

CHECKPOINT_FILE = "saved_models/marquise_nn.pth"

# Create directory for saved models if it doesn't exist
os.makedirs("saved_models", exist_ok=True)

### **Initialize Marquise NN (DQNAgent)** ###
marquise_net = DQNAgent(773, 56)

# ### **Load Checkpoint if Exists** ###
if os.path.exists(CHECKPOINT_FILE):
    marquise_net.policy_net.load_state_dict(torch.load(CHECKPOINT_FILE))
    marquise_net.policy_net.train()
    original_print(f"✅ Loaded model from {CHECKPOINT_FILE}")
else:
    original_print("⚠ No saved model found, starting fresh.")

### **Track Wins** ###
winners = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}


def finish():
    ### **Final Stats** ###
    original_print(f"🏆 Marquise Wins: {winners[1]}")
    original_print(f"🦅 Eyrie Dynasties Wins: {winners[2]}")
    original_print(f"🌲 Woodland Alliance Wins: {winners[3]}")
    original_print(f"🎒 Vagabond Wins: {winners[4]}")
    original_print(f"⏳ Timeouts: {winners[5]}")

    ### **Final Test Run With Logging Enabled** ###
    set_log(True)
    marquise = Marquise(MarquiseNNController(marquise_net))
    # marquise = Marquise(MarquiseRandomController())
    eyrie = EyrieDynasties(EyrieRandomController())
    woodland_alliance = WoodlandAlliance(AllianceRandomController())
    vagabond = Vagabond(VagabondRandomController())
    settings = GameSettings([marquise, eyrie, woodland_alliance, vagabond])
    manager = GameManager(settings, TURN_LIMIT)
    manager.run_game()


if __name__ == "__main__":
    try:
        for i in range(RUN_COUNT):
            original_print(f"RUN: {i+1}")

            # Initialize factions
            marquise = Marquise(MarquiseNNController(marquise_net))
            # marquise = Marquise(MarquiseRandomController())
            eyrie = EyrieDynasties(EyrieRandomController())
            woodland_alliance = WoodlandAlliance(AllianceRandomController())
            vagabond = Vagabond(VagabondRandomController())

            # Set up game
            settings = GameSettings(
                [marquise, eyrie, woodland_alliance, vagabond])
            manager = GameManager(settings, TURN_LIMIT)

            # Run game and track winner
            winner = manager.run_game()
            winners[winner] += 1

            # Train Marquise NN
            marquise_net.learn()
            # marquise_net.memory.clear()

            # Update the target net every 1000 runs
            if (i + 1) % UPDATE_TARGET_EVERY == 0:
                marquise_net.target_net.load_state_dict(
                    marquise_net.policy_net.state_dict())

            # Save Model Every 500 Runs
            if (i + 1) % SAVE_EVERY == 0:
                torch.save(marquise_net.policy_net.state_dict(),
                           CHECKPOINT_FILE)
                original_print(f"💾 Model checkpoint saved at {i+1} runs.")
    except KeyboardInterrupt:
        pass
    finally:
        finish()
