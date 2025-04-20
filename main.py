import os
import matplotlib
import ray
from ray.rllib.algorithms.ppo import PPOConfig
from ray.tune.registry import register_env
from ray.rllib.env import PettingZooEnv
from src.pettingzoo_env import RootEnv
from ray.rllib.models import ModelCatalog
from src.controllers.nn_controllers.masked_policy_model import TorchActionMaskModel
import matplotlib.pyplot as plt
from tqdm import tqdm
import logging
import torch
from pathlib import Path


LOG_DIR = Path("training/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)


def env_creator(config=None):
    return PettingZooEnv(RootEnv())


faction_color_map = {
    'marquise': 'orange',
    'eyrie': 'blue',
    'woodland_alliance': 'green',
    'vagabond': 'gray'
}


def new_file_handler(iter_idx: int) -> logging.FileHandler:
    fname = LOG_DIR / f"run-{iter_idx:05d}.log"
    fh = logging.FileHandler(fname, mode="w", encoding="utf‑8")
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh.setFormatter(fmt)
    fh.setLevel(logging.DEBUG)
    return fh


def plot_metric(data_dict, episodes, title, ylabel, filename, plot_dir, colors=None):
    fig, ax = plt.subplots()
    for i, (label, values) in enumerate(data_dict.items()):
        color = colors[i] if colors and i < len(colors) else None
        ax.plot(episodes, values, label=label.capitalize(), color=color)

    ax.set_title(title)
    ax.set_xlabel("Training Iteration")
    ax.set_ylabel(ylabel)
    ax.legend()
    ax.grid()
    plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, filename))
    plt.close()


