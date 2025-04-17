import os
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


def env_creator(config=None):
    return PettingZooEnv(RootEnv())


if __name__ == "__main__":

    # Set up Logging

    log_file = "training/logs/training.log"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, mode='w'),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger(__name__)

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
        .env_runners(num_env_runners=0)
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
        .training(
            lr=2e-5,
            gamma=0.99,
            vf_clip_param=100.0,
            model={
                "custom_model": "TorchActionMaskModel",
                "fcnet_hiddens": [128],
                "fcnet_activation": "relu",
                "custom_model_config": {"no_masking": False},
            }
        )
        .resources(num_gpus=int(os.environ.get("RLLIB_NUM_GPUS", "0")))
        .debugging(log_level='WARN')  # INFO, DEBUG, WARN, ERROR
    )

    algo = config.build()

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
        }
    }

    checkpoint_dir = "training/checkpoints/"
    plot_dir = "training/plots/"
    os.makedirs(checkpoint_dir, exist_ok=True)
    os.makedirs(plot_dir, exist_ok=True)

    iteration_num = 5

    for i in tqdm(range(iteration_num)):
        result = algo.train()

        train_dict['episode'].append(i)
        train_dict['episode_reward'].append(
            result['env_runners']['episode_reward_mean'])
        train_dict['step_num'].append(result['timesteps_total'])
        train_dict['total_episodes'].append(
            result['env_runners']['episodes_this_iter'])
        train_dict['total_steps'].append(result['num_env_steps_sampled'])

        logger.info(f"Episode: {i}")
        for faction in train_dict['faction_losses'].keys():
            policy_loss = result['info']['learner'][faction]['learner_stats']['policy_loss']
            faction_reward = result['env_runners']['policy_reward_mean'][faction]
            faction_steps = result['info']['learner'][faction]['num_agent_steps_trained']

            train_dict['faction_losses'][faction].append(policy_loss)
            train_dict['faction_rewards'][faction].append(faction_reward)
            train_dict['faction_steps'][faction].append(faction_steps)

            average_reward = faction_reward / \
                result['env_runners']['episodes_this_iter']

            reward_per_step = average_reward / faction_steps

            logger.warning(
                f"  {faction.capitalize()} - Steps: {faction_steps:.2f}, Reward: {average_reward:.2f}, per Step Rwd: {reward_per_step:.2f}")

        # Combined plot

        max_loss = max(max(losses)
                       for losses in train_dict['faction_losses'].values())
        min_loss = min(min(losses)
                       for losses in train_dict['faction_losses'].values())

        fig, ax = plt.subplots()
        for faction in train_dict['faction_losses']:
            ax.plot(train_dict['episode'], train_dict['faction_losses']
                    [faction], label=f"{faction.capitalize()}")
        ax.set_title("Policy Loss per Faction")
        ax.set_xlabel("Training Iteration")
        ax.set_ylabel("Policy Loss")
        plt.ylim(min_loss, max_loss)
        plt.legend()
        plt.grid()
        plt.savefig(f'{plot_dir}combined_policy_loss_iteration.png')
        plt.close()

        # Plotting the policy loss for each faction separately with shared scale
        fig, ax = plt.subplots()
        for faction, loss_values in train_dict['faction_losses'].items():
            fig, ax = plt.subplots()
            ax.plot(loss_values, label=f"{faction.capitalize()} Policy Loss")
            ax.set_title(f"{faction.capitalize()} Policy Loss during Training")
            ax.set_xlabel("Training Iteration")
            ax.set_ylabel("Policy Loss")
            plt.ylim(min_loss, max_loss)
            plt.legend()
            plt.grid()
            plt.savefig(f'{plot_dir}{faction}_policy_loss_iteration.png')
            plt.close()

        # Save checkpoint every 10 iterations
        if (i + 1) % 10 == 0:
            algo.save(checkpoint_dir)
            logger.info(
                f"Checkpoint saved at iteration {i + 1}: {checkpoint_dir}")
