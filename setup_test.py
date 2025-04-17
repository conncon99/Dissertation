
from src.utils.game_settings import GameSettings
from src.utils.game_manager import GameManager
from src.factions.marquise_de_cat import Marquise
from src.factions.eyrie_dynasties import EyrieDynasties
from src.factions.woodland_alliance import WoodlandAlliance
from src.factions.vagabond.vagabond import Vagabond
from src.controllers.random_controllers import *
from src.controllers.player_controllers.marquise_player_controller import MarquisePlayerController
from src.controllers.player_controllers.alliance_player_controller import AlliancePlayerController
from src.controllers.player_controllers.eyrie_player_controller import EyriePlayerController
from src.controllers.player_controllers.vagabond_player_controller import VagabondPlayerController
import logging
import os

log_file = "training/logs/setup_test.log"
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

NUM_RUNS = 5
TURN_LIMIT = 100

for i in range(NUM_RUNS):

    marquise = Marquise(MarquiseRandomController())
    eyrie_dynasties = EyrieDynasties(EyrieRandomController())
    woodland_alliance = WoodlandAlliance(AllianceRandomController())
    # vagabond = Vagabond(VagabondRandomController())

    # marquise = Marquise(MarquisePlayerController())
    # eyrie_dynasties = EyrieDynasties(EyriePlayerController())
    # woodland_alliance = WoodlandAlliance(AlliancePlayerController())
    vagabond = Vagabond(VagabondPlayerController())

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

    logger.info("Game Over!")
    if isinstance(gm.winner, list):
        logger.info(f"Winners: {', '.join(str(f) for f in gm.winner)}")
    elif gm.winner:
        logger.info(f"Winner: {gm.winner}")
    else:
        logger.info("No winner declared.")
