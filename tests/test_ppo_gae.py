import numpy as np
import pytest

torch = pytest.importorskip("torch")

from rl.ppo import Rollout


def test_linked_gae_matches_per_chain_gae():
    rng = np.random.default_rng(0)
    gamma, lam = 0.99, 0.9
    ro = Rollout.__new__(Rollout)  # skip pinned buffers
    n, envs = 200, 3
    ro.ptr = n
    ro.value = rng.normal(size=n).astype(np.float32)
    ro.reward = rng.normal(size=n)
    ro.done = np.zeros(n, bool)
    ro.next_idx = np.full(n, -1)
    ro.boot_value = np.zeros(n, np.float32)

    # Random interleaving of (env, faction) chains, some ending in game over
    chains = {}
    order = [(int(rng.integers(envs)), int(rng.integers(4))) for _ in range(n)]
    for t, key in enumerate(order):
        chains.setdefault(key, []).append(t)
    for key, ts in chains.items():
        for a, b in zip(ts[:-1], ts[1:]):
            ro.next_idx[a] = b
        if rng.random() < 0.5:
            ro.done[ts[-1]] = True
        else:
            ro.boot_value[ts[-1]] = rng.normal()

    adv, ret = ro.advantages(gamma, lam)

    for ts in chains.values():
        expected, running = {}, 0.0
        for i in reversed(range(len(ts))):
            t = ts[i]
            if i == len(ts) - 1:
                nv = 0.0 if ro.done[t] else ro.boot_value[t]
                running = 0.0
            else:
                nv = ro.value[ts[i + 1]]
            delta = ro.reward[t] + gamma * nv - ro.value[t]
            running = delta + gamma * lam * running
            expected[t] = running
        for t, v in expected.items():
            assert adv[t] == pytest.approx(v, rel=1e-5, abs=1e-6)
    np.testing.assert_allclose(ret, adv + ro.value, rtol=1e-6)
