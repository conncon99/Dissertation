"""Play a trained checkpoint against uniformly random opponents and report results.

    py -3.11 -m rl.evaluate runs/<run>/checkpoints/latest.pt --games 500
    py -3.11 -m rl.evaluate runs/<run>/checkpoints/latest.pt --policy-factions marquise --greedy

Factions listed in --policy-factions use the checkpoint; the rest pick uniformly random legal
actions. Every evaluation game is recorded (replay with ``python -m rl.replay``).
"""


def main(argv=None):
    # Imports stay inside main(): worker processes re-import this module on Windows
    import argparse
    import json
    import os
    import time

    import numpy as np
    import torch

    from rl.model import FactionActorCritic
    from rl.root_game import ACTION_DIM, FACTION_NAMES, NUM_FACTIONS, OBS_DIM
    from rl.vec_env import AsyncRootVecEnv

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("checkpoint")
    ap.add_argument("--games", type=int, default=200)
    ap.add_argument("--policy-factions", nargs="+", default=FACTION_NAMES, choices=FACTION_NAMES)
    ap.add_argument("--greedy", action="store_true", help="take the most likely action instead of sampling")
    ap.add_argument("--num-envs", type=int, default=4 * (os.cpu_count() or 4))
    ap.add_argument("--seed", type=int, default=12345)
    ap.add_argument("--out", default=None, help="output directory (default: <run>/eval/<timestamp>)")
    args = ap.parse_args(argv)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    ckpt = torch.load(args.checkpoint, map_location=device)
    cfg = ckpt["config"]
    model = FactionActorCritic(OBS_DIM, ACTION_DIM, NUM_FACTIONS, cfg["hidden"]).to(device)
    model.load_state_dict(ckpt["model"])
    model.eval()
    uses_policy = np.array([name in args.policy_factions for name in FACTION_NAMES])

    out = args.out or os.path.join(os.path.dirname(os.path.dirname(args.checkpoint)), "eval",
                                   time.strftime("%Y%m%d_%H%M%S"))
    env = AsyncRootVecEnv(args.num_envs, os.path.join(out, "games"), run_seed=args.seed,
                          turn_limit=cfg["turn_limit"], settle_terminal_rewards=cfg["settle_terminal_rewards"])
    env.set_update(ckpt["update"])
    rng = np.random.default_rng(args.seed)
    sh = env.shared
    results = []
    try:
        while len(results) < args.games:
            ready = env.poll()
            for w in ready[sh.done[ready]].tolist():
                if not sh.ep_error[w]:
                    results.append({"win": sh.ep_win[w].copy(), "vp": sh.ep_vp[w].copy(),
                                    "turns": int(sh.ep_turns[w])})
            agent = sh.agent[ready]
            actions = np.zeros(len(ready), dtype=np.int64)
            by_policy = uses_policy[agent]
            for i in np.flatnonzero(~by_policy):
                actions[i] = rng.choice(np.flatnonzero(sh.mask[ready[i]]))
            if by_policy.any():
                rows = ready[by_policy]
                obs = torch.from_numpy(sh.obs[rows]).to(device)
                mask = torch.from_numpy(sh.mask[rows]).to(device)
                agent_t = torch.from_numpy(agent[by_policy]).to(device)
                with torch.no_grad():
                    if args.greedy:
                        logits, _ = model(obs, agent_t, mask)
                        chosen = logits.argmax(-1)
                    else:
                        chosen, _, _ = model.act(obs, agent_t, mask)
                actions[by_policy] = chosen.cpu().numpy()
            env.send(ready, actions)
    finally:
        env.close()

    results = results[:args.games]
    wins = np.array([r["win"] for r in results])
    vp = np.array([r["vp"] for r in results])
    summary = {
        "checkpoint": args.checkpoint, "update": ckpt["update"], "games": len(results),
        "policy_factions": args.policy_factions, "greedy": args.greedy,
        "no_winner_rate": float((~wins.any(1)).mean()),
        "mean_turns": float(np.mean([r["turns"] for r in results])),
        "factions": {name: {"controller": "policy" if uses_policy[f] else "random",
                            "win_rate": float(wins[:, f].mean()), "mean_vp": float(vp[:, f].mean())}
                     for f, name in enumerate(FACTION_NAMES)},
    }
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))
    print(f"games recorded in {os.path.join(out, 'games')}")


if __name__ == "__main__":
    main()
