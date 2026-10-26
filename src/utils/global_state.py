"""Restores the simulator's process-wide state so every game starts as if in a fresh process.

The engine keeps some state outside the GameManager:
  * module-level card singletons (``src.cards.cards``, quests, ...) whose ``owner``,
    ``action`` and ``game_state`` attributes are mutated during play,
  * module-level lists holding those cards (e.g. ``DOMINANCE_CARDS``),
  * class-level registries (``PieceWithID``, ``ActionGroupRegistry``),
  * numpy's global RNG.

Without resetting these, game N depends on how game N-1 ended, which makes a game
impossible to recreate from its seed alone.
"""
from __future__ import annotations
import copy
import enum
import sys
import types

import numpy as np

from src.actions.action_group_registry import ActionGroupRegistry
from src.pieces.piece_with_id import PieceWithID

_SKIP_TYPES = (types.ModuleType, type, types.FunctionType, types.BuiltinFunctionType,
               enum.Enum, int, float, str, bool, bytes, type(None))

_snapshot = None


def _is_src_object(value) -> bool:
    return type(value).__module__.startswith("src.")


def _collect_globals():
    """Find every distinct module-level mutable object in the ``src`` package."""
    objects = {}
    containers = {}
    for name, module in list(sys.modules.items()):
        if not (name == "src" or name.startswith("src.")) or module is None:
            continue
        for attr, value in vars(module).items():
            if attr.startswith("__") or isinstance(value, _SKIP_TYPES):
                continue
            if _is_src_object(value):
                objects[id(value)] = value
            elif isinstance(value, (list, dict)):
                containers[id(value)] = value
    return list(objects.values()), list(containers.values())


def take_snapshot():
    """Record the pristine state of all module-level objects. Call once after imports."""
    global _snapshot
    objects, containers = _collect_globals()
    # Keep references between singletons as references (not copies) when restoring
    memo = {id(o): o for o in objects}
    memo.update({id(c): c for c in containers})
    _snapshot = {
        "objects": [(o, copy.deepcopy(o.__dict__, dict(memo))) for o in objects],
        "containers": [(c, copy.copy(c)) for c in containers],
        "memo": memo,
    }


def reset_global_state(seed: int | None = None):
    """Restore all module-level game objects, clear ID registries and reseed numpy."""
    if _snapshot is None:
        take_snapshot()
    memo = _snapshot["memo"]
    for obj, state in _snapshot["objects"]:
        obj.__dict__.clear()
        obj.__dict__.update(copy.deepcopy(state, dict(memo)))
    for container, state in _snapshot["containers"]:
        container.clear()
        if isinstance(container, list):
            container.extend(state)
        else:
            container.update(state)
    PieceWithID.reset_ids()
    ActionGroupRegistry.reset()
    if seed is not None:
        np.random.seed(seed)
