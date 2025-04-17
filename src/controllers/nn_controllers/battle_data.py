from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.factions.faction import Faction
    from src.board.clearing import Clearing


class BattleData:
    def __init__(self, attacker: Faction, defender: Faction, battle_clearing: Clearing, is_attacker: bool, been_ambushed: bool = None, used_ambush: bool = None, attacker_damage_modifier: int = 0, defender_damage_modifier: int = 0, attacker_roll: int = 0, defender_roll: int = 0):
        self.attacker = attacker
        self.defender = defender
        self.is_attacker = is_attacker
        self.been_ambushed = been_ambushed
        self.used_ambush = used_ambush
        self.attacker_damage_modifier = attacker_damage_modifier
        self.defender_damage_modifier = defender_damage_modifier
        self.attacker_roll = attacker_roll
        self.defender_roll = defender_roll
        self.battle_clearing = battle_clearing
