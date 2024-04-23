import ray
from ray.rllib.algorithms import PPOConfig, PPO
from ray.rllib.policy.policy import PolicySpec
from ray.rllib.models import ModelCatalog
from agent import TorchActionMaskModel
from uno import UnoEnv
import ray.tune as tune

# Register the environment and model
tune.register_env("uno_multiagent", lambda config: UnoEnv(config))
ModelCatalog.register_custom_model("custom_action_mask_model", TorchActionMaskModel)

# Define policy mapping function
def mapping_fn(agent_id):
    return "alpha" if agent_id == 1 else "bravo"

# Set up the configuration for interfacing
config = (
    PPOConfig()
    .framework("torch")
    .environment("uno_multiagent", disable_env_checking=True)
    .multi_agent(
        policies={
            "alpha": PolicySpec(config={"gamma": 0.85, "model": {"custom_model": "custom_action_mask_model"}}),
            "bravo": PolicySpec(config={"gamma": 0.95, "model": {"custom_model": "custom_action_mask_model"}}),
        },
        policy_mapping_fn=mapping_fn
    )
    .rollouts(num_rollout_workers=0) 
)

# Load the trained algorithm
algo = PPO(config)
algo.restore("./models/KartenmasterV2.0/")

# Initialize the environment and reset it
env = UnoEnv(config={"n_players": 2})  # Ensure this matches training config
obs = env.reset()[0]
done = False

while not done:
    print("Board:")
    print("Actual Player:", env.actual_player)
    env.observation_to_human(obs[env.actual_player]["real_obs"])
    if env.actual_player == 1:
        action = algo.compute_single_action(obs[env.actual_player], policy_id="alpha")
        print("Agent Action", action)
    else:
        action = int(input("Enter your action: "))
    obs, reward, terminated, _, info = env.step({env.actual_player: action})
    done = terminated["__all__"]
    print(f"Action: {action}, Reward: {reward}, Info: {info}")
