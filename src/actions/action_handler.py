"""Turns can be broken up into 3 stages:
    1. Phases - Birdsong, Daylight, Evening
    2. ActionGroup - the list of actions that can be taken at a given moment
    3. Action - the atomic action that is undertaken, e.g. Battle, Move

"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional, TYPE_CHECKING, Generator, Any
from math import inf
from src.utils.game_state import GameState
from src.controllers.messages.game_messages import ActionChoiceMessage
from src.actions.action_group_registry import ActionGroupRegistry
import types
import logging
if TYPE_CHECKING:
    from src.factions.faction import Faction
    from src.controllers.messages.game_messages import GameMessage


class Action(ABC):
    """
    :param name: A unique name for the action (e.g., 'Move', 'Battle').
    :param max_uses: Maximum times this action can be used. None -> unlimited.
    :param is_ordered: If True, this action must be done in a specific order
                        (within an ordered group).
    """

    def __init__(self, name: str, max_uses: Optional[int] = None, is_action_group_modifier: bool = False, group_spanning: bool = False) -> None:
        self.name = name
        self.logger = logging.getLogger()
        self.max_uses = max_uses if max_uses is not None else inf
        self.times_used = 0
        self.is_action_group_modifier = is_action_group_modifier
        # Whether the action exists across multiple groups
        self.group_spanning = group_spanning
        self.id = -1
        self.action_group: ActionGroup = None
        self.action_complete = False

    def __repr__(self):
        return self.name

    @abstractmethod
    def can_perform(self, executor: Faction, game_state: Optional[GameState] = None) -> bool:
        if self.group_spanning and self in executor.used_spanning_actions.keys():
            self.times_used = executor.used_spanning_actions[self]
        return self.times_used < self.max_uses

    @abstractmethod
    def perform(self, game_state: GameState, executor: Faction) -> Generator[GameMessage, Any, None]:
        self.logger.info(f" - {self.name} action completed\n")
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
        self.logger = logging.getLogger()
        self.id = id
        self.ordered = ordered
        self.actions = actions if actions is not None else []
        self.was_max_assigned = max_total_uses != None
        self.max_total_uses = len(
            self.actions) if self.ordered else max_total_uses if max_total_uses is not None else inf
        self.original_max = self.max_total_uses
        self.total_uses = 0  # Tracks how many actions have been performed in this group so far
        self.cancel_group = False
        self.started = False
        self._current_action_gen = None
        self._chosen_action = None
        self.action_iter = None
        self._remaining_actions = []

        # Whether this action group can be aborted before all actions are played
        self.can_abort = can_abort
        self.id = self._assign_unique_id()
        self.logger.debug(f"ID: {self.id}: {self.name}")

    def _assign_unique_id(self):
        """Generate a globally unique integer ID for this ActionGroup."""
        registry = ActionGroupRegistry()  # Singleton instance
        return registry.get_unique_id()

    def can_perform_any_action(self):
        return self.total_uses < self.max_total_uses

    def step_action_group(self, executor, game_state) -> Generator[GameMessage, Any, None]:
        """Runs one step of this ActionGroup."""
        if not self.started:
            self.started = True
            self._assign_action_group()
            # self._perform_available_modifiers(executor, game_state)
            self.logger.info(
                f"\n[GROUP] Starting '{self.name}' (ordered={self.ordered})")

        if self.ordered:
            self._remaining_actions = self.actions[:]
            if not self.was_max_assigned:
                self.max_total_uses = len(self._remaining_actions)
        else:
            if not self.was_max_assigned:
                self.max_total_uses = inf

        if self.ordered:
            yield from self._run_ordered_group(executor, game_state)
        else:
            yield from self._run_unordered_group(executor, game_state)

    def _run_unordered_group(self, executor, game_state) -> Generator[GameMessage, Any, None]:
        """
        Unordered group: actions may be performed in any order.
        The controller may choose to finish the group by returning a None action.
        """

        while not self.cancel_group:

            # Dynamically compute the available actions.
            primary_actions = [action for action in self.actions if action.can_perform(
                executor, game_state) and not action.is_action_group_modifier]
            modifier_actions = [action for action in self.actions if action.can_perform(
                executor, game_state) and action.is_action_group_modifier]

            if self.can_abort:
                if primary_actions:
                    primary_actions.append(None)
                if modifier_actions:
                    modifier_actions.append(None)

            self.logger.debug(
                f"{executor} modifier_actions: {modifier_actions}")
            self.logger.debug(f"{executor} hand: {executor.hand}")

            if not self.can_perform_any_action():
                if modifier_actions:
                    self.logger.debug(
                        "- Max actions hit, offering modifier actions")
                    if len(modifier_actions) == 1:
                        self._chosen_action = modifier_actions[0]
                    else:
                        response = yield ActionChoiceMessage(game_state, self, modifier_actions)
                        self._chosen_action = response.chosen_action
                else:
                    self.logger.debug(
                        "- Max actions hit, no modifiers available. Exiting.")
                    break
            else:
                if primary_actions:
                    if len(primary_actions) == 1:
                        self._chosen_action = primary_actions[0]
                    else:
                        self.logger.debug(
                            "- Waiting for Primary Action Choice...")
                        response = yield ActionChoiceMessage(game_state, self, primary_actions)
                        self._chosen_action = response.chosen_action
                elif modifier_actions:
                    if len(modifier_actions) == 1:
                        self._chosen_action = modifier_actions[0]
                    else:
                        self.logger.debug(
                            "- Waiting for Modifier Action Choice...")
                        response = yield ActionChoiceMessage(game_state, self, modifier_actions)
                        self._chosen_action = response.chosen_action
                else:
                    break

            # If the controller returns None, interpret that as finishing the group.
            if self._chosen_action is None:
                self.logger.debug(
                    f" - Unordered ActionGroup '{self.name}' aborted by controller.")
                break

            self.logger.info(
                f" - Performing action: '{self._chosen_action.name}'")
            # Delegate to the chosen action's generator.
            yield from self._chosen_action.perform(game_state, executor)
            if not self._chosen_action.is_action_group_modifier:
                self.total_uses += 1

        self.logger.info(f"[GROUP] Finished group '{self.name}'")
        self.reset_action_group()

    def _run_ordered_group(self, executor, game_state) -> Generator[GameMessage, Any, None]:
        while not self.cancel_group and self.can_perform_any_action():
            available_actions = [
                a for a in self._remaining_actions if a.can_perform(executor, game_state)]
            if not available_actions:
                self.logger.debug("- No available actions left to perform.")
                break

            # Choose an action.
            if len(available_actions) == 1:
                self._chosen_action = available_actions[0]
                self.logger.debug(
                    f"- Automatically selected '{self._chosen_action.name}'")
            else:
                self.logger.debug("- Waiting for action choice...")
                message = ActionChoiceMessage(
                    game_state, self, available_actions)
                response = yield message
                self._chosen_action = response.chosen_action
                if self._chosen_action is None:
                    self.logger.info(
                        f" - ActionGroup '{self.name}' was aborted by controller.")
                    self.cancel_group = True
                    break

            self.logger.info(
                f" - Performing action: '{self._chosen_action.name}'")

            # Delegate the entire action generator with yield from.
            yield from self._delegate_action(self._chosen_action, game_state, executor)
            self.logger.debug(f"Remaining Actions: {self._remaining_actions}")
            self.total_uses += 1
            # Remove Action
            self.logger.debug(f"Attempting to remove {self._chosen_action}")
            if self._chosen_action in self._remaining_actions:
                self._remaining_actions.remove(self._chosen_action)
            else:
                self.logger.debug(
                    "Action not found, getting attempting to find alternate")
                self._remaining_actions.remove(
                    self._get_alternate_action(self._chosen_action))

            self._chosen_action = None

        self.logger.info(f"[GROUP] Finished '{self.name}'")
        self.reset_action_group()

    def _delegate_action(self, action, game_state, executor) -> Generator[GameMessage, Any, None]:
        # Delegate all send() calls directly into the action's perform generator.
        yield from action.perform(game_state, executor)

    def _perform_available_modifiers(self, executor, game_state):
        for modifier in (a for a in self.actions if a.is_action_group_modifier and a.can_perform(executor, game_state)):
            self.logger.info(
                f"- Performing available modifier action '{modifier.name}")
            modifier.perform(game_state, executor)

    def _assign_action_group(self):
        for action in self.actions:
            action.action_group = self

    def modify_max_uses(self, amount: int):
        if self.max_total_uses == inf:
            return
        self.max_total_uses += amount
        self.logger.info(
            f" - ActionGroup '{self.name}' max uses changed to {self.max_total_uses}")

    def _get_alternate_action(self, chosen_action: Action):
        viable_actions = [
            action for action in self._remaining_actions if action.id == chosen_action.id]
        return viable_actions[0]

    def reset_action_group(self):
        for action in self.actions:
            action.times_used = 0
        self.total_uses = 0
        self.max_total_uses = self.original_max
        self.cancel_group = False
        self._remaining_actions = []
        self.started = False
        self._chosen_action = None
        self._current_action_gen = None

    def cancel_action_group(self):
        self.cancel_group = True
