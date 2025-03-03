from actions.action_handler import Action


class BuildAction(Action):
    def __init__(self, name, max_uses=None):
        super().__init__(name, max_uses)

    def can_perform(self, executor):
        return super().can_perform(executor)

    def perform(self, game_state, executor):
        return super().perform(game_state, executor)
