from __future__ import annotations
from src.actions.action_handler import Action
from typing import TYPE_CHECKING
from src.utils.root_types import Items
from src.board.clearing import Clearing
from src.controllers.messages.game_messages import ChooseQuestMessage, ChooseQuestRewardMessage, QuestUseItemTrackMessage
from src.controllers.messages.controller_messages import QuestUseItemTrackResponse
from src.actions.action_group_registry import ActionIDs

if TYPE_CHECKING:
    from src.factions.vagabond.vagabond import Vagabond
    from src.factions.vagabond.quests import QuestCard


class QuestAction(Action):
    def __init__(self, name="Quest", max_uses=None, is_action_group_modifier=False):
        super().__init__(name, max_uses, is_action_group_modifier)
        self.id = ActionIDs.QUEST

    def can_perform(self, executor: Vagabond, game_state=None):
        return len(executor.quest_cards) > 0 and isinstance(executor.vagabond_pawn.space, Clearing) and any(self._can_complete_quest(executor, quest_card) and quest_card.suit == executor.vagabond_pawn.space.get_suit() for quest_card in executor.quest_cards)

    def perform(self, game_state, executor: Vagabond):
        available_quests = [quest for quest in executor.quest_cards if quest.suit ==
                            executor.vagabond_pawn.space.get_suit() and self._can_complete_quest(executor, quest)]

        # Choose Quest

        response = yield ChooseQuestMessage(game_state, self.action_group, available_quests)
        chosen_quest = response.chosen_quest

        self.logger.info(
            f" - completed quest: '{chosen_quest}' in Clearing {executor.vagabond_pawn.space.index}")

        item1, item2 = chosen_quest.items
        use_item_track_1, use_item_track_2 = False, False
        if self._get_track_item_count(executor, item1) > 0 and executor.satchel.available_items[item1] > 0:
            response: QuestUseItemTrackResponse = yield QuestUseItemTrackMessage(game_state, self.action_group, executor.satchel.available_items[item1], self._get_track_item_count(executor, item1))
            use_item_track_1 = response.use_item_track
        elif self._get_track_item_count(executor, item1) > 0:
            use_item_track_1 = True
        executor.satchel.exhaust_item(item1, use_item_track_1)

        if self._get_track_item_count(executor, item2) > 0 and executor.satchel.available_items[item2] > 0:
            response: QuestUseItemTrackResponse = yield QuestUseItemTrackMessage(game_state, self.action_group, executor.satchel.available_items[item2], self._get_track_item_count(executor, item2))
            use_item_track_2 = response.use_item_track
        elif self._get_track_item_count(executor, item2) > 0:
            use_item_track_2 = True
        executor.satchel.exhaust_item(item2, use_item_track_2)

        executor.completed_quests[chosen_quest.suit] += 1
        new_quest_card = executor.quest_deck.draw(1)
        self.logger.info(f" - Drew new quest card: {new_quest_card}")
        executor.quest_cards.extend(new_quest_card)

        # Choose Reward
        response = yield ChooseQuestRewardMessage(game_state, self.action_group)
        take_vp_reward = response.take_vp_reward

        if take_vp_reward:
            executor.add_vp(executor.completed_quests[chosen_quest.suit])
            self.logger.info(
                f" - Gaining {executor.completed_quests[chosen_quest.suit]} victory points as a reward")
        else:
            reward_cards = executor.deck.draw(2)
            executor.hand.extend(reward_cards)
            self.logger.info(f" - Drew cards {reward_cards} as a reward")

        return super().perform(game_state, executor)

    def _can_complete_quest(self, executor: Vagabond, quest_card: QuestCard) -> bool:
        item1, item2 = quest_card.items
        # Needs two of the same item

        item1_track_val = self._get_track_item_count(executor, item1)
        item2_track_val = self._get_track_item_count(executor, item2)

        if item1 == item2:
            return executor.satchel.available_items[item1] + item1_track_val >= 2
        else:
            return executor.satchel.available_items[item1] + item1_track_val >= 1 and executor.satchel.available_items[item2] + item2_track_val >= 1

    def _get_track_item_count(self, executor: Vagabond, item: Items) -> int:
        item_track_val = 0
        if item == Items.BAG:
            item_track_val = executor.active_bag_count
        elif item == Items.COINS:
            item_track_val = executor.active_coin_count
        elif item == Items.TEA:
            item_track_val = executor.active_tea_count
        return item_track_val
