import random
import numpy as np
import torch
import matplotlib.pyplot as plt
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
from deap import tools, creator, base
from utils.game_settings import GameSettings
from utils.game_manager import GameManager
from factions import *
from controllers.random_controllers import *
from controllers.nn_controllers.marquise_nn_controller import MarquiseNNController
from controllers.nn_controllers.faction_net import FactionNet, DQNAgent
import gc
import builtins
from utils.colour_utils import colored_print, original_print
from actions.action_group_registry import ActionGroupRegistry

builtins.print = colored_print


TURN_LIMIT = 100
RUN_COUNT = 10

marquise_net = DQNAgent()

if __name__ == "__main__":
    for i in range(RUN_COUNT):
        original_print(f"RUN: {i}")
        marquise = Marquise(MarquiseNNController(marquise_net))
        eyrie = EyrieDynasties(EyrieRandomController())
        woodland_alliance = WoodlandAlliance(AllianceRandomController())
        vagabond = Vagabond(VagabondRandomController())
        settings = GameSettings([marquise, eyrie, woodland_alliance, vagabond])
        manager = GameManager(settings, TURN_LIMIT)
        manager.run_game()
