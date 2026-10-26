"""RootEnv (the PettingZoo AEC env used by main.py) must hand every decision to the right agent."""
import numpy as np
import pytest

from rl.root_game import RootGame, FACTION_NAMES
from src.pettingzoo_env import RootEnv


def _play_env(seed, action_seed):
    rng = np.random.default_rng(action_seed)
    env = RootEnv()
    env.reset(seed=seed)
    actions, actors = [], []
    totals = {agent: 0.0 for agent in env.possible_agents}
    while env.agents:
        agent = env.agent_selection
        gm = env.gm
        # The selected agent is the faction the game is waiting on, and it has a decision
        assert gm.current_message is not None
        assert env._faction_to_agent(gm.game_state.active_player) == agent
        mask = env.observe(agent)["action_mask"]
        legal = np.flatnonzero(mask)
        assert len(legal) > 0
        # The mask handed to the agent is the one for the decision the game is waiting on
        assert np.array_equal(mask > 0, np.array(gm.masker.create_mask(gm.current_message)) > 0)
        for other in env.possible_agents:
            if other != agent:
                assert not env.observe(other)["action_mask"].any()
        action = int(rng.choice(legal))
        actions.append(action)
        actors.append(agent)
        env.step(action)
        for a, r in env.rewards.items():
            totals[a] += r
    assert env.gm.done
    assert all(env.terminations.values()) or all(env.truncations.values())
    return env, actions, actors, totals


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_env_selects_acting_faction_and_matches_root_game(seed):
    env, actions, actors, totals = _play_env(seed, action_seed=seed + 100)

    # The same seed and actions must give the same game, rewards included, in RootGame
    game = RootGame()
    game.reset(seed)
    for action, actor in zip(actions, actors):
        assert FACTION_NAMES[game.current_agent] == actor
        game.step(action)
    assert game.done
    assert game.result()["vp"] == [f.victory_points for f in
                                   sorted(env.gm.settings.faction_list, key=lambda f: f.faction_id)]
    assert np.allclose(game.returns, [totals[name] for name in FACTION_NAMES])


def test_env_works_with_tianshou_wrapper():
    from tianshou.env import PettingZooEnv
    env = PettingZooEnv(RootEnv())
    obs, _ = env.reset(seed=5)
    rng = np.random.default_rng(0)
    for _ in range(200):
        legal = np.flatnonzero(obs["mask"])
        assert obs["agent_id"] == env.env.agent_selection
        obs, rewards, term, trunc, _ = env.step(int(rng.choice(legal)))
        assert len(rewards) == 4
        if term or trunc:
            break
