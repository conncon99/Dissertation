from __future__ import annotations
from cards.cards import *
from random import shuffle
from typing import TYPE_CHECKING, List
from cards.cards import DOMINANCE_CARDS

if TYPE_CHECKING:
    from cards.card import Card
    from factions.faction import Faction
    from board.map import Map


class Deck:

    def __init__(self, map: Map) -> None:
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
            BIRD_AMBUSH_2,
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
            SCOUTING_PARTY_2,
            COMMAND_WARREN,
            COMMAND_WARREN_2,
            COBBLER,
            COBBLER_2,
            SAPPERS,
            SAPPERS_2,
            BRUTAL_TACTICS,
            BRUTAL_TACTICS_2,
            ARMORERS,
            ARMORERS_2,
            BETTER_BURROW_BANK,
            BETTER_BURROW_BANK_2,
            STAND_AND_DELIVER,
            STAND_AND_DELIVER_2,
            TAX_COLLECTOR,
            TAX_COLLECTOR_2,
            TAX_COLLECTOR_3,
            CODEBREAKERS,
            CODEBREAKERS_2,
            ROYAL_CLAIM
        ]
        self.map = map

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
        if card in executor.hand:
            executor.hand.remove(card)

        if card in DOMINANCE_CARDS:
            self.map.available_dominance_cards.append(card)
            print(f" - Placed {card} in available dominance card pile")
        else:
            self.discard.append(card)
            print(f" - Discarded '{card}'")
