from utils.game_settings import GameSettings
from utils.game_manager import GameManager
from factions.marquise_de_cat import Marquise
from factions.eyrie_dynasties import EyrieDynasties
from factions.woodland_alliance import WoodlandAlliance
from factions.vagabond.vagabond import Vagabond
from controllers.random_controllers.marquise_random_controller import MarquiseRandomController
from controllers.random_controllers.eyrie_random_controller import EyrieRandomController
from controllers.random_controllers.alliance_random_controller import AllianceRandomController
from controllers.random_controllers.vagabond_random_controller import VagabondRandomController
from utils.colour_utils import colored_print
import builtins

builtins.print = colored_print
for _ in range(5):
    marquise = Marquise(MarquiseRandomController())
    eyrie = EyrieDynasties(EyrieRandomController())
    woodland_alliance = WoodlandAlliance(AllianceRandomController())
    vagabond = Vagabond(VagabondRandomController())
    settings = GameSettings([vagabond, marquise, eyrie, woodland_alliance])
    game_manager = GameManager(settings)
