from cards.card import *
from utils.root_types import Suits, Items

# Royal Viziers

ROYAL_VIZIER_1 = Card(Suits.BIRD, "Royal Vizier 1", False, "")
ROYAL_VIZIER_2 = Card(Suits.BIRD, "Royal Vizier 2", False, "")

# Item Cards
SWORD_MOUSE = ItemCard(
    Suits.MOUSE, vp_bonus=2, item_bonus=Items.SWORD, name="Swords Mouse"
).make_craftable(fox_count=2)
TRAVEL_GEAR_FOX = ItemCard(
    Suits.FOX, vp_bonus=1, item_bonus=Items.BOOTS, name="Travel Gear Fox"
).make_craftable(rabbit_count=1)
TRAVEL_GEAR_MOUSE = ItemCard(
    Suits.MOUSE, vp_bonus=1, item_bonus=Items.BOOTS, name="Travel Gear Mouse"
).make_craftable(rabbit_count=1)
WOODLAND_RUNNERS = ItemCard(
    Suits.BIRD, vp_bonus=1, item_bonus=Items.BOOTS, name="Woodland Runners"
).make_craftable(rabbit_count=1)
ANVIL = ItemCard(
    Suits.FOX, vp_bonus=2, item_bonus=Items.HAMMER, name="Anvil"
).make_craftable(fox_count=1)
ARMS_TRADER = ItemCard(
    Suits.BIRD, vp_bonus=2, item_bonus=Items.SWORD, name="Arms Trader"
).make_craftable(fox_count=2)
A_VISIT_TO_FRIENDS = ItemCard(
    Suits.RABBIT, vp_bonus=1, item_bonus=Items.BOOTS, name="A visit to Friends"
).make_craftable(rabbit_count=1)
BAKE_SALE = ItemCard(
    Suits.RABBIT, vp_bonus=3, item_bonus=Items.COINS, name="Bake Sale"
).make_craftable(rabbit_count=2)
BIRDY_BUNDLE = ItemCard(
    Suits.BIRD, vp_bonus=1, item_bonus=Items.BAG, name="Birdy Bundle"
).make_craftable(mouse_count=1)
CROSSBOW_BIRD = ItemCard(
    Suits.BIRD, vp_bonus=1, item_bonus=Items.CROSSBOW, name="Crossbow Bird"
).make_craftable(fox_count=1)
CROSSBOW_MOUSE = ItemCard(
    Suits.MOUSE, vp_bonus=1, item_bonus=Items.CROSSBOW, name="Crossbow Mouse"
).make_craftable(fox_count=1)
FOXFOLK_STEEL = ItemCard(
    Suits.FOX, vp_bonus=2, item_bonus=Items.SWORD, name="Foxfolk Steel"
).make_craftable(fox_count=2)
GENTLY_USED_KNAPSACK = ItemCard(
    Suits.FOX, vp_bonus=1, item_bonus=Items.BAG, name="Gently used knapsack"
).make_craftable(mouse_count=1)
INVESTMENTS = ItemCard(
    Suits.MOUSE, vp_bonus=3, item_bonus=Items.COINS, name="Investments"
).make_craftable(rabbit_count=2)
MOUSE_IN_A_SACK = ItemCard(
    Suits.MOUSE, vp_bonus=1, item_bonus=Items.BAG, name="Mouse in a Sack"
).make_craftable(mouse_count=1)
PROTECTION_RACKET = ItemCard(
    Suits.FOX, vp_bonus=3, item_bonus=Items.COINS, name="Protection Racket"
).make_craftable(rabbit_count=2)
ROOT_TEA_RABBIT = ItemCard(
    Suits.RABBIT, vp_bonus=2, item_bonus=Items.TEA, name="Root Tea Rabbit"
).make_craftable(mouse_count=1)
ROOT_TEA_FOX = ItemCard(
    Suits.FOX, vp_bonus=2, item_bonus=Items.TEA, name="Root Tea Fox"
).make_craftable(mouse_count=1)
ROOT_TEA_MOUSE = ItemCard(
    Suits.MOUSE, vp_bonus=2, item_bonus=Items.TEA, name="Root Tea Mouse"
).make_craftable(mouse_count=1)
SMUGGLERS_TRAIL = ItemCard(
    Suits.RABBIT, vp_bonus=1, item_bonus=Items.BAG, name="Smugglers Trail"
).make_craftable(mouse_count=1)

# # Favour Cards
FAVOR_OF_THE_FOXES = FavourCard(
    Suits.FOX, "Favor of the Foxes").make_craftable(fox_count=3)
FAVOR_OF_THE_MICE = FavourCard(
    Suits.MOUSE, "Favor of the Mice").make_craftable(mouse_count=3)
FAVOR_OF_THE_RABBITS = FavourCard(
    Suits.RABBIT, "Favor of the Rabbits").make_craftable(rabbit_count=3)

# Dominance Cards
BIRD_DOMINANCE = DominanceCard(Suits.BIRD, "Bird Dominance")
FOX_DOMINANCE = DominanceCard(Suits.FOX, "Fox Dominance")
MOUSE_DOMINANCE = DominanceCard(Suits.MOUSE, "Mouse Dominance")
RABBIT_DOMINANCE = DominanceCard(Suits.RABBIT, "Rabbit Dominance")

DOMINANCE_CARDS = [BIRD_DOMINANCE, FOX_DOMINANCE,
                   MOUSE_DOMINANCE, RABBIT_DOMINANCE]

# Ambush Cards
BIRD_AMBUSH = AmbushCard(Suits.BIRD, "Bird Ambush")
FOX_AMBUSH = AmbushCard(Suits.FOX, "Fox Ambush")
RABBIT_AMBUSH = AmbushCard(Suits.RABBIT, "Rabbit Ambush")
MOUSE_AMBUSH = AmbushCard(Suits.MOUSE, "Mouse Ambush")

AMBUSH_CARDS = [BIRD_AMBUSH, FOX_AMBUSH, RABBIT_AMBUSH, MOUSE_AMBUSH]

# Misc Cards
SCOUTING_PARTY = Card(Suits.MOUSE, "Scouting Party", True,
                      "As attacker in battle, you are not affected by ambush cards.").make_craftable(mouse_count=2)
COMMAND_WARREN = CommandWarrenCard()
COBBLER = CobblerCard()
SAPPERS = SappersCard()
BRUTAL_TACTICS = BrutalTacticsCard()
ARMORERS = ArmorersCard()
BETTER_BURROW_BANK = BetterBurrowBankCard()