if __name__ == "__main__":

    print("CUDA Available:", torch.cuda.is_available())
    print("GPU Device:", torch.cuda.get_device_name(
        0) if torch.cuda.is_available() else "None")

    # Set up Logging

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    # ch = logging.StreamHandler()
    # ch.setLevel(logging.WARNING)
    # ch.setFormatter(logging.Formatter(
    #     "%(asctime)s [%(levelname)s] %(message)s"))
    # logger.addHandler(ch)

    current_fh = new_file_handler(0)
    logger.addHandler(current_fh)

    matplotlib.use("Agg")

    # Initialize Ray
    ray.init()

    # Environment and Model setup
    env_name = "root_v0"
    register_env(env_name, lambda _: PettingZooEnv(RootEnv()))
    ModelCatalog.register_custom_model(
        "TorchActionMaskModel", TorchActionMaskModel)

    test_env = env_creator()
    obs_space = test_env.observation_space["marquise"]
    act_space = test_env.action_space["marquise"]

    # Trainer setup
    config = (
        PPOConfig()
        .environment(env=env_name, disable_env_checking=True)
        .api_stack(enable_rl_module_and_learner=False,
                   enable_env_runner_and_connector_v2=False)
        .env_runners(num_env_runners=8)
        .framework(framework="torch")
        .checkpointing(export_native_model_files=True)
        .multi_agent(
            policies={
                "marquise": (None, obs_space, act_space, {}),
                "eyrie": (None, obs_space, act_space, {}),
                "woodland_alliance": (None, obs_space, act_space, {}),
                "vagabond": (None, obs_space, act_space, {}),
            },
            policy_mapping_fn=lambda agent_id, *args, **kw: agent_id
        )
        .resources(num_gpus=1)  # int(os.environ.get("RLLIB_NUM_GPUS", "0"))
        .debugging(log_level='WARN')  # INFO, DEBUG, WARN, ERROR
        .training(
            lr=2e-5,
            gamma=0.99,
            vf_clip_param=100.0,
            model={
                "custom_model": "TorchActionMaskModel",
                "custom_model_config": {
                    "no_masking": False,
                    "lstm_hidden_size": 1024,
                    "fc_layer_sizes": [1024, 1024, 512]
                },
            }
        )
    )

    algo = config.build_algo()

    train_dict = {
        'episode': [],
        'episode_reward': [],
        'step_num': [],
        'total_episodes': [],
        'total_steps': [],
        'faction_losses': {
            'marquise': [],
            'eyrie': [],
            'woodland_alliance': [],
            'vagabond': []
        },
        'faction_rewards': {
            'marquise': [],
            'eyrie': [],
            'woodland_alliance': [],
            'vagabond': []
        },
        'faction_steps': {
            'marquise': [],
            'eyrie': [],
            'woodland_alliance': [],
            'vagabond': []
        },
        'faction_vf_losses': {
            'marquise': [],
            'eyrie': [],
            'woodland_alliance': [],
            'vagabond': []
        }
    }

    checkpoint_dir = "training/checkpoints/"
    plot_dir = "training/plots/"
    os.makedirs(checkpoint_dir, exist_ok=True)
    os.makedirs(plot_dir, exist_ok=True)

    iteration_num = 10_000

    for i in tqdm(range(iteration_num)):
        result = algo.train()

        train_dict['episode'].append(i)
        train_dict['episode_reward'].append(
            result['env_runners']['episode_reward_mean'])
        train_dict['step_num'].append(result['timesteps_total'])
        train_dict['total_episodes'].append(
            result['env_runners']['episodes_this_iter'])
        train_dict['total_steps'].append(result['num_env_steps_sampled'])

        logger.warning(f"Episode: {i}")
        for faction in train_dict['faction_losses'].keys():
            learner_info = result["info"]["learner"].get(faction)

            if learner_info:
                policy_loss = learner_info["learner_stats"]["policy_loss"]
                vf_loss = learner_info["learner_stats"]["vf_loss"]
            else:  # Take average of last 5 if they exist if no data found
                recent_policy = train_dict["faction_losses"][faction][-5:]
                recent_vf = train_dict["faction_vf_losses"][faction][-5:]

                policy_loss = (sum(recent_policy) /
                               len(recent_policy)) if recent_policy else 0.0
                vf_loss = (sum(recent_vf) / len(recent_vf)
                           ) if recent_vf else 0.0

                logger.warning(
                    f"No learner stats for {faction} in iter {i}; "
                    f"using averaged fallback (policy={policy_loss:.4f}, vf={vf_loss:.4f})"
                )

            # bookkeeping exactly as before
            train_dict['faction_losses'][faction].append(policy_loss)
            train_dict['faction_vf_losses'][faction].append(vf_loss)

            faction_reward = result['env_runners']['policy_reward_mean'].get(
                faction, 0.0)
            faction_steps = learner_info['num_agent_steps_trained'] if learner_info else 0
            train_dict['faction_rewards'][faction].append(faction_reward)
            train_dict['faction_steps'][faction].append(faction_steps)

            average_reward = faction_reward / \
                max(result['env_runners']['episodes_this_iter'], 1)
            reward_per_step = average_reward / max(faction_steps, 1)

            logger.debug(
                f"  {faction.capitalize()} - Steps: {faction_steps:.2f}, "
                f"Reward: {average_reward:.2f}, per‑step Rwd: {reward_per_step:.4f}"
            )

        colors = [faction_color_map[faction]
                  for faction in train_dict['faction_rewards']]

        if (i + 1) % 100 == 0 and i != 0:
            logger.removeHandler(current_fh)
            current_fh.close()
            current_fh = new_file_handler(i)
            logger.addHandler(current_fh)

        # Save checkpoint every 10 iterations
        if (i + 1) % 10 == 0:

            algo.save(checkpoint_dir)
            logger.warning(
                f"Checkpoint saved at iteration {i + 1}: {checkpoint_dir}")

            plot_metric(
                data_dict=train_dict['faction_rewards'],
                episodes=train_dict['episode'],
                title="Combined Episode Rewards",
                ylabel="Episode Reward",
                filename="combined_episode_reward_per_iteration.png",
                plot_dir=plot_dir,
                colors=colors
            )

            plot_metric(
                data_dict=train_dict['faction_vf_losses'],
                episodes=train_dict['episode'],
                title="Combined Value Function Losses",
                ylabel="VF Loss",
                filename="combined_vf_loss_per_iteration.png",
                plot_dir=plot_dir,
                colors=colors
            )

            plot_metric(
                data_dict=train_dict['faction_losses'],
                episodes=train_dict['episode'],
                title="Combined Policy Function Losses",
                ylabel="Policy Loss",
                filename="combined_policy_loss_per_iteration.png",
                plot_dir=plot_dir,
                colors=colors
            )

            for faction in train_dict['faction_rewards']:
                plot_metric(
                    data_dict={
                        faction: train_dict['faction_rewards'][faction]},
                    episodes=train_dict['episode'],
                    title=f"{faction.capitalize()} Episode Reward per Iteration",
                    ylabel="Episode Reward",
                    filename=f"{faction}_episode_reward_per_iteration.png",
                    plot_dir=plot_dir,
                    colors=[faction_color_map[faction]]
                )

            for faction in train_dict['faction_vf_losses']:
                plot_metric(
                    data_dict={
                        faction: train_dict['faction_vf_losses'][faction]},
                    episodes=train_dict['episode'],
                    title=f"{faction.capitalize()} VF Loss per Iteration",
                    ylabel="VF Loss",
                    filename=f"{faction}_vf_loss_per_iteration.png",
                    plot_dir=plot_dir,
                    colors=[faction_color_map[faction]]
                )

            for faction in train_dict['faction_vf_losses']:
                plot_metric(
                    data_dict={faction: train_dict['faction_losses'][faction]},
                    episodes=train_dict['episode'],
                    title=f"{faction.capitalize()} Policy Loss per Iteration",
                    ylabel="Policy Loss",
                    filename=f"{faction}_policy_loss_per_iteration.png",
                    plot_dir=plot_dir,
                    colors=[faction_color_map[faction]]
                )
