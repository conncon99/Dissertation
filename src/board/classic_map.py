from board.map import Map
from board.forest import Forest
from utils.root_types import Suits


class ClassicMap(Map):

    def __init__(self, game_state) -> None:
        super().__init__(game_state)
        self.corner_clearings = [
            self.clearings[0], self.clearings[2], self.clearings[8], self.clearings[11]]

    def create_clearings(self) -> None:
        self.create_new_clearing(0, Suits.FOX, 1, False)
        self.create_new_clearing(1, Suits.RABBIT, 2, False)
        self.create_new_clearing(2, Suits.MOUSE, 2, False)
        self.create_new_clearing(3, Suits.RABBIT, 2, True)
        self.create_new_clearing(4, Suits.MOUSE, 2, False)
        self.create_new_clearing(5, Suits.FOX, 2, True)
        self.create_new_clearing(6, Suits.MOUSE, 3, True)
        self.create_new_clearing(7, Suits.FOX, 2, True)
        self.create_new_clearing(8, Suits.RABBIT, 1, False)
        self.create_new_clearing(9, Suits.FOX, 2, False)
        self.create_new_clearing(10, Suits.MOUSE, 2, False)
        self.create_new_clearing(11, Suits.RABBIT, 1, False)

    def create_forests(self) -> None:
        self.forests = [Forest(i, self.game_state) for i in range(7)]

    def set_up_clearings(self) -> None:
        self.add_clearing_connections(self.clearings[0], [1, 3, 4])
        self.add_clearing_connections(self.clearings[1], [0, 2])
        self.add_clearing_connections(self.clearings[2], [1, 3, 7])
        self.add_clearing_connections(self.clearings[3], [0, 2, 5])
        self.add_clearing_connections(self.clearings[4], [0, 5, 8])
        self.add_clearing_connections(self.clearings[5], [4, 3, 6, 8, 10])
        self.add_clearing_connections(self.clearings[6], [5, 7, 11])
        self.add_clearing_connections(self.clearings[7], [2, 6, 11])
        self.add_clearing_connections(self.clearings[8], [4, 5, 9])
        self.add_clearing_connections(self.clearings[9], [8, 10])
        self.add_clearing_connections(self.clearings[10], [5, 9, 11])
        self.add_clearing_connections(self.clearings[11], [10, 6, 7])

    def set_up_forests(self) -> None:
        self.add_forest_connections(self.forests[0], clearing_indexes=[
                                    0, 1, 3, 2], forest_indexes=[1, 2])
        self.add_forest_connections(self.forests[1], clearing_indexes=[
                                    0, 3, 4, 5], forest_indexes=[0, 2, 3])
        self.add_forest_connections(self.forests[2], clearing_indexes=[
                                    3, 2, 5, 6, 7], forest_indexes=[0, 1, 5, 6])
        self.add_forest_connections(self.forests[3], clearing_indexes=[
                                    4, 5, 8], forest_indexes=[1, 4])
        self.add_forest_connections(self.forests[4], clearing_indexes=[
                                    5, 8, 9, 10], forest_indexes=[3, 5])
        self.add_forest_connections(self.forests[5], clearing_indexes=[
                                    5, 6, 10, 11], forest_indexes=[2, 4, 6])
        self.add_forest_connections(self.forests[6], clearing_indexes=[
                                    6, 7, 11], forest_indexes=[2, 5])

    def get_opposite_corner(self, clearing):
        if clearing.index == 2:
            return self.clearings[8]
        elif clearing.index == 8:
            return self.clearings[2]
        elif clearing.index == 0:
            return self.clearings[11]
        elif clearing.index == 11:
            return self.clearings[0]
        raise IndexError
