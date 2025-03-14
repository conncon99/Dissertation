from typing import List
from factions.faction import Faction
from random import shuffle


class GameSettings:
    def __init__(self, faction_list: List[Faction]) -> None:
        self.faction_list = faction_list
        self.num_factions = len(faction_list)
        self.faction_ids = [
            faction.faction_id for faction in self.faction_list]

    def randomize_turn_order(self) -> List[Faction]:
        """Generates a random turn order from the list of factions"""
        turn_order = [faction for faction in self.faction_list]
        shuffle(turn_order)
        return turn_order
