
from utils.game_settings import GameSettings
from utils.game_manager import GameManager
from factions.marquise_de_cat import Marquise
from factions.eyrie_dynasties import EyrieDynasties
from factions.woodland_alliance import WoodlandAlliance
from factions.vagabond.vagabond import Vagabond
from controllers.random_controllers import *
from controllers.player_controllers.marquise_player_controller import MarquisePlayerController
import builtins
from utils.colour_utils import colored_print, original_print, set_print_colour

builtins.print = colored_print

NUM_RUNS = 1
TURN_LIMIT = 100

for i in range(NUM_RUNS):
    marquise = Marquise(MarquiseRandomController())
    eyrie_dynasties = EyrieDynasties(EyrieRandomController())
    woodland_alliance = WoodlandAlliance(AllianceRandomController())
    vagabond = Vagabond(VagabondRandomController())

    settings = GameSettings(
        [marquise, eyrie_dynasties, woodland_alliance, vagabond])
    gm = GameManager(settings, TURN_LIMIT, marquise)
    gm.reset_ids()

    while not gm.done:
        if gm.current_message:
            action = gm.game_state.active_player.controller.send_game_message(
                gm.current_message)
            gm.step(action)
        else:
            gm.step()
        if gm.setup_complete:
            set_print_colour(
                gm.turn_order[gm.current_faction_index].print_colour)
        else:
            set_print_colour(
                gm.setup_order[gm.current_faction_setup_index].print_colour)
        if gm.current_message:
            print(f"Requiring message of type: {gm.current_message.type.name}")

    original_print("Game Over!")
    if isinstance(gm.winner, list):
        original_print("Winners:", ", ".join([str(f) for f in gm.winner]))
    elif gm.winner:
        original_print("Winner:", gm.winner)
    else:
        original_print("No winner declared.")
