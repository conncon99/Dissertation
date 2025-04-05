
from utils.game_settings import GameSettings
from utils.game_manager import GameManager
from factions.marquise_de_cat import Marquise
from factions.eyrie_dynasties import EyrieDynasties
from factions.woodland_alliance import WoodlandAlliance
from factions.vagabond.vagabond import Vagabond
from controllers.random_controllers import *
import builtins
from utils.colour_utils import colored_print, original_print, set_log

builtins.print = colored_print


marquise = Marquise(MarquiseRandomController())
eyrie_dynasties = EyrieDynasties(EyrieRandomController())
woodland_alliance = WoodlandAlliance(AllianceRandomController())
vagabond = Vagabond(VagabondRandomController())

settings = GameSettings(
    [marquise, eyrie_dynasties, woodland_alliance, vagabond])
gm = GameManager(settings, 5)

while not gm.done:
    if gm.current_message:
        action = gm.current_faction.controller.send_game_message(
            gm.current_message)
        gm.step(action)
    else:
        gm.step()


print("Game Over!")
if isinstance(gm.winner, list):
    print("Winners:", ", ".join([f.name for f in gm.winner]))
elif gm.winner:
    print("Winner:", gm.winner.name)
else:
    print("No winner declared.")
