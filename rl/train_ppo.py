"""Train Root factions with multi-agent PPO self-play.

    py -3.11 -m rl.train_ppo --run-name first_try
    py -3.11 -m rl.train_ppo --resume runs/first_try/checkpoints/latest.pt
    py -3.11 -m rl.train_ppo --help

Kept free of heavy imports: on Windows every worker process re-imports this module, and
the workers must not load torch or TensorBoard.
"""


def main(argv=None):
    from rl.ppo import Trainer, parse_args
    Trainer(parse_args(argv)).train()


if __name__ == "__main__":
    main()
