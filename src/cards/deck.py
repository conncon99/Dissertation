from __future__ import annotations
from cards.cards import *
from random import shuffle
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from cards.card import Card
    from factions.faction import Faction


class Deck:

    def __init__(self) -> None:
        self.deck = [
            # Item Cards
            SWORD_MOUSE,
            TRAVEL_GEAR_FOX,
            TRAVEL_GEAR_MOUSE,
            WOODLAND_RUNNERS,
            ANVIL,
            ARMS_TRADER,
            A_VISIT_TO_FRIENDS,
            BAKE_SALE,
            BIRDY_BUNDLE,
            CROSSBOW_BIRD,
            CROSSBOW_MOUSE,
            FOXFOLK_STEEL,
            GENTLY_USED_KNAPSACK,
            INVESTMENTS,
            MOUSE_IN_A_SACK,
            PROTECTION_RACKET,
            ROOT_TEA_RABBIT,
            ROOT_TEA_FOX,
            ROOT_TEA_MOUSE,
            SMUGGLERS_TRAIL,
            # Ambush Cards
            BIRD_AMBUSH,
            BIRD_AMBUSH,
            FOX_AMBUSH,
            MOUSE_AMBUSH,
            RABBIT_AMBUSH,
            # Dominance Cards
            FOX_DOMINANCE,
            MOUSE_DOMINANCE,
            RABBIT_DOMINANCE,
            BIRD_DOMINANCE,
            # Favour Cards
            FAVOR_OF_THE_RABBITS,
            FAVOR_OF_THE_FOXES,
            FAVOR_OF_THE_MICE,
            # Misc Cards
            SCOUTING_PARTY,
            COMMAND_WARREN,
            COBBLER,
            SAPPERS,
            BRUTAL_TACTICS,
            ARMORERS,
            BETTER_BURROW_BANK
        ]

        self.discard = []

    def shuffle(self):
        """Shuffle the deck"""
        shuffle(self.deck)

    def draw(self, number: int) -> List[Card]:
        """Draw a specified number of cards from the deck"""
        drawn_cards = []
        while len(drawn_cards) < number:
            # If the deck is empty, replenish it
            if not self.deck and self.discard != []:
                print(f" - Deck is empty, replenishing...")
                self.replenish_deck()
            elif not self.deck and not self.discard:
                print(f" - Deck and Discard are empty, no card drawn")
                return drawn_cards
            drawn_cards.append(self.deck.pop(0))
        return drawn_cards

    def replenish_deck(self):
        if len(self.deck) == 0:
            self.deck = self.discard.copy()
            self.shuffle()
            self.discard.clear()

    def discard_card(self, card: Card, executor: Faction):
        self.discard.append(card)
        if card in executor.hand:
            executor.hand.remove(card)
        print(f" - Discarded '{card}'")
