from actions.action_handler import Action
from utils.callback_handler import CallbackTimes
from actions.action_group_registry import ActionIDs


class RoyalClaimAction(Action):
    def __init__(self, card, name="Royal Claim", max_uses=1, is_action_group_modifier=True, group_spanning=True):
        super().__init__(name, max_uses, is_action_group_modifier, group_spanning)
        self.card = card
        self.id = ActionIDs.ROYAL_CLAIM

    def can_perform(self, executor, game_state=None):
        return super().can_perform(executor, game_state)

    def perform(self, game_state, executor):
        num_ruled = 0
        for clearing in game_state.board.clearings:
            if clearing.get_owner() == executor.faction_id:
                num_ruled += 1
        executor.add_vp(num_ruled)
        print(
            f" - {executor} gained {num_ruled} victory points from ruling {num_ruled} clearings")

        executor.active_cards.remove(self.card)

        for action_group in executor.actions[CallbackTimes.IN_BIRDSONG]:
            if self in action_group.actions:
                action_group.actions.remove(self)

        return super().perform(game_state, executor)
        yield
