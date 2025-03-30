from __future__ import annotations
from typing import TYPE_CHECKING
from utils.root_types import Factions
import math

if TYPE_CHECKING:
    from utils.game_state import GameState


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


class RewardHelper:
    def __init__(self):
        self.prev_vp = 0
        self.prev_warriors = 0
        self.prev_actives = 0
        self.prev_clearings_ruled = 0
        self.turn_penalty = 0.1

    def calculate_reward(self, game_state: GameState):
        if game_state.marquise.dominance is None:
            vp_diff = (game_state.marquise.victory_points - self.prev_vp)
            reward = vp_diff - self.turn_penalty
        else:
            reward = self.get_dominance_reward(game_state) - self.turn_penalty
        self.update_values(game_state)
        return reward

    def update_values(self, game_state: GameState):
        self.prev_vp = game_state.marquise.victory_points
        self.prev_warriors = len(game_state.marquise.units)
        self.prev_actives = len(game_state.marquise.active_cards)
        self.prev_clearings_ruled = self.get_clearings_ruled(game_state)

    def get_clearings_ruled(self, game_state: GameState):
        total = 0
        for clearing in game_state.board.clearings:
            if clearing.get_owner() == Factions.MARQUISE_DE_CAT.value:
                total += 1
        return total

    def get_dominance_reward(self, game_state: GameState):
        total = 0
        for clearing in game_state.board.clearings:
            if clearing.get_owner() == Factions.MARQUISE_DE_CAT.value and clearing.get_suit() == game_state.marquise.dominance:
                total += 1
        return total / 2
