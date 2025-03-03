from utils.root_types import Suits, Items
from typing import Tuple
from dataclasses import dataclass
from random import shuffle


@dataclass
class QuestCard():
    name: str
    suit: Suits
    items: Tuple[Items, Items]

    def __repr__(self):
        return f"{self.name} in a {self.suit.name.capitalize()} clearing"


RABBIT_ERRAND = QuestCard("Errand", Suits.RABBIT, (Items.TEA, Items.BOOTS))
FOX_ERRAND = QuestCard("Errand", Suits.FOX, (Items.TEA, Items.BOOTS))
MOUSE_ESCORT = QuestCard("Escort", Suits.MOUSE, (Items.BOOTS, Items.BOOTS))
RABBIT_EXPEL_BANDITS = QuestCard(
    "Expel Bandits", Suits.RABBIT, (Items.SWORD, Items.SWORD))
MOUSE_EXPEL_BANDITS = QuestCard(
    "Expel Bandits", Suits.MOUSE, (Items.SWORD, Items.SWORD))
RABBIT_FEND_BEAR = QuestCard(
    "Fend Off a Bear", Suits.RABBIT, (Items.TORCH, Items.CROSSBOW))
MOUSE_FEND_BEAR = QuestCard(
    "Fend Off a Bear", Suits.MOUSE, (Items.TORCH, Items.CROSSBOW))
FUNDRAISING = QuestCard("Fundraising", Suits.FOX, (Items.TEA, Items.COINS))
RABBIT_SPEECH = QuestCard(
    "Give a Speech", Suits.RABBIT, (Items.TORCH, Items.TEA))
FOX_SPEECH = QuestCard("Give a Speech", Suits.FOX, (Items.TORCH, Items.TEA))
RABBIT_GUARD_DUTY = QuestCard(
    "Guard Duty", Suits.RABBIT, (Items.TORCH, Items.SWORD))
MOUSE_GUARD_DUTY = QuestCard(
    "Guard Duty", Suits.MOUSE, (Items.TORCH, Items.SWORD))
FOX_LOGISTICS_HELP = QuestCard(
    "Logistics Help", Suits.FOX, (Items.BOOTS, Items.BAG))
MOUSE_LOGISTICS_HELP = QuestCard(
    "Logistics Help", Suits.MOUSE, (Items.BOOTS, Items.BAG))
REPAIR_A_SHED = QuestCard("Repair a Shed", Suits.FOX,
                          (Items.TORCH, Items.HAMMER))


class QuestDeck():
    def __init__(self):
        self.quests = [RABBIT_ERRAND, FOX_ERRAND, MOUSE_ESCORT, RABBIT_EXPEL_BANDITS,
                       MOUSE_EXPEL_BANDITS, RABBIT_FEND_BEAR, MOUSE_FEND_BEAR, FUNDRAISING, RABBIT_SPEECH, FOX_SPEECH, MOUSE_GUARD_DUTY, RABBIT_GUARD_DUTY, FOX_LOGISTICS_HELP, MOUSE_LOGISTICS_HELP, REPAIR_A_SHED]
        shuffle(self.quests)

    def draw(self, amount: int):
        drawn_cards = []
        while len(drawn_cards) < amount and len(self.quests) > 0:
            drawn_cards.append(self.quests.pop(0))
        return drawn_cards
