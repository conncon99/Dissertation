from __future__ import annotations
from typing import TYPE_CHECKING, Dict
from utils.root_types import Factions

if TYPE_CHECKING:
    from factions.vagabond.vagabond import Vagabond

# Relationship Track
# Marker for each faction
# Victory points and costs associated with moving between each value
HOSTILE = 0
INDIFFERENT = 1
ALLIED = 4


class RelationshipTrack:
    def __init__(self, vagabond: Vagabond):
        self.vagabond = vagabond
        # {Faction ID : Relationship Level}
        self.relationship_level: Dict[int, int] = {
            faction.value: INDIFFERENT for faction in Factions if faction != Factions.VAGABOND}
        # {Faction ID: Number of times they have been aided this turn}
        self.aids_this_turn: Dict[int, int] = {
            faction.value: 0 for faction in Factions if faction != Factions.VAGABOND}
        # {Relationship Level: Aids required for a level up}
        self.aids_per_level_up: Dict[int, int] = {
            HOSTILE: 999, INDIFFERENT: 1, 2: 2, 3: 3, ALLIED: 999}
        # {Relationship Level: VP reward on reaching that level}
        self.level_up_rewards: Dict[int, int] = {
            HOSTILE: 0, INDIFFERENT: 0, 2: 1, 3: 2, ALLIED: 2}

    def reset_aids_per_turn(self):
        for faction_id in self.aids_this_turn.keys():
            self.aids_this_turn[faction_id] = 0

    def aid_faction(self, faction_id: int):

        if self.relationship_level[faction_id] == ALLIED:
            self.vagabond.add_vp(2)
            print(f" - Gained 2 VP for aiding an allied faction")
        self.aids_this_turn[faction_id] += 1
        print(f" - Aids This Turn: {self.aids_this_turn[faction_id]}")
        relationship_level = self.relationship_level[faction_id]
        if self.aids_this_turn[faction_id] == self.aids_per_level_up[relationship_level] and (self.relationship_level[faction_id] != HOSTILE or self.relationship_level[faction_id] != ALLIED):
            self.relationship_level[faction_id] += 1
            self.aids_this_turn[faction_id] = 0
            self.vagabond.add_vp(
                self.level_up_rewards[self.relationship_level[faction_id]])
            print(
                f" - Relationship level increased, gaining {self.level_up_rewards[self.relationship_level[faction_id]]} VP")
