from src.actions.action_handler import Action
from src.utils.root_types import Suits
from src.actions.action_group_registry import ActionIDs


class DominanceAction(Action):
    def __init__(self, name="Dominance Action", max_uses=1, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.id = ActionIDs.DOMINANCE

    def can_perform(self, executor, game_state):
        return super().can_perform(executor, game_state)

    def perform(self, game_state, executor):
        if executor.dominance == Suits.BIRD:
            # Rule two opposite corner clearings (3.3.1.II)
            board = game_state.board
            if any(corner.get_owner() == executor.faction_id and board.get_opposite_corner(corner).get_owner() == executor.faction_id for corner in board.corner_clearings):
                executor.has_won = True
                self.logger.info(f"{executor} has acheived Bird Dominance")
        else:
            dominance_count = 0
            for clearing in game_state.board.clearings:
                if clearing.get_suit() == executor.dominance and clearing.get_owner() == executor.faction_id:
                    dominance_count += 1
            self.logger.info(
                f" - {executor} controls {dominance_count} {executor.dominance.name.capitalize()} Clearings")
            if dominance_count >= 3:
                self.logger.info(
                    f" - {executor} has achieved {executor.dominance.name.capitalize()} Dominance and won")
                executor.has_won = True
        return super().perform(game_state, executor)
        yield
