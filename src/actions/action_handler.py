"""Turns can be broken up into 3 stages:
    1. Phases - Birdsong, Daylight, Evening
    2. ActionGroup - the list of actions that can be taken at a given moment
    3. Action - the atomic action that is undertaken, e.g. Battle, Move

"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional, TYPE_CHECKING, Dict
from math import inf
from utils.game_state import GameState
from controllers.messages.game_messages import ActionChoiceMessage
from actions.action_group_registry import ActionGroupRegistry
if TYPE_CHECKING:
    from factions.faction import Faction


class Action(ABC):
    """
    :param name: A unique name for the action (e.g., 'Move', 'Battle').
    :param max_uses: Maximum times this action can be used. None -> unlimited.
    :param is_ordered: If True, this action must be done in a specific order
                        (within an ordered group).
    """

    def __init__(self, name: str, max_uses: Optional[int] = None, is_action_group_modifier: bool = False, group_spanning: bool = False) -> None:
        self.name = name
        self.max_uses = max_uses if max_uses is not None else inf
        self.times_used = 0
        self.is_action_group_modifier = is_action_group_modifier
        # Whether the action exists across multiple groups
        self.group_spanning = group_spanning
        self.id = -1
        self.action_group: ActionGroup = None

    @abstractmethod
    def can_perform(self, executor: Faction, game_state: Optional[GameState] = None) -> bool:
        if self.group_spanning and self in executor.used_spanning_actions.keys():
            self.times_used = executor.used_spanning_actions[self]
        return self.times_used < self.max_uses

    @abstractmethod
    def perform(self, game_state: GameState, executor: Faction) -> None:
        print(f" - {self.name} action completed\n")
        if self.group_spanning and self in executor.used_spanning_actions.keys():
            executor.used_spanning_actions[self] += 1
        elif self.group_spanning:
            executor.used_spanning_actions[self] = 1
        else:
            self.times_used += 1
        return


class ActionGroup:

    def __init__(self, name: str, ordered: bool = False, actions: List[Action] = None, max_total_uses: Optional[int] = None, can_abort: bool = False):
        """
        :param name: Name/description of the group (e.g. 'Craft', 'Up to 3 Actions').
        :param ordered: If True, the actions in this group must be done in order.
        :param actions: A list of Action objects.
        :param max_total_uses: Maximum times *any* actions in this group can be used (combined).
                               None -> no shared limit. Each Action might still have its own limit.
        """
        self.name = name
        self.id = id
        self.ordered = ordered
        self.actions = actions if actions is not None else []
        self.was_max_assigned = max_total_uses != None
        self.max_total_uses = len(
            self.actions) if self.ordered else max_total_uses if max_total_uses is not None else inf
        self.original_max = self.max_total_uses
        self.total_uses = 0  # Tracks how many actions have been performed in this group so far
        self.cancel_group = False

        # Whether this action group can be aborted before all actions are played
        self.can_abort = can_abort
        self.id = self._assign_unique_id()
        print(f"ID: {self.id}: {self.name}")

    def _assign_unique_id(self):
        """Generate a globally unique integer ID for this ActionGroup."""
        registry = ActionGroupRegistry()  # Singleton instance
        return registry.get_unique_id()

    def can_perform_any_action(self):
        return self.total_uses < self.max_total_uses

    def run_group(self, executor, game_state):
        """
        Execute actions in this group according to the constraints:
            - If 'ordered=True', iterate in sequence.
            - If 'ordered=False', let the player pick any action
        """
        self._assign_action_group()
        if self.cancel_group:
            return

        print(f"\n[GROUP] Starting '{self.name}' (ordered={self.ordered})")
        if not isinstance(self.actions, list):
            self.actions = [self.actions]

        if self.ordered:
            self._run_ordered_group(executor, game_state)
        else:
            self._run_non_ordered_group(executor, game_state)

        print(f"- Finished {self.name}")
        self.reset_action_group()

    def _run_ordered_group(self, executor, game_state):

        if not self.was_max_assigned:
            self.max_total_uses = len(self.actions)

        remaining_actions = self.actions[:]  # Copy of the action list

        while remaining_actions:
            if self.cancel_group:
                print(f"- Cancelling action group")
                return
            if not self.can_perform_any_action():
                print(f"- No more actions can be performed in this group")
                break

            # Filter actions that can still be performed
            available_actions = [
                action for action in remaining_actions if action.can_perform(executor, game_state)]

            if not available_actions:
                print(f"- No available actions left to perform")
                break

            # Send a game message to choose the next action
            chosen_action = executor.controller.send_game_message(
                ActionChoiceMessage(available_actions)
            ).chosen_action

            print(f"- Performing action '{chosen_action.name}'")
            chosen_action.perform(game_state, executor)
            self.total_uses += 1
            remaining_actions.remove(chosen_action)

        self._perform_available_modifiers(executor, game_state)

    def _run_non_ordered_group(self, executor: Faction, game_state):
        while True:
            modifiers = [a for a in self.actions if a.is_action_group_modifier and a.can_perform(
                executor, game_state)]
            primaries = [a for a in self.actions if not a.is_action_group_modifier and a.can_perform(
                executor, game_state)]

            if self.can_abort:
                if modifiers:
                    modifiers.append(None)
                if primaries:
                    primaries.append(None)

            if not modifiers and not primaries:
                print("- No available actions to perform in this group")
                break

            if not self.can_perform_any_action() and modifiers:
                chosen_action: Optional[Action] = executor.controller.send_game_message(
                    ActionChoiceMessage(modifiers)).chosen_action
            elif primaries:
                chosen_action: Optional[Action] = executor.controller.send_game_message(
                    ActionChoiceMessage(primaries)).chosen_action
            elif modifiers:
                chosen_action: Optional[Action] = executor.controller.send_game_message(
                    ActionChoiceMessage(modifiers)).chosen_action
            else:
                break

            if chosen_action is None:
                print(
                    f"- Aborting '{self.name}' with {self.max_total_uses - self.total_uses} actions remaining")
                break

            print(f"- Performing '{chosen_action.name}' from the pool")
            chosen_action.perform(game_state, executor)
            if not chosen_action.is_action_group_modifier:
                self.total_uses += 1

            # Stop if no further actions can be performed and no modifiers are available
            if not self.can_perform_any_action() and not modifiers:
                print("- Reached action limit and no modifiers available")
                break

    def _perform_available_modifiers(self, executor, game_state):
        for modifier in (a for a in self.actions if a.is_action_group_modifier and a.can_perform(executor, game_state)):
            print(f"- Performing available modifier action '{modifier.name}")
            modifier.perform(game_state, executor)

    def _assign_action_group(self):
        for action in self.actions:
            action.action_group = self

    def modify_max_uses(self, amount: int):
        if self.max_total_uses == inf:
            return
        self.max_total_uses += amount
        print(
            f" - ActionGroup '{self.name}' max uses changed to {self.max_total_uses}")

    def reset_action_group(self):
        for action in self.actions:
            action.times_used = 0
        self.total_uses = 0
        self.max_total_uses = self.original_max
        self.cancel_group = False

    def cancel_action_group(self):
        self.cancel_group = True
