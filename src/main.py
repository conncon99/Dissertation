from utils.game_settings import GameSettings
from utils.game_manager import GameManager
from factions import *
from controllers.random_controllers import *
from controllers.nn_controllers.marquise_nn_controller import MarquiseNNController
import gc
import builtins
from utils.colour_utils import colored_print, original_print
from actions.action_group_registry import ActionGroupRegistry
from stable_baselines3 import PPO

builtins.print = colored_print


def clean_up(marquise, eyrie, woodland_alliance, vagabond, settings, game_manager):
    del marquise
    del eyrie
    del woodland_alliance
    del vagabond
    del settings
    del game_manager
    ActionGroupRegistry.reset()
    gc.collect()


RUN_COUNT = 10
TURN_LIMIT = 100


for i in range(RUN_COUNT):
    original_print(f"RUN {i}")
    marquise = Marquise(MarquiseRandomController())
    eyrie = EyrieDynasties(EyrieRandomController())
    woodland_alliance = WoodlandAlliance(AllianceRandomController())
    vagabond = Vagabond(VagabondRandomController())
    settings = GameSettings([vagabond, marquise, eyrie, woodland_alliance])
    game_manager = GameManager(settings, turn_limit=TURN_LIMIT)
    clean_up(marquise, eyrie, woodland_alliance,
             vagabond, settings, game_manager)
