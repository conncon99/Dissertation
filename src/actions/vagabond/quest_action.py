from __future__ import annotations
from actions.action_handler import Action
from typing import TYPE_CHECKING
from utils.root_types import Items, Suits
from board.clearing import Clearing
from controllers.messages.game_messages import ChooseQuestMessage, ChooseQuestRewardMessage

if TYPE_CHECKING:
    from factions.vagabond.vagabond import Vagabond
    from factions.vagabond.quests import QuestCard


class QuestAction(Action):
    def __init__(self, name="Quest", max_uses=None, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)

    def can_perform(self, executor: Vagabond, game_state=None):
        return len(executor.quest_cards) > 0 and isinstance(executor.vagabond_pawn.space, Clearing) and any(self._can_complete_quest(executor, quest_card) and quest_card.suit == executor.vagabond_pawn.space.get_suit() for quest_card in executor.quest_cards)

    def perform(self, game_state, executor: Vagabond):
        available_quests = [quest for quest in executor.quest_cards if quest.suit ==
                            executor.vagabond_pawn.space.get_suit() and self._can_complete_quest(executor, quest)]

        # Choose Quest

        chosen_quest = executor.controller.send_game_message(
            ChooseQuestMessage(available_quests)).chosen_quest

        print(
            f" - completed quest: '{chosen_quest}' in Clearing {executor.vagabond_pawn.space.index}")

        item1, item2 = chosen_quest.items
        executor.satchel.exhaust_item(item1)
        executor.satchel.exhaust_item(item2)

        executor.completed_quests[chosen_quest.suit] += 1
        new_quest_card = executor.quest_deck.draw(1)
        print(f" - Drew new quest card: {new_quest_card}")
        executor.quest_cards.extend(new_quest_card)

        # Choose Reward
        take_vp_reward = executor.controller.send_game_message(
            ChooseQuestRewardMessage()).take_vp_reward

        if take_vp_reward:
            executor.add_vp(executor.completed_quests[chosen_quest.suit])
            print(
                f" - Gaining {executor.completed_quests[chosen_quest.suit]} victory points as a reward")
        else:
            reward_cards = executor.deck.draw(2)
            executor.hand.extend(reward_cards)
            print(f" - Drew cards {reward_cards} as a reward")

        return super().perform(game_state, executor)

    def _can_complete_quest(self, executor: Vagabond, quest_card: QuestCard) -> bool:
        item1, item2 = quest_card.items
        # Needs two of the same item
        if item1 == item2:
            return executor.satchel.available_items[item1] >= 2
        else:
            return executor.satchel.available_items[item1] >= 1 and executor.satchel.available_items[item2] >= 1
