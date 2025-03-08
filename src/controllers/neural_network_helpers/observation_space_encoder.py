from typing import TYPE_CHECKING
import numpy as np
from controllers.messages.game_messages import GameMessages, GameMessage

if TYPE_CHECKING:
    from utils.game_state import GameState
    from factions.faction import Faction


class ObservationSpace:
    def __init__(self):
        pass

    def encode_game_state(game_state: GameState, faction: Faction):
        return np.array([
            #### GENERAL ####
            # Active faction (who is using this)
            # Current Turn Count
            # Current Player
            # Current Phase
            # Current Callback Time/BattleCallback Time
            # Marquise de Cat Turn order
            # Eyrie Dynasties Turn order
            # Woodland Alliance Turn order
            # Vagabond Turn order

            # Marquise Victory Points
            # Eyrie Dynasties Victory Points
            # Woodland Alliance Victory Points
            # Vagabond Victory Points

            # Marquise Dominance Status
            # Eyrie Dynasties Dominance Status
            # Woodland Alliance Dominance Status
            # Vagabond Coalition Status

            # Marquise Crafted Items
            # Eyrie Dynasties Crafted Items
            # Woodland Alliance Crafted Items
            # Vagabond Crafted Items

            #### HANDS #####

            # One hot encoded hand (54 cards)
            # One hot encoded active cards (11 cards?)

            # TODO: Other player actives cards and hands

            #### BOARD ####

            # For each clearing
            # Clearing faction ruler
            # Clearing suit
            # Total clearing slots
            # Available clearing slots
            # Marquise de cat warrior count (normalized via max faction warrior count)
            # Eyrie Dynasties warrior count
            # Woodland Alliance warrior count
            # is vagabond pawn on this space?

            # MARQUISE
            # Wood Count
            # has Keep?
            # Recruiter count
            # Workshop count
            # Sawmill Count

            # EYRIE DYNASTIES
            # has Roost?

            # WOODLAND ALLIANCE
            # has Sympathy
            # has Base

            # Vagabond
            # has Ruin

            # For each Forest
            # Has Vagabond Pawn?

            #### MARQUISE SPECIFIC ####
            # number of sawmills
            # number of recruiters
            # number of workshops
            # number of units

            #### EYRIE DYNASTIES SPECIFIC ####
            # number of roosts
            # number of units
            # Eyrie Leader ID
            # Decree Strucutre

            #### WOODLAND ALLIANCE SPECIFIC ####
            # Number of bases
            # Number of supporters
            # Makeup of supporters - private info for WA only
            # Number of sympathy tokens
            # Number of officers

            #### VAGABOND SPECIFIC ####
            # Vagabond Character
            # One hot encoded available satchel items
            # One hot encoded exhausted satchel items
            # One hot encoded exhausted damaged satchel items
            # One hot encoded damaged satchel items
            # Bag Track Count
            # Tea Track Count
            # Coin track count

            # Marquise De Cat relatonship status
            # Eyrie Dynasties relationship status
            # Woodland Alliance relationship status


            #### GameMessage ####
            # one hot encoded game message type

            #### Actions ####
            # one hot encoded available action - all 0 if not ActionChoiceMessage


        ])
