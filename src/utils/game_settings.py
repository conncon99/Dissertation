from typing import List
from src.factions.faction import Faction
import numpy as np


class GameSettings:
    def __init__(self, faction_list: List[Faction], use_manual_rolling=False, use_manual_card_draw=False) -> None:
        self.faction_list = faction_list
        self.num_factions = len(faction_list)
        self.faction_ids = [
            faction.faction_id for faction in self.faction_list]
        self.use_manual_rolling = use_manual_rolling
        self.use_manual_card_draw = use_manual_card_draw
        self.turn_order = None

    def randomize_turn_order(self) -> List[Faction]:
        """Generates a random turn order from the list of factions"""
        if not self.turn_order:
            turn_order = [faction for faction in self.faction_list]
            np.random.shuffle(turn_order)
            self.turn_order = turn_order
        return self.turn_order

    def get_setup_order(self) -> List[Faction]:
        return sorted(self.faction_list, key=lambda f: f.setup_order)
